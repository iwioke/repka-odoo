"""Extract a structured clean-room spec for a source module from the raw audit.

Reads the browser audit JSON and produces, for a given source module name,
a JSON document containing:
  - module metadata and dependencies
  - models defined by the module (via ir.model.data ownership)
  - fields defined by the module (via ir.model.data ownership), grouped by model
  - field selections (ir.model.fields.selection owned by the module)
  - views owned by the module
  - menus owned by the module
  - window actions owned by the module
  - server actions owned by the module
  - reports owned by the module
  - security groups owned by the module
  - model access records owned by the module
  - record rules owned by the module
  - cron records owned by the module
  - mail templates owned by the module
  - sequences owned by the module
  - paper formats owned by the module

Ownership is determined by ir.model.data records whose ``module`` field equals
the source module name. This is metadata-only and does not copy any source code.

Usage:
    python3 tools/extract_module_spec.py <raw_audit.json> <module_name> <out.json>
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict


def _by_module(ir_model_data, module_name):
    """Return dict complete_name -> record for ir.model.data owned by module."""
    owned = {}
    for r in ir_model_data:
        if r.get("module") == module_name:
            owned[r.get("complete_name")] = r
    return owned


def _records(dataset):
    return dataset.get("records", [])


def _selected_fields(dataset):
    return dataset.get("selected_fields", [])


def extract(raw, module_name):
    ds = raw["datasets"]
    imd = _records(ds["ir.model.data"])
    owned = _by_module(imd, module_name)

    # index ir.model.data by (model, res_id) for quick ownership lookup
    owned_by_target = defaultdict(dict)
    for r in imd:
        if r.get("module") == module_name:
            owned_by_target[r.get("model")][r.get("res_id")] = r

    # module record
    mods = _records(ds["ir.module.module"])
    mod_rec = next((m for m in mods if m.get("name") == module_name), None)

    # dependencies
    deps = _records(ds["ir.module.module.dependency"])
    dep_ids = set(mod_rec.get("dependencies_id", []) or []) if mod_rec else set()
    mod_deps = [d.get("name") for d in deps if d.get("id") in dep_ids]

    # models defined by the module
    models = _records(ds["ir.model"])
    model_id_to_rec = {m["id"]: m for m in models}
    owned_model_ids = set(owned_by_target.get("ir.model", {}).keys())
    owned_models = [model_id_to_rec[i] for i in owned_model_ids if i in model_id_to_rec]
    owned_models.sort(key=lambda m: m.get("model", ""))

    # fields defined by the module
    fields = _records(ds["ir.model.fields"])
    field_id_to_rec = {f["id"]: f for f in fields}
    owned_field_ids = set(owned_by_target.get("ir.model.fields", {}).keys())
    owned_fields = [field_id_to_rec[i] for i in owned_field_ids if i in field_id_to_rec]
    fields_by_model = defaultdict(list)
    for f in owned_fields:
        fields_by_model[f.get("model")].append(f)
    for k in fields_by_model:
        fields_by_model[k].sort(key=lambda f: (f.get("name", "")))

    # selections
    selections = _records(ds.get("ir.model.fields.selection", {"records": []}))
    owned_sel_ids = set(owned_by_target.get("ir.model.fields.selection", {}).keys())
    sel_id_to_rec = {s["id"]: s for s in selections}
    owned_selections = [sel_id_to_rec[i] for i in owned_sel_ids if i in sel_id_to_rec]
    sel_by_field = defaultdict(list)
    for s in owned_selections:
        sel_by_field[s.get("field_id")].append(s)

    # attach selections to fields
    for f in owned_fields:
        f["_selections"] = [
            {"value": s.get("value"), "name": s.get("name")}
            for s in sel_by_field.get(f["id"], [])
        ]

    # views
    views = _records(ds["ir.ui.view"])
    owned_view_ids = set(owned_by_target.get("ir.ui.view", {}).keys())
    owned_views = [v for v in views if v.get("id") in owned_view_ids]
    owned_views.sort(key=lambda v: (str(v.get("model") or ""), str(v.get("name") or "")))

    # menus
    menus = _records(ds["ir.ui.menu"])
    owned_menu_ids = set(owned_by_target.get("ir.ui.menu", {}).keys())
    owned_menus = [m for m in menus if m.get("id") in owned_menu_ids]
    owned_menus.sort(key=lambda m: m.get("id", 0))

    # window actions
    acts = _records(ds["ir.actions.act_window"])
    owned_act_ids = set(owned_by_target.get("ir.actions.act_window", {}).keys())
    owned_acts = [a for a in acts if a.get("id") in owned_act_ids]
    owned_acts.sort(key=lambda a: a.get("id", 0))

    # server actions
    srv = _records(ds["ir.actions.server"])
    owned_srv_ids = set(owned_by_target.get("ir.actions.server", {}).keys())
    owned_srv = [s for s in srv if s.get("id") in owned_srv_ids]
    owned_srv.sort(key=lambda s: s.get("id", 0))

    # reports
    reports = _records(ds.get("ir.actions.report", {"records": []}))
    owned_rep_ids = set(owned_by_target.get("ir.actions.report", {}).keys())
    owned_reports = [r for r in reports if r.get("id") in owned_rep_ids]
    owned_reports.sort(key=lambda r: r.get("id", 0))

    # groups
    groups = _records(ds["res.groups"])
    owned_grp_ids = set(owned_by_target.get("res.groups", {}).keys())
    owned_groups = [g for g in groups if g.get("id") in owned_grp_ids]
    owned_groups.sort(key=lambda g: g.get("id", 0))

    # model access
    access = _records(ds["ir.model.access"])
    owned_acc_ids = set(owned_by_target.get("ir.model.access", {}).keys())
    owned_access = [a for a in access if a.get("id") in owned_acc_ids]
    owned_access.sort(key=lambda a: (a.get("model_id", [None, ""])[1] if isinstance(a.get("model_id"), list) else a.get("model_id"), a.get("id", 0)))

    # record rules
    rules = _records(ds["ir.rule"])
    owned_rule_ids = set(owned_by_target.get("ir.rule", {}).keys())
    owned_rules = [r for r in rules if r.get("id") in owned_rule_ids]
    owned_rules.sort(key=lambda r: r.get("id", 0))

    # cron
    crons = _records(ds.get("ir.cron", {"records": []}))
    owned_cron_ids = set(owned_by_target.get("ir.cron", {}).keys())
    owned_crons = [c for c in crons if c.get("id") in owned_cron_ids]
    owned_crons.sort(key=lambda c: c.get("id", 0))

    # mail templates
    mt = _records(ds.get("mail.template", {"records": []}))
    owned_mt_ids = set(owned_by_target.get("mail.template", {}).keys())
    owned_mt = [m for m in mt if m.get("id") in owned_mt_ids]
    owned_mt.sort(key=lambda m: m.get("id", 0))

    # sequences
    seqs = _records(ds.get("ir.sequence", {"records": []}))
    owned_seq_ids = set(owned_by_target.get("ir.sequence", {}).keys())
    owned_seqs = [s for s in seqs if s.get("id") in owned_seq_ids]
    owned_seqs.sort(key=lambda s: s.get("id", 0))

    # paper formats
    pf = _records(ds.get("report.paperformat", {"records": []}))
    owned_pf_ids = set(owned_by_target.get("report.paperformat", {}).keys())
    owned_pf = [p for p in pf if p.get("id") in owned_pf_ids]
    owned_pf.sort(key=lambda p: p.get("id", 0))

    # module category
    cats = _records(ds.get("ir.module.category", {"records": []}))
    owned_cat_ids = set(owned_by_target.get("ir.module.category", {}).keys())
    owned_cats = [c for c in cats if c.get("id") in owned_cat_ids]

    return {
        "module": {
            "name": mod_rec.get("name") if mod_rec else module_name,
            "shortdesc": mod_rec.get("shortdesc") if mod_rec else None,
            "summary": (mod_rec.get("summary") or "").strip() if mod_rec else None,
            "author": mod_rec.get("author") if mod_rec else None,
            "license": mod_rec.get("license") if mod_rec else None,
            "latest_version": mod_rec.get("latest_version") if mod_rec else None,
            "application": mod_rec.get("application") if mod_rec else None,
            "dependencies": mod_deps,
        },
        "models": [
            {
                "id": m.get("id"),
                "name": m.get("name"),
                "model": m.get("model"),
                "state": m.get("state"),
                "transient": m.get("transient"),
                "info": (m.get("info") or "").strip(),
                "is_mail_thread": m.get("is_mail_thread"),
                "is_mail_activity": m.get("is_mail_activity"),
                "order": m.get("order"),
                "modules": m.get("modules"),
            }
            for m in owned_models
        ],
        "fields": {
            model: [
                {
                    "id": f.get("id"),
                    "name": f.get("name"),
                    "field_description": f.get("field_description"),
                    "ttype": f.get("ttype"),
                    "relation": f.get("relation"),
                    "relation_field": f.get("relation_field"),
                    "required": f.get("required"),
                    "readonly": f.get("readonly"),
                    "store": f.get("store"),
                    "copied": f.get("copied"),
                    "translate": f.get("translate"),
                    "help": f.get("help"),
                    "compute": f.get("compute"),
                    "related": f.get("related"),
                    "depends": f.get("depends"),
                    "selection": f.get("selection"),
                    "selections": f.get("_selections"),
                    "relation_table": f.get("relation_table"),
                    "column1": f.get("column1"),
                    "column2": f.get("column2"),
                    "group_operator": f.get("group_operator"),
                    "digits": f.get("digits"),
                    "domain": f.get("domain"),
                }
                for f in flist
            ]
            for model, flist in fields_by_model.items()
        },
        "views": owned_views,
        "menus": owned_menus,
        "window_actions": owned_acts,
        "server_actions": owned_srv,
        "reports": owned_reports,
        "groups": owned_groups,
        "model_access": owned_access,
        "record_rules": owned_rules,
        "crons": owned_crons,
        "mail_templates": owned_mt,
        "sequences": owned_seqs,
        "paper_formats": owned_pf,
        "module_categories": owned_cats,
    }


def main(argv):
    if len(argv) != 4:
        print(__doc__)
        return 2
    raw_path, module_name, out_path = argv[1], argv[2], argv[3]
    with open(raw_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    spec = extract(raw, module_name)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(spec, fh, ensure_ascii=False, indent=2, sort_keys=False)
    n_models = len(spec["models"])
    n_fields = sum(len(v) for v in spec["fields"].values())
    print(
        f"{module_name}: {n_models} models, {n_fields} fields, "
        f"{len(spec['views'])} views, {len(spec['menus'])} menus, "
        f"{len(spec['window_actions'])} window actions, "
        f"{len(spec['groups'])} groups, {len(spec['model_access'])} ACLs, "
        f"{len(spec['record_rules'])} record rules, "
        f"{len(spec['crons'])} crons, {len(spec['reports'])} reports"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
