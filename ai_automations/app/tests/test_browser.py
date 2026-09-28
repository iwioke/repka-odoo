import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import create_server


class DevTools:
    def __init__(self, url):
        target = urlsplit(url)
        self.socket = socket.create_connection((target.hostname, target.port), timeout=5)
        self.socket.settimeout(10)
        key = base64.b64encode(os.urandom(16)).decode()
        handshake = (f"GET {target.path} HTTP/1.1\r\nHost: {target.netloc}\r\nUpgrade: websocket\r\n"
                     f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.socket.sendall(handshake.encode())
        response = b""
        while b"\r\n\r\n" not in response:
            response += self.socket.recv(4096)
        if not response.startswith(b"HTTP/1.1 101 "):
            raise RuntimeError(response.decode(errors="replace"))
        self.remaining = response.split(b"\r\n\r\n", 1)[1]
        self.identifier = 0

    def read(self, size):
        while len(self.remaining) < size:
            self.remaining += self.socket.recv(65536)
        result, self.remaining = self.remaining[:size], self.remaining[size:]
        return result

    def message(self):
        header = self.read(2)
        length = header[1] & 127
        if length == 126:
            length = int.from_bytes(self.read(2), "big")
        elif length == 127:
            length = int.from_bytes(self.read(8), "big")
        if header[1] & 128:
            mask = self.read(4)
            raw = self.read(length)
            data = bytes(value ^ mask[i % 4] for i, value in enumerate(raw))
        else:
            data = self.read(length)
        return json.loads(data)

    def evaluate(self, expression):
        self.identifier += 1
        payload = json.dumps({"id": self.identifier, "method": "Runtime.evaluate", "params": {
            "expression": expression, "returnByValue": True, "awaitPromise": True}}).encode()
        mask = os.urandom(4)
        size = len(payload)
        length = bytes([size]) if size < 126 else b"\x7e" + size.to_bytes(2, "big") if size < 65536 else b"\x7f" + size.to_bytes(8, "big")
        self.socket.sendall(b"\x81" + bytes([0x80 | length[0]]) + length[1:] + mask + bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload)))
        while True:
            message = self.message()
            if message.get("id") == self.identifier:
                if "exceptionDetails" in message.get("result", {}):
                    raise RuntimeError(message["result"]["exceptionDetails"])
                return message["result"]["result"].get("value")

    def close(self):
        self.socket.close()


class BrowserFlowTests(unittest.TestCase):
    def test_full_browser_flow(self):
        chrome = shutil.which("google-chrome") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if not Path(chrome).is_file():
            self.skipTest("Chrome is unavailable")
        server = create_server(0)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory(prefix="repka-ui-") as profile:
                process = subprocess.Popen([chrome, "--headless=new", "--disable-gpu", "--no-first-run",
                                            "--remote-debugging-port=0", f"--user-data-dir={profile}", origin],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                try:
                    port_file = Path(profile) / "DevToolsActivePort"
                    for _ in range(100):
                        if port_file.exists():
                            break
                        time.sleep(.1)
                    self.assertTrue(port_file.exists(), "Chrome did not start")
                    port = port_file.read_text().splitlines()[0]
                    targets = json.load(urlopen(f"http://127.0.0.1:{port}/json"))
                    page = next(target for target in targets if target["type"] == "page")
                    client = DevTools(page["webSocketDebuggerUrl"])
                    try:
                        for _ in range(100):
                            if client.evaluate("document.querySelectorAll('.card').length") == 23:
                                break
                            time.sleep(.1)
                        self.assertEqual(client.evaluate("document.querySelectorAll('.card').length"), 23)
                        self.assertEqual(client.evaluate("document.querySelectorAll('.card .run-button:disabled').length"), 19)
                        client.evaluate("document.querySelector('#search').value='margin'; document.querySelector('#search').dispatchEvent(new Event('input',{bubbles:true}))")
                        self.assertEqual(client.evaluate("document.querySelectorAll('.card').length"), 1)
                        client.evaluate("document.querySelector('.card .link-button').click()")
                        self.assertIn('Freight Margin Watch', client.evaluate("document.querySelector('.modal h2').textContent"))
                        client.evaluate("document.querySelector('.modal .primary').click()")
                        self.assertIn('DEMO MODE', client.evaluate("document.querySelector('.modal .notice').textContent"))
                        client.evaluate("document.querySelector('.modal .primary').click()")
                        for _ in range(100):
                            if client.evaluate("document.querySelector('.modal pre')?.textContent || ''"):
                                break
                            time.sleep(.1)
                        result = json.loads(client.evaluate("document.querySelector('.modal pre')?.textContent || '{}'"))
                        self.assertEqual(result["scenario"], "margin_watch")
                        self.assertEqual(result["result"]["review_count"], 1)
                        client.evaluate("document.querySelector('.modal .secondary').click(); document.querySelector('#nav-history').click()")
                        self.assertIn('Freight Margin Watch', client.evaluate("document.querySelector('#history-content').textContent"))
                        client.evaluate("document.querySelector('#nav-automations').click(); document.querySelector('#search').value=''; document.querySelector('#search').dispatchEvent(new Event('input',{bubbles:true}))")
                        client.evaluate("document.querySelector('.card .run-button').click(); document.querySelector('.modal .primary').click()")
                        for _ in range(100):
                            if client.evaluate("document.querySelector('.modal pre')?.textContent || ''"):
                                break
                            time.sleep(.1)
                        self.assertEqual(json.loads(client.evaluate("document.querySelector('.modal pre').textContent"))["scenario"], "customer_360")
                        for slug, title in (("document_readiness", "Document Readiness"), ("executive_brief", "Executive Brief")):
                            client.evaluate("document.querySelector('.modal .secondary').click()")
                            client.evaluate(f"[...document.querySelectorAll('.card')].find(card=>card.querySelector('h3').textContent==={json.dumps(title)}).querySelector('.run-button').click()")
                            client.evaluate("document.querySelector('.modal .primary').click()")
                            for _ in range(100):
                                if client.evaluate("document.querySelector('.modal pre')?.textContent || ''"):
                                    break
                                time.sleep(.1)
                            self.assertEqual(json.loads(client.evaluate("document.querySelector('.modal pre').textContent"))["scenario"], slug)
                        client.evaluate("document.querySelector('.modal .secondary').click()")
                        client.evaluate("document.querySelector('#search').value='lead'; document.querySelector('#search').dispatchEvent(new Event('input',{bubbles:true}))")
                        self.assertEqual(client.evaluate("document.querySelectorAll('.card').length"), 1)
                        self.assertTrue(client.evaluate("document.querySelector('.card .run-button').disabled"))
                        client.evaluate("document.querySelector('#search').value=''; document.querySelector('#search').dispatchEvent(new Event('input',{bubbles:true}))")
                        client.evaluate("[...document.querySelectorAll('.filter')].find(x=>x.textContent==='Documents / Logistics').click()")
                        self.assertEqual(client.evaluate("document.querySelectorAll('.card').length"), 1)
                        client.evaluate("document.querySelector('.card .run-button').click()")
                        client.evaluate("document.querySelector('.input-label input').click(); document.querySelector('textarea').value='{}'; document.querySelector('.modal .primary').click()")
                        for _ in range(100):
                            if client.evaluate("document.querySelector('.modal .notice.error')?.textContent || ''"):
                                break
                            time.sleep(.1)
                        self.assertIn('Automation failed', client.evaluate("document.querySelector('.modal .notice.error').textContent"))
                        client.evaluate("document.querySelector('.modal .primary').click()")
                        self.assertEqual(client.evaluate("document.querySelector('textarea').value"), '{}')
                        client.evaluate("document.querySelector('.modal .secondary').click(); document.querySelector('#nav-history').click()")
                        self.assertIn('Failed', client.evaluate("document.querySelector('#history-content').textContent"))
                    finally:
                        client.close()
                finally:
                    process.terminate()
                    process.wait(timeout=10)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
