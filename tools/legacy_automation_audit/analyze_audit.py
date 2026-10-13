#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ODOO_AUTHORS = {"odoo s.a.", "odoo sa", "odoo"}
OCA_MARKERS = ("odoo community association", "github.com/oca", "odoo-community.org")
CUSTOM_NAME_MARKERS = (
    "ufs",
    "roundtrip",
    "lm_",
    "transport",
    "expedition",
    "forwarder",
    "waybill",
)


def records(data, model):
    return data.get("datasets", {}).get(model, {}).get("records", [])


def relation_id(value):
    return value[0] if isinstance(value, list) and value else False


def normalize_author(value):
    return " ".join((value or "Unknown").split())


def module_kind(module):
    author = normalize_author(module.get("author"))
    author_lower = author.lower()
    website = (module.get("website") or "").lower()
    if author_lower in ODOO_AUTHORS or website.startswith("https://www.odoo.com"):
        return "odoo"
    if any(marker in author_lower or marker in website for marker in OCA_MARKERS):
        return "oca"
    return "third_party_or_custom"


def split_modules(value):
    if not value:
        return set()
    if isinstance(value, list):
        values = value
    else:
        values = re.split(r"[,\s]+", str(value))
    return {str(item).strip() for item in values if str(item).strip()}


def build_summary(data):
    module_records = records(data, "ir.module.module")
    model_records = records(data, "ir.model")
    field_records = records(data, "ir.model.fields")
    view_records = records(data, "ir.ui.view")
    menu_records = records(data, "ir.ui.menu")
    dependency_records = records(data, "ir.module.module.dependency")
    external_ids = records(data, "ir.model.data")

    modules_by_id = {module["id"]: module for module in module_records}
    modules_by_name = {module["name"]: module for module in module_records}
    modules_by_kind = defaultdict(list)
    modules_by_author = defaultdict(list)

    for module in module_records:
        name = module.get("name")
        if not name:
            continue
        modules_by_kind[module_kind(module)].append(name)
        modules_by_author[normalize_author(module.get("author"))].append(name)

    applications = [
        {
            "name": module.get("name"),
            "label": module.get("shortdesc"),
            "author": normalize_author(module.get("author")),
            "version": module.get("latest_version"),
            "license": module.get("license"),
            "kind": module_kind(module),
        }
        for module in module_records
        if module.get("application")
    ]

    non_official_names = set(modules_by_kind["third_party_or_custom"])
    custom_candidates = {
        name
        for name in non_official_names
        if any(marker in name.lower() for marker in CUSTOM_NAME_MARKERS)
        or "roundtrip" in normalize_author(modules_by_name[name].get("author")).lower()
        or "roundtrip" in (modules_by_name[name].get("website") or "").lower()
    }

    dependencies = defaultdict(list)
    for dependency in dependency_records:
        module = modules_by_id.get(relation_id(dependency.get("module_id")))
        if module and dependency.get("name"):
            dependencies[module["name"]].append(dependency["name"])

    candidate_models = defaultdict(set)
    for model in model_records:
        model_modules = split_modules(model.get("modules"))
        for module_name in model_modules & custom_candidates:
            if model.get("model"):
                candidate_models[module_name].add(model["model"])

    candidate_fields = defaultdict(list)
    for field in field_records:
        field_modules = split_modules(field.get("modules"))
        for module_name in field_modules & custom_candidates:
            candidate_fields[module_name].append(
                {
                    "model": field.get("model"),
                    "name": field.get("name"),
                    "type": field.get("ttype"),
                    "relation": field.get("relation"),
                    "required": bool(field.get("required")),
                    "readonly": bool(field.get("readonly")),
                }
            )

    external_id_counts = Counter(
        item.get("module") for item in external_ids if item.get("module")
    )
    view_counts = Counter(view.get("model") for view in view_records if view.get("model"))
    view_type_counts = Counter(view.get("type") for view in view_records if view.get("type"))

    candidate_details = []
    for name in sorted(custom_candidates):
        module = modules_by_name[name]
        candidate_details.append(
            {
                "name": name,
                "label": module.get("shortdesc"),
                "author": normalize_author(module.get("author")),
                "version": module.get("latest_version"),
                "license": module.get("license"),
                "dependencies": sorted(set(dependencies.get(name, []))),
                "models": sorted(candidate_models.get(name, set())),
                "field_count": len(candidate_fields.get(name, [])),
                "fields": sorted(
                    candidate_fields.get(name, []),
                    key=lambda item: (item.get("model") or "", item.get("name") or ""),
                ),
                "external_id_count": external_id_counts.get(name, 0),
            }
        )

    top_level_menus = sorted(
        [
            {
                "name": menu.get("name"),
                "action": menu.get("action"),
                "sequence": menu.get("sequence"),
                "xml_id": menu.get("xml_id"),
            }
            for menu in menu_records
            if not menu.get("parent_id")
        ],
        key=lambda item: (item.get("sequence") or 0, item.get("name") or ""),
    )

    return {
        "source": data.get("source", {}),
        "dataset_counts": {
            model: len(dataset.get("records", []))
            for model, dataset in sorted(data.get("datasets", {}).items())
        },
        "module_counts": {
            "total": len(module_records),
            **{kind: len(names) for kind, names in sorted(modules_by_kind.items())},
        },
        "authors": [
            {"author": author, "count": len(names), "modules": sorted(names)}
            for author, names in sorted(modules_by_author.items(), key=lambda item: (-len(item[1]), item[0]))
        ],
        "applications": sorted(applications, key=lambda item: item.get("name") or ""),
        "non_official_modules": sorted(non_official_names),
        "custom_candidate_modules": candidate_details,
        "manual_models": sorted(
            model.get("model") for model in model_records if model.get("state") == "manual" and model.get("model")
        ),
        "manual_fields": sorted(
            f"{field.get('model')}.{field.get('name')}"
            for field in field_records
            if field.get("state") == "manual" and field.get("model") and field.get("name")
        ),
        "top_level_menus": top_level_menus,
        "view_counts_by_type": dict(sorted(view_type_counts.items())),
        "models_with_most_views": [
            {"model": model, "count": count}
            for model, count in view_counts.most_common(50)
        ],
        "security_counts": {
            "groups": len(records(data, "res.groups")),
            "model_access": len(records(data, "ir.model.access")),
            "record_rules": len(records(data, "ir.rule")),
        },
        "automation_counts": {
            "scheduled_actions": len(records(data, "ir.cron")),
            "server_actions": len(records(data, "ir.actions.server")),
            "automations": len(records(data, "base.automation")),
        },
        "errors": data.get("errors", []),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Build a safe technical summary from an Odoo audit")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    summary = build_summary(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "source": summary["source"],
        "module_counts": summary["module_counts"],
        "applications": len(summary["applications"]),
        "custom_candidates": len(summary["custom_candidate_modules"]),
        "manual_models": len(summary["manual_models"]),
        "manual_fields": len(summary["manual_fields"]),
        "errors": len(summary["errors"]),
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
