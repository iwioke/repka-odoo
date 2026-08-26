#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


ODOO_AUTHORS = {"Odoo", "Odoo SA", "Odoo S.A."}


def query_local_modules(project_dir, condition):
    command = [
        "docker",
        "compose",
        "-f",
        str(project_dir / "compose.yaml"),
        "exec",
        "-T",
        "db",
        "psql",
        "-U",
        "odoo",
        "-d",
        "repka",
        "-At",
        "-c",
        f"SELECT name FROM ir_module_module WHERE {condition} ORDER BY name",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return {line for line in result.stdout.splitlines() if line}


def parse_args():
    parser = argparse.ArgumentParser(description="Compare source and local Odoo module sets")
    parser.add_argument("summary", type=Path)
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    return parser.parse_args()


def main():
    args = parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    source_odoo = {
        module
        for author in summary["authors"]
        if author["author"] in ODOO_AUTHORS
        for module in author["modules"]
    }
    available = query_local_modules(args.project_dir, "TRUE")
    installed = query_local_modules(args.project_dir, "state = 'installed'")

    result = {
        "source_odoo_count": len(source_odoo),
        "available_count": len(source_odoo & available),
        "missing_from_image": sorted(source_odoo - available),
        "already_installed": sorted(source_odoo & installed),
        "available_not_installed": sorted(source_odoo & available - installed),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
