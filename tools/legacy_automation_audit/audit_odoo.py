#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import xmlrpc.client
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


BATCH_SIZE = 500

MODEL_SPECS = {
    "ir.module.module": {
        "domain": [["state", "=", "installed"]],
        "fields": [
            "name", "shortdesc", "summary", "description", "author", "website",
            "license", "category_id", "state", "latest_version", "published_version",
            "application", "auto_install", "demo", "icon", "dependencies_id",
        ],
    },
    "ir.module.module.dependency": {
        "fields": ["module_id", "name", "auto_install_required"],
    },
    "ir.model": {
        "fields": [
            "name", "model", "state", "transient", "modules", "info", "is_mail_thread",
            "is_mail_activity", "is_mail_blacklist", "order",
        ],
    },
    "ir.model.fields": {
        "fields": [
            "name", "complete_name", "field_description", "model", "model_id", "state",
            "modules", "ttype", "relation", "relation_field", "required", "readonly",
            "index", "store", "compute", "depends", "related", "copy", "translate",
            "help", "selection", "size", "on_delete", "groups",
        ],
    },
    "ir.ui.view": {
        "fields": [
            "name", "model", "type", "priority", "arch_db", "inherit_id", "key",
            "active", "mode", "xml_id", "groups_id",
        ],
    },
    "ir.ui.menu": {
        "fields": [
            "name", "complete_name", "parent_id", "action", "sequence", "groups_id",
            "active", "web_icon", "xml_id",
        ],
    },
    "ir.actions.act_window": {
        "fields": [
            "name", "type", "res_model", "view_mode", "view_ids", "domain", "context",
            "target", "search_view_id", "limit", "binding_model_id", "binding_type",
            "binding_view_types", "xml_id",
        ],
    },
    "ir.actions.server": {
        "fields": [
            "name", "type", "model_id", "state", "crud_model_id", "link_field_id",
            "binding_model_id", "binding_type", "binding_view_types", "xml_id",
        ],
    },
    "ir.actions.act_url": {
        "fields": ["name", "type", "target", "binding_model_id", "binding_type", "xml_id"],
    },
    "ir.actions.client": {
        "fields": ["name", "type", "tag", "target", "binding_model_id", "binding_type", "xml_id"],
    },
    "ir.actions.report": {
        "fields": [
            "name", "type", "model", "report_type", "report_name", "report_file",
            "print_report_name", "paperformat_id", "attachment_use", "multi", "groups_id",
            "binding_model_id", "binding_type", "binding_view_types", "xml_id",
        ],
    },
    "report.paperformat": {
        "fields": [
            "name", "format", "page_height", "page_width", "orientation", "margin_top",
            "margin_bottom", "margin_left", "margin_right", "header_line", "header_spacing",
            "dpi", "css_margins", "disable_shrinking", "xml_id",
        ],
    },
    "ir.model.access": {
        "fields": [
            "name", "active", "model_id", "group_id", "perm_read", "perm_write",
            "perm_create", "perm_unlink", "xml_id",
        ],
    },
    "ir.rule": {
        "fields": [
            "name", "active", "model_id", "domain_force", "groups", "global",
            "perm_read", "perm_write", "perm_create", "perm_unlink", "xml_id",
        ],
    },
    "res.groups": {
        "fields": [
            "name", "category_id", "privilege_id", "comment", "implied_ids", "share",
            "xml_id",
        ],
    },
    "ir.module.category": {
        "fields": ["name", "parent_id", "sequence", "visible", "exclusive", "xml_id"],
    },
    "base.automation": {
        "fields": [
            "name", "active", "model_id", "trigger", "trg_date_id", "trg_date_range",
            "trg_date_range_type", "filter_pre_domain", "filter_domain", "action_server_ids",
            "last_run", "xml_id",
        ],
    },
    "ir.cron": {
        "fields": [
            "name", "active", "user_id", "interval_number", "interval_type", "priority",
            "model_id", "state", "ir_actions_server_id", "xml_id",
        ],
    },
    "mail.template": {
        "fields": [
            "name", "model_id", "lang", "auto_delete", "use_default_to", "report_template_ids",
            "mail_server_id", "xml_id",
        ],
    },
    "ir.sequence": {
        "fields": [
            "name", "active", "code", "implementation", "prefix", "suffix", "padding",
            "number_increment", "use_date_range", "company_id", "xml_id",
        ],
    },
    "ir.sequence.date_range": {
        "fields": ["sequence_id", "date_from", "date_to"],
    },
    "ir.model.data": {
        "fields": ["name", "module", "model", "res_id", "noupdate", "complete_name"],
    },
    "res.lang": {
        "domain": [["active", "=", True]],
        "fields": ["name", "code", "iso_code", "url_code", "active", "direction", "date_format", "time_format"],
    },
}


class OdooAuditor:
    def __init__(self, url, database, username, password, delay=0.05):
        self.url = url.rstrip("/")
        self.database = database
        self.username = username
        self.password = password
        self.delay = delay
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)
        self.object = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)
        self.uid = self.common.authenticate(database, username, password, {})
        if not self.uid:
            raise RuntimeError("Odoo authentication failed")
        self.errors = []

    def execute(self, model, method, args=None, kwargs=None):
        time.sleep(self.delay)
        return self.object.execute_kw(
            self.database,
            self.uid,
            self.password,
            model,
            method,
            args or [],
            kwargs or {},
        )

    def available_fields(self, model):
        return self.execute(model, "fields_get", [], {"attributes": ["type", "string"]})

    def read_model(self, model, spec):
        available = self.available_fields(model)
        fields = [field for field in spec.get("fields", []) if field in available]
        domain = spec.get("domain", [])
        records = []
        offset = 0

        while True:
            page = self.execute(
                model,
                "search_read",
                [domain],
                {
                    "fields": fields,
                    "offset": offset,
                    "limit": BATCH_SIZE,
                    "order": "id",
                },
            )
            records.extend(page)
            if len(page) < BATCH_SIZE:
                break
            offset += len(page)

        return {
            "available_fields": sorted(available),
            "selected_fields": fields,
            "records": records,
        }

    def run(self):
        version = self.common.version()
        datasets = {}

        for model, spec in MODEL_SPECS.items():
            try:
                datasets[model] = self.read_model(model, spec)
                print(f"{model}: {len(datasets[model]['records'])}", flush=True)
            except xmlrpc.client.Fault as error:
                message = self.safe_error(error)
                self.errors.append({"model": model, "error": message})
                print(f"{model}: unavailable ({message})", flush=True)
            except (OSError, ValueError) as error:
                message = self.safe_error(error)
                self.errors.append({"model": model, "error": message})
                print(f"{model}: failed ({message})", flush=True)

        return {
            "audit_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": {
                "host": urlparse(self.url).hostname,
                "database": self.database,
                "server_version": version.get("server_version"),
                "server_serie": version.get("server_serie"),
                "protocol_version": version.get("protocol_version"),
            },
            "datasets": datasets,
            "errors": self.errors,
        }

    @staticmethod
    def safe_error(error):
        message = getattr(error, "faultString", str(error)).splitlines()[0]
        return message[:300]


def json_default(value):
    if isinstance(value, xmlrpc.client.Binary):
        return {"binary_size": len(value.data)}
    if isinstance(value, (bytes, bytearray)):
        return {"binary_size": len(value)}
    return str(value)


def build_summary(result):
    datasets = result["datasets"]
    modules = datasets.get("ir.module.module", {}).get("records", [])
    models = datasets.get("ir.model", {}).get("records", [])
    fields = datasets.get("ir.model.fields", {}).get("records", [])
    menus = datasets.get("ir.ui.menu", {}).get("records", [])

    applications = sorted(
        {record["name"] for record in modules if record.get("application") and record.get("name")}
    )
    manual_models = sorted(
        {
            record["model"]
            for record in models
            if record.get("state") == "manual" and record.get("model")
        }
    )
    manual_fields = sorted(
        {
            f"{record.get('model')}.{record.get('name')}"
            for record in fields
            if record.get("state") == "manual" and record.get("model") and record.get("name")
        }
    )
    top_level_menus = sorted(
        {record["name"] for record in menus if not record.get("parent_id") and record.get("name")}
    )

    return {
        "source": result["source"],
        "counts": {
            model: len(dataset["records"])
            for model, dataset in sorted(datasets.items())
        },
        "installed_modules": sorted(record["name"] for record in modules if record.get("name")),
        "applications": applications,
        "manual_models": manual_models,
        "manual_fields": manual_fields,
        "top_level_menus": top_level_menus,
        "errors": result["errors"],
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Read-only technical audit of an Odoo instance")
    parser.add_argument("--url", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument(
        "--password-file",
        type=Path,
        default=Path.home() / ".repka-odoo-password",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("audit"))
    return parser.parse_args()


def main():
    args = parse_args()
    password = args.password_file.read_text(encoding="utf-8").strip()
    if not password:
        raise RuntimeError("The Odoo password file is empty")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(args.output_dir, 0o700)

    auditor = OdooAuditor(args.url, args.database, args.username, password)
    result = auditor.run()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_path = args.output_dir / f"source_metadata_{timestamp}.json"
    summary_path = args.output_dir / f"source_summary_{timestamp}.json"

    raw_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    summary_path.write_text(json.dumps(build_summary(result), ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(raw_path, 0o600)
    os.chmod(summary_path, 0o600)

    print(f"Raw metadata saved to {raw_path}")
    print(f"Summary saved to {summary_path}")
    print(f"Unavailable datasets: {len(result['errors'])}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, xmlrpc.client.Error) as error:
        print(f"Audit failed: {OdooAuditor.safe_error(error)}", file=sys.stderr)
        raise SystemExit(1)
