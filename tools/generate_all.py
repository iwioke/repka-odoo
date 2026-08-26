#!/usr/bin/env python3
"""Generate all repka addons from audit specs in dependency order."""

import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDONS = os.path.join(REPO, "addons")
AUDIT = os.path.join(REPO, "audit")
GEN = os.path.join(REPO, "tools", "generate_addon.py")

# (spec_file, addon_name, manifest_name, extra_depends)
MODULES = [
    # Helper modules
    ("chatter_attachment_share_spec.json", "repka_chatter_attachment_share",
     "РЕПКА: Chatter Attachment Share", None),
    ("correspondent_bank_spec.json", "repka_correspondent_bank",
     "РЕПКА: Correspondent Bank", None),
    ("currency_rate_update_nbrb_ab_spec.json", "repka_currency_rate_nbrb",
     "РЕПКА: Currency Rate NBRB", None),
    ("fa_icon_widget_spec.json", "repka_fa_icon_widget",
     "РЕПКА: FA Icon Widget", None),
    ("leaflet_map_action_spec.json", "repka_leaflet_map_action",
     "РЕПКА: Leaflet Map Action", None),
    ("tree_open_by_ref_spec.json", "repka_tree_open_by_ref",
     "РЕПКА: Tree Open By Ref", None),
    ("tree_view_clipboard_copy_spec.json", "repka_tree_view_clipboard_copy",
     "РЕПКА: Tree View Clipboard Copy", None),
    # Main modules in dependency order
    ("ufs_fleet_spec.json", "repka_fleet",
     "РЕПКА: Автопарк", None),
    ("ufs_fleet_fuel_import_spec.json", "repka_fleet_fuel_import",
     "РЕПКА: Импорт топлива", None),
    ("ufs_fleet_maintenance_spec.json", "repka_fleet_maintenance",
     "РЕПКА: Обслуживание автопарка", None),
    ("ufs_fleet_tires_base_spec.json", "repka_fleet_tires",
     "РЕПКА: Шины", None),
    ("ufs_fleet_wallet_spec.json", "repka_fleet_wallet",
     "РЕПКА: Кошелёк автопарка", None),
    ("ufs_fleet_waybill_spec.json", "repka_fleet_waybill",
     "РЕПКА: Путевые листы", None),
    ("ufs_forwarding_spec.json", "repka_forwarding",
     "РЕПКА: Экспедирование", None),
    ("ufs_invoices_spec.json", "repka_invoices",
     "РЕПКА: Счета", None),
    ("ufs_invoices_base_reports_spec.json", "repka_invoices_base_reports",
     "РЕПКА: Печатные формы счетов", None),
    ("ufs_invoices_forwarding_spec.json", "repka_invoices_forwarding",
     "РЕПКА: Счета экспедирования", None),
    ("ufs_complex_reporting_spec.json", "repka_complex_reporting",
     "РЕПКА: Комплексная отчётность", None),
    ("ufs_special_lm_spec.json", "repka_special_lm",
     "РЕПКА: Спец. LM", None),
    ("ufs_excel_report_spec.json", "repka_excel_report",
     "РЕПКА: Excel-отчёты", None),
]


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    for spec_file, addon_name, manifest_name, extra_deps in MODULES:
        if only and addon_name not in only:
            continue
        spec_path = os.path.join(AUDIT, spec_file)
        addon_dir = os.path.join(ADDONS, addon_name)
        if not os.path.exists(spec_path):
            print(f"SKIP {addon_name}: spec not found at {spec_path}")
            continue
        cmd = [
            sys.executable, GEN, spec_path, addon_dir, addon_name,
            "--manifest-name", manifest_name,
        ]
        if extra_deps:
            cmd.extend(["--depends", extra_deps])
        print(f"Generating {addon_name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr[:500]}")
        else:
            print(f"  OK: {result.stdout.strip()}")


if __name__ == "__main__":
    main()
