import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


MAX_BODY_BYTES = 10 * 1024 * 1024


def build_result(payload):
    document = payload.get("document", {})
    order = payload.get("order", {})
    filename = (document.get("filename") or "").lower()
    document_type = "unknown"
    if "cmr" in filename:
        document_type = "cmr"
    elif "request" in filename or "заяв" in filename:
        document_type = "transport_request"
    elif "invoice" in filename or "счет" in filename or "счёт" in filename:
        document_type = "invoice"
    elif "act" in filename or "акт" in filename:
        document_type = "act"
    fields = [
        {"name": "document_number", "value": document.get("number"), "confidence": 0.99},
        {"name": "carrier", "value": order.get("carrier"), "confidence": 0.99},
    ]
    checks = []
    state = "completed"
    summary = "Документ соответствует детерминированному демонстрационному профилю."
    if document_type == "cmr":
        expected_weight = order.get("cargo", {}).get("weight_kg") or 0
        actual_weight = 9250 if "error" in filename else expected_weight
        fields.extend([
            {"name": "route", "value": order.get("route", []), "confidence": 0.98},
            {"name": "weight_kg", "value": actual_weight, "confidence": 0.98},
        ])
        if actual_weight != expected_weight:
            checks.append({
                "code": "cargo_weight_mismatch",
                "severity": "warning",
                "document_value": actual_weight,
                "crm_value": expected_weight,
                "message": "Вес в CMR отличается от веса в заказе CRM.",
            })
        if "error" in filename:
            checks.append({
                "code": "consignee_stamp_missing",
                "severity": "critical",
                "message": "В CMR отсутствует подпись или печать получателя.",
            })
            state = "blocked"
            summary = "В CMR обнаружено расхождение веса и нет подтверждения получателя."
    if document_type == "unknown":
        state = "attention"
        summary = "Тип документа не распознан детерминированным демонстрационным профилем."
    return {
        "request_id": payload.get("request_id"),
        "status": state,
        "document_type": {"value": document_type, "confidence": 0.99 if document_type != "unknown" else 0.0},
        "extracted_fields": fields,
        "checks": checks,
        "summary": summary,
        "model": {"name": "deterministic-mock", "version": "0.1"},
    }


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/health":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        self._send_json(HTTPStatus.OK, {"status": "ok"})

    def do_POST(self):
        if self.path != "/check":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid request size"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode())
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON"})
            return
        self._send_json(HTTPStatus.OK, build_result(payload))

    def _send_json(self, status, body):
        encoded = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def main():
    ThreadingHTTPServer(("0.0.0.0", 8080), RequestHandler).serve_forever()


if __name__ == "__main__":
    main()
