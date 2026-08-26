#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


ODOO_AUTHORS = {"Odoo", "Odoo SA", "Odoo S.A."}
REPLACEMENTS = {
    "currency_numeric_codes": "repka_currency_numeric_codes",
    "ufs_fleet_simple_battery": "repka_fleet_battery",
}


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
    source_all = {
        module
        for author in summary["authors"]
        for module in author["modules"]
    }
    source_odoo = {
        module
        for author in summary["authors"]
        if author["author"] in ODOO_AUTHORS
        for module in author["modules"]
    }
    available = query_local_modules(args.project_dir, "TRUE")
    installed = query_local_modules(args.project_dir, "state = 'installed'")
    replacement_coverage = {
        source: replacement
        for source, replacement in REPLACEMENTS.items()
        if source in source_all and replacement in installed
    }
    covered = (source_all & installed) | set(replacement_coverage)

    result = {
        "source_total": len(source_all),
        "source_modules_covered": len(covered),
        "source_modules_installed_by_name": len(source_all & installed),
        "source_modules_replaced_clean_room": replacement_coverage,
        "source_modules_missing": sorted(source_all - covered),
        "project_modules": sorted(name for name in installed if name.startswith("repka_")),
        "source_odoo_count": len(source_odoo),
        "source_odoo_available": len(source_odoo & available),
        "source_odoo_missing_from_image": sorted(source_odoo - available),
        "source_odoo_not_installed": sorted(source_odoo & available - installed),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
