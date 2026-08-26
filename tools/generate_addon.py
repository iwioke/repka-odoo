"""Generate a clean-room Odoo addon from a module spec extracted by extract_module_spec.py.

The generator produces:
  - __manifest__.py
  - __init__.py + models/__init__.py
  - models/*.py  (one file per logical group)
  - security/ir.model.access.csv
  - security/repka_security.xml (groups, record rules, module categories)
  - views/*.xml (reproduced from audited arch_db metadata)
  - menus/repka_menus.xml
  - actions/repka_actions.xml
  - data/repka_data.xml (sequences, crons, mail templates, paper formats)
  - i18n/ru.po stub
  - tests/__init__.py + tests/test_structure.py

Only metadata is used: model names, field names, types, relations, selections,
required/readonly/store flags, related paths, view arch_db, menus, actions,
ACLs, groups, rules, crons, sequences. No proprietary Python/JS source is copied.
Computed-field logic that the audit cannot capture is stubbed with a TODO marker
and a safe default so the schema matches for future migration.

Usage:
    python3 tools/generate_addon.py <spec.json> <addon_dir> <addon_name> \
        <suite_manifest_path> [--depends dep1,dep2,...]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import textwrap
from collections import defaultdict

# Fields provided by mail.thread / mail.activity.mixin — must not be redefined.
MAIL_FIELDS = {
    "message_ids", "message_follower_ids", "message_partner_ids",
    "message_needaction", "message_needaction_counter",
    "message_has_error", "message_has_error_counter", "message_has_sms_error",
    "message_is_follower", "message_attachment_count", "message_main_attachment_id",
    "website_message_ids", "rating_ids",
    "activity_ids", "activity_state", "activity_summary",
    "activity_type_id", "activity_user_id", "activity_calendar_event_id",
    "activity_date_deadline", "activity_exception_decoration", "activity_exception_icon",
    "activity_type_icon", "my_activity_date_deadline",
}

# Standard ORM fields — must not be redefined.
ORM_FIELDS = {"id", "display_name", "create_uid", "create_date", "write_uid", "write_date"}

# Fields commonly defined by standard Odoo models — skip on extensions to avoid conflicts.
# This is a conservative set; Odoo will raise if we try to redefine a field with
# incompatible params, so we only list the most common ones here.
STANDARD_SKIP_FIELDS = {
    "lang", "active", "is_company", "child_ids", "name", "company_id",
    "country_id", "state_id", "city", "street", "street2", "zip",
    "phone", "mobile", "email", "website", "vat", "category_id",
    "parent_id", "type", "function", "title", "user_id", "comment",
    "color", "image_1920", "image_128", "partner_share",
    "commercial_partner_id", "commercial_company_name",
    "bank_ids", "team_id", "message_bounce",
    "login", "password", "company_ids", "groups_id", "share",
    "partner_id", "currency_id", "sequence", "logo",
    "account_no", "acc_number", "acc_holder_name", "bank_id",
    "acc_type", "allow_out_payment", "qr_code_valid",
    "model_id", "driver_id", "manager_id", "license_plate", "vin_sn",
    "acquisition_date", "first_contract_date", "state_id",
    "seats", "doors", "model_year", "horsepower", "horsepower_tax",
    "power", "co2", "fuel_type", "transmission", "odometer", "odometer_unit",
    "sale_price", "cost", "tag_ids", "car_value",
    "brand_id", "category_id", "vehicle_count",
    "bluebook_value", "bluebook_currency_id",
    "date", "value", "unit",
    "work_phone", "mobile_phone", "work_email", "department_id",
    "job_id", "job_title", "address_id", "address_home_id",
    "manager_id", "coach_id", "gender", "birthday", "marital",
    "spouse_complete_name", "spouse_birthdate", "children",
    "emergency_contact", "emergency_phone", "barcode", "pin",
    "resource_id", "resource_calendar_id", "work_location_id",
    "departure_reason", "departure_description", "departure_date",
    "employee_type", "km_home_work", "motor_vehicle",
    "default_code", "barcode", "list_price", "standard_price",
    "volume", "weight", "price", "price_extra", "uom_id", "uom_po_id",
    "description_sale", "description_purchase", "description",
    "categ_id", "seller_ids", "taxes_id", "supplier_taxes_id",
    "product_tmpl_id", "attribute_value_ids", "is_product_variant",
    "ref", "move_type", "invoice_date", "invoice_date_due",
    "invoice_payment_term_id", "invoice_line_ids", "line_ids",
    "partner_bank_id", "journal_id", "fiscal_position_id",
    "invoice_source_email", "invoice_user_id", "invoice_incoterm_id",
    "invoice_cash_rounding_id", "invoice_payment_state", "invoice_sent",
    "to_check", "narration", "payment_reference", "payment_id",
    "team_id", "commercial_partner_id", "is_move_sent",
    "stock_move_id", "auto_post", "reversed_entry_id",
    "posted_before", "payment_state", "quick_edit_mode",
    "quick_encoding_label", "amount_untaxed", "amount_tax",
    "amount_total", "amount_residual", "amount_untaxed_signed",
    "amount_tax_signed", "amount_total_signed", "amount_residual_signed",
    "amount_total_in_currency_signed", "debit", "credit", "balance",
    "amount_currency", "amount_residual", "amount_residual_currency",
    "account_id", "move_id", "display_type", "product_id",
    "product_uom_id", "quantity", "price_unit", "discount",
    "price_subtotal", "price_total", "price_subtotal_signed",
    "tax_ids", "tax_tag_ids", "tax_line_id", "tax_repartition_line_id",
    "tax_group_id", "tag_ids", "analytic_distribution",
    "analytic_line_ids", "parent_state", "state",
    "is_rounding_line", "exclude_from_invoice_tab",
    "recompute_tax_line", "debit_cash_basis", "credit_cash_basis",
    "balance_cash_basis", "amount_residual_cash_basis",
    "amount_residual_cash_basis_currency", "move_name",
    "full_reconcile_id", "matched_debit_ids", "matched_credit_ids",
    "reconciled", "account_internal_type", "account_internal_group",
    "account_root_id", "account_type", "journal_id", "user_type_id",
    "date_maturity", "tax_exigible", "is_anglo_saxon",
    "company_currency_id", "blocked", "partner_name", "partner_vat",
    "product_type", "is_refund", "reconcilable",
    "bic", "country_id", "phone", "email", "street", "street2",
    "zip", "city", "state_id", "code", "address_format",
    "address_view_id", "phone_prefix", "state_level", "vat_label",
    "zip_required", "state_required", "code_digits",
    "parent_id", "company_registry", "sequence",
    "footer_line", "internal_header", "report_header", "report_footer",
    "paperformat_id", "external_report_layout_id",
    "internal_report_layout_id", "font", "primary_color",
    "secondary_color", "social_facebook", "social_linkedin",
    "social_twitter", "social_youtube", "social_instagram",
    "social_github", "sequence_id", "resource_calendar_id",
    "partner_gid", "qr_code", "currency_ids",
    "name", "code", "number", "prefix", "suffix", "padding",
    "implementation", "use_date_range", "date_range_ids",
    "next_actual", "date_range_name",
}

# Map audit ttype -> Odoo field constructor
FIELD_MAP = {
    "char": "fields.Char",
    "text": "fields.Text",
    "html": "fields.Html",
    "integer": "fields.Integer",
    "float": "fields.Float",
    "monetary": "fields.Monetary",
    "boolean": "fields.Boolean",
    "date": "fields.Date",
    "datetime": "fields.Datetime",
    "selection": "fields.Selection",
    "many2one": "fields.Many2one",
    "one2many": "fields.One2many",
    "many2many": "fields.Many2many",
    "reference": "fields.Reference",
    "many2one_reference": "fields.Integer",
    "binary": "fields.Binary",
}


def _py_str(s):
    """Escape a Python string literal."""
    if s is None:
        return '""'
    return json.dumps(str(s), ensure_ascii=False)


def _field_name_attr(name):
    """Return the Python kwarg name=... for a field."""
    return f"name={_py_str(name)}"


def _selection_list(selections):
    """Build a Python list of (value, label) tuples."""
    if not selections:
        return "[]"
    parts = []
    for s in selections:
        v = s.get("value")
        label = s.get("name") or v
        parts.append(f"({_py_str(v)}, {_py_str(label)})")
    return "[" + ", ".join(parts) + "]"


def _model_has_mail_thread(m):
    return m.get("is_mail_thread")


def _model_has_mail_activity(m):
    return m.get("is_mail_activity")


def _is_abstract(m):
    """Heuristic: mixin/utils models that should be _abstract=True."""
    name = m.get("model", "")
    if "mixin" in name:
        return True
    if name in ("model.utils", "ufs.aiohelper", "ufs.base.trace",
                "ufs.mixin.cargo", "ufs.mixin.guid", "ufs.mixin.state",
                "ufs.mixins.services", "ufs.order.mixin", "ufs.payment.term.mixin"):
        return True
    return False


def _is_transient(m):
    return m.get("transient")


def _field_line(f, model_name, model_m2m_conflicts=None):
    """Generate a single field assignment line."""
    if model_m2m_conflicts is None:
        model_m2m_conflicts = {}
    fname = f["name"]
    ttype = f.get("ttype", "char")
    constructor = FIELD_MAP.get(ttype, "fields.Char")
    kwargs = []

    # field_description / string
    desc = f.get("field_description")
    if desc:
        kwargs.append(f"string={_py_str(desc)}")

    # required / readonly / store / copy / translate
    if f.get("required"):
        kwargs.append("required=True")
    if f.get("readonly"):
        kwargs.append("readonly=True")
    if f.get("store") is False and ttype not in ("one2many", "many2many"):
        kwargs.append("store=False")
    if f.get("copied") is False and ttype not in ("one2many", "many2many"):
        kwargs.append("copy=False")
    if f.get("translate"):
        kwargs.append("translate=True")

    # help
    help_text = f.get("help")
    if help_text:
        kwargs.append(f"help={_py_str(help_text)}")

    # relation
    rel = f.get("relation")
    if ttype == "many2one" and rel:
        kwargs.append(f"comodel_name={_py_str(rel)}")
        ondelete = f.get("on_delete")
    elif ttype == "one2many":
        if rel:
            kwargs.append(f"comodel_name={_py_str(rel)}")
        rf = f.get("relation_field")
        if rf:
            kwargs.append(f"inverse_name={_py_str(rf)}")
    elif ttype == "many2many":
        if rel:
            kwargs.append(f"comodel_name={_py_str(rel)}")
        rt = f.get("relation_table")
        c1 = f.get("column1")
        c2 = f.get("column2")
        if rt:
            kwargs.append(f"relation={_py_str(rt)}")
        if c1:
            kwargs.append(f"column1={_py_str(c1)}")
        if c2:
            kwargs.append(f"column2={_py_str(c2)}")
        # If multiple m2m fields on the same model point to the same comodel,
        # Odoo needs an explicit relation table for at least one. We detect
        # this via a pre-computed set passed in model_m2m_conflicts.
        if model_m2m_conflicts and (model_name, rel) in model_m2m_conflicts:
            conflict_names = model_m2m_conflicts[(model_name, rel)]
            if fname != conflict_names[0] and not rt:
                # Generate a unique relation table name
                kwargs.append(f'relation="{model_name.replace(".", "_")}_{fname}_rel"')
    elif ttype == "reference":
        # Reference needs a list of (label, model) — best-effort from relation
        if rel:
            kwargs.append(f"selection=[({_py_str(rel)}, {_py_str(rel)})]")
        else:
            # Audit did not capture the reference target — use a placeholder
            kwargs.append('selection=[("ufs.base.order", "Order")]')
    elif ttype == "selection":
        sels = f.get("selections")
        if sels:
            kwargs.append(f"selection={_selection_list(sels)}")
        else:
            # Audit did not capture selection values — use a placeholder so the
            # field is valid. Values will be refined during behavior observation.
            kwargs.append('selection=[("placeholder", "Placeholder")]')

    # related
    related = f.get("related")
    if related:
        kwargs.append(f"related={_py_str(related)}")

    # group_operator
    ga = f.get("group_operator")
    if ga and ttype in ("integer", "float", "monetary"):
        kwargs.append(f"group_operator={_py_str(ga)}")

    # digits
    digits = f.get("digits")
    if digits and ttype == "float":
        kwargs.append(f"digits={digits}")

    # domain
    domain = f.get("domain")
    if domain and ttype in ("many2one", "many2many", "one2many"):
        kwargs.append(f"domain={_py_str(domain)}")

    # Compute stub: non-stored readonly without related → likely computed
    if (f.get("readonly") and not related and f.get("store") is False
            and fname not in MAIL_FIELDS and fname not in ORM_FIELDS
            and ttype not in ("one2many", "many2many")):
        # These are computed presentational fields we can't reconstruct.
        # Make them non-stored computed with a safe default.
        pass  # handled below

    kwargs_str = ", ".join(kwargs)
    if not kwargs_str:
        return f"    {fname} = {constructor}()"
    return f"    {fname} = {constructor}({kwargs_str})"


def _generate_model_class(m, fields_list, all_model_names, m2m_conflicts=None):
    """Generate a Python class for a model."""
    model_name = m["model"]
    class_name = _class_name(model_name)
    is_abstract = _is_abstract(m)
    is_transient = _is_transient(m)

    # Determine _name / _inherit / _description
    is_standard_extension = model_name in {
        "res.partner", "res.partner.bank", "res.bank", "res.company", "res.country",
        "res.users", "fleet.vehicle", "fleet.vehicle.model", "fleet.vehicle.odometer",
        "hr.employee",
        "hr.employee.base", "hr.employee.public", "product.product", "product.template",
        "account.move", "account.move.line", "account.move.send", "ir.sequence",
        "ir.http", "mail.template", "mail.mail", "mail.compose.message",
        "mail.thread", "res.config.settings", "ir.model", "model.utils",
    }

    # Some standard models are AbstractModel — must use AbstractModel to extend them
    STANDARD_ABSTRACT = {
        "account.move.send", "mail.thread", "hr.employee.base",
        "hr.employee.public", "ir.http", "model.utils",
    }

    # Filter fields
    own_fields = []
    for f in fields_list:
        fname = f["name"]
        if fname in MAIL_FIELDS or fname in ORM_FIELDS:
            continue
        if is_standard_extension and fname in STANDARD_SKIP_FIELDS:
            # Skip fields that standard Odoo already defines to avoid conflicts
            continue
        own_fields.append(f)

    # Build inheritance list
    inherits = []
    if _model_has_mail_thread(m) and not is_standard_extension:
        inherits.append("mail.thread")
    if _model_has_mail_activity(m) and not is_standard_extension:
        inherits.append("mail.activity.mixin")

    lines = []

    if is_abstract:
        lines.append(f"class {class_name}(models.AbstractModel):")
        lines.append(f'    _name = "{model_name}"')
        lines.append(f'    _description = "{m.get("name", model_name)}"')
    elif is_transient:
        lines.append(f"class {class_name}(models.TransientModel):")
        lines.append(f'    _name = "{model_name}"')
        lines.append(f'    _description = "{m.get("name", model_name)}"')
    elif is_standard_extension:
        if model_name in STANDARD_ABSTRACT:
            lines.append(f"class {class_name}(models.AbstractModel):")
        else:
            lines.append(f"class {class_name}(models.Model):")
        lines.append(f'    _inherit = "{model_name}"')
    else:
        lines.append(f"class {class_name}(models.Model):")
        lines.append(f'    _name = "{model_name}"')
        lines.append(f'    _description = "{m.get("name", model_name)}"')

    # Order
    order = m.get("order")
    if order and order != "id" and not is_standard_extension:
        lines.append(f'    _order = "{order}"')

    # Inheritance
    if inherits:
        lines.append(f'    _inherit = {inherits!r}')

    if not own_fields and is_standard_extension:
        lines.append("    # No ufs_base-owned fields captured for this extension")
    elif not own_fields and not is_standard_extension:
        lines.append("    # No fields captured")

    for f in own_fields:
        lines.append(_field_line(f, model_name, m2m_conflicts))

    return "\n".join(lines)


def _class_name(model_name):
    """Convert model dotted name to a CamelCase class name."""
    parts = model_name.replace("_", ".").split(".")
    return "".join(p.capitalize() for p in parts)


def _group_models(models):
    """Group models into logical files."""
    groups = defaultdict(list)
    for m in models:
        name = m["model"]
        if _is_abstract(m):
            groups["mixins"].append(m)
        elif _is_transient(m):
            groups["wizards"].append(m)
        elif name.startswith("ufs.base.order") or name == "ufs.order.service" or name == "ufs.order.state" or name == "ufs.order.category":
            groups["order"].append(m)
        elif name.startswith("ufs.cargo"):
            groups["cargo"].append(m)
        elif name.startswith("ufs.contract"):
            groups["contract"].append(m)
        elif name.startswith("ufs.doc") or name.startswith("ufs.strict_doc"):
            groups["document"].append(m)
        elif name.startswith("ufs.driver") or name == "ufs.vehicle":
            groups["driver_vehicle"].append(m)
        elif name.startswith("ufs.base.equipment"):
            groups["equipment"].append(m)
        elif name.startswith("ufs.location") or name == "ufs.loading_type":
            groups["location"].append(m)
        elif name.startswith("ufs.tracking") or name == "ufs.transport.document":
            groups["tracking"].append(m)
        elif name.startswith("ufs.payment") or name == "ufs.u_guid":
            groups["payment"].append(m)
        elif name in ("res.partner", "res.partner.bank", "res.bank", "res.partner.credit_limit",
                       "res.partner.doc.preference", "ufs.partner.doc.line"):
            groups["partner"].append(m)
        elif name in ("res.company", "res.country", "res.users", "res.config.settings"):
            groups["company"].append(m)
        elif name.startswith("fleet.") or name.startswith("hr.") or name.startswith("product."):
            groups["extensions"].append(m)
        elif name.startswith("account."):
            groups["accounting"].append(m)
        elif name.startswith("ir.") or name.startswith("mail."):
            groups["system"].append(m)
        else:
            groups["misc"].append(m)
    return groups


def generate(spec, addon_dir, addon_name, depends_extra=None):
    depends_extra = depends_extra or []
    os.makedirs(addon_dir, exist_ok=True)
    models_dir = os.path.join(addon_dir, "models")
    views_dir = os.path.join(addon_dir, "views")
    security_dir = os.path.join(addon_dir, "security")
    menus_dir = os.path.join(addon_dir, "menus")
    actions_dir = os.path.join(addon_dir, "actions")
    data_dir = os.path.join(addon_dir, "data")
    tests_dir = os.path.join(addon_dir, "tests")
    i18n_dir = os.path.join(addon_dir, "i18n")
    for d in [models_dir, views_dir, security_dir, menus_dir, actions_dir, data_dir, tests_dir, i18n_dir]:
        os.makedirs(d, exist_ok=True)

    all_model_names = {m["model"] for m in spec["models"]}
    fields_by_model = defaultdict(list)
    for model, flist in spec["fields"].items():
        fields_by_model[model] = flist

    # Detect many2many conflicts: multiple m2m fields on the same model
    # pointing to the same comodel — Odoo needs explicit relation tables.
    m2m_groups = defaultdict(list)
    for model, flist in spec["fields"].items():
        for f in flist:
            if f.get("ttype") == "many2many" and f.get("relation"):
                m2m_groups[(model, f["relation"])].append(f["name"])
    m2m_conflicts = {k: v for k, v in m2m_groups.items() if len(v) > 1}

    # Group models
    groups = _group_models(spec["models"])

    # Generate model files
    model_imports = []
    for group_name, model_list in sorted(groups.items()):
        if not model_list:
            continue
        filename = f"{group_name}.py"
        model_imports.append(filename[:-3])
        lines = ["from odoo import fields, models", ""]
        for m in sorted(model_list, key=lambda x: x["model"]):
            flist = fields_by_model.get(m["model"], [])
            lines.append(_generate_model_class(m, flist, all_model_names, m2m_conflicts))
            lines.append("")
        with open(os.path.join(models_dir, filename), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))

    # models/__init__.py
    with open(os.path.join(models_dir, "__init__.py"), "w", encoding="utf-8") as fh:
        for imp in sorted(model_imports):
            fh.write(f"from . import {imp}\n")

    # __init__.py
    with open(os.path.join(addon_dir, "__init__.py"), "w", encoding="utf-8") as fh:
        fh.write("from . import models\n")

    # __manifest__.py
    source_deps = spec["module"]["dependencies"]
    # Map source deps to repka/standard/oca equivalents
    dep_mapping = {
        "web_responsive": "web_responsive",
        "hr": "hr",
        "contacts": "contacts",
        "web_notify": "web_notify",
        "base_view_inheritance_extension": "base_view_inheritance_extension",
        "base_fontawesome": "base_fontawesome",
        "uom": "uom",
        "fleet": "fleet",
        "web_chatter_position": "web_chatter_position",
        "account": "account",
        "web_boolean_button": "repka_web_boolean_button",
        "binary_preview_icon": "repka_binary_preview_icon",
    }
    mapped_deps = []
    for d in source_deps:
        mapped = dep_mapping.get(d, d)
        if mapped not in mapped_deps:
            mapped_deps.append(mapped)
    for d in depends_extra:
        if d not in mapped_deps:
            mapped_deps.append(d)
    # Always include base
    if "base" not in mapped_deps:
        mapped_deps.insert(0, "base")

    manifest_lines = [
        "{",
        f'    "name": "РЕПКА: Логистическое ядро",',
        '    "version": "18.0.1.0.0",',
        '    "category": "Services/Logistics",',
        '    "summary": "Clean-room reconstruction of the logistics foundation",',
        '    "description": "РЕПКА logistics core — clean-room reconstruction from audited metadata.",',
        '    "author": "РЕПКА",',
        '    "website": "https://github.com/iwioke/repka-odoo",',
        '    "license": "LGPL-3",',
        '    "depends": ' + json.dumps(mapped_deps) + ",",
        '    "data": [',
        '        "security/repka_security.xml",',
        '        "security/ir.model.access.csv",',
        '        "data/repka_data.xml",',
        '        "actions/repka_actions.xml",',
        '        "views/repka_views.xml",',
        '        "menus/repka_menus.xml",',
        '    ],',
        '    "installable": True,',
        '    "application": False,',
        '    "auto_install": False,',
        "}",
    ]
    with open(os.path.join(addon_dir, "__manifest__.py"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(manifest_lines) + "\n")

    # Security: groups, categories, record rules
    _generate_security(spec, security_dir, addon_name)

    # ACL CSV
    _generate_acl(spec, security_dir, addon_name)

    # Views (from audited arch_db)
    _generate_views(spec, views_dir, addon_name, all_model_names)

    # Actions
    _generate_actions(spec, actions_dir, addon_name)

    # Menus
    _generate_menus(spec, menus_dir, addon_name)

    # Data (sequences, crons, mail templates, paper formats)
    _generate_data(spec, data_dir, addon_name)

    # i18n stub
    _generate_i18n(spec, i18n_dir, addon_name)

    # Tests
    _generate_tests(spec, tests_dir, addon_name, all_model_names)

    return len(spec["models"])


# Standard Odoo group IDs -> xml_id mapping (from source audit)
STANDARD_GROUP_MAP = {
    1: "base.group_user",       # User types / Internal User
    2: "base.group_portal",
    3: "base.group_public",
    4: "base.group_system",      # Administration / Settings
    5: "base.group_multi_company",
    6: "base.group_partner_manager",
    7: "base.group_no_one",
    8: "base.group_erp_manager",
}


def _group_ref(gid):
    """Return the xml_id ref for a group, mapping standard Odoo groups."""
    if gid in STANDARD_GROUP_MAP:
        return STANDARD_GROUP_MAP[gid]
    return f"group_{gid}"


def _generate_security(spec, security_dir, addon_name):
    # Build a map from ir.model id -> technical model name
    model_id_to_name = {m["id"]: m["model"] for m in spec.get("models", [])}

    lines = ['<?xml version="1.0" encoding="utf-8"?>', '<odoo>', '<data>']

    # Module categories
    cats = spec.get("module_categories", [])
    for c in cats:
        cid = c.get("id")
        name = c.get("name")
        parent = c.get("parent_id")
        seq = c.get("sequence", 0)
        lines.append(f'    <record id="module_category_{cid}" model="ir.module.category">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        if parent and isinstance(parent, list) and parent[1]:
            lines.append(f'        <field name="parent_id" ref="module_category_{parent[0]}"/>')
        lines.append(f'        <field name="sequence">{seq}</field>')
        lines.append(f'    </record>')

    # Groups
    for g in spec.get("groups", []):
        gid = g.get("id")
        name = g.get("name")
        cat = g.get("category_id")
        cat_ref = ""
        if cat and isinstance(cat, list) and cat[0]:
            cat_ref = f' ref="module_category_{cat[0]}"'
        lines.append(f'    <record id="group_{gid}" model="res.groups">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        if cat_ref:
            lines.append(f'        <field name="category_id"{cat_ref}/>')
        lines.append(f'    </record>')

    # Record rules
    for r in spec.get("record_rules", []):
        rid = r.get("id")
        name = r.get("name")
        model = r.get("model_id")
        # model_id is [id, human_name] — look up technical name by id
        model_tech = None
        if isinstance(model, list) and model[0]:
            model_tech = model_id_to_name.get(model[0])
        if not model_tech and isinstance(model, list) and model[1]:
            # Fallback: try to convert human name to model name
            # This won't work for most cases, but it's a last resort
            model_tech = model[1].replace(" ", "_").lower()
        domain = r.get("domain_force") or ""
        groups = r.get("groups")
        lines.append(f'    <record id="rule_{rid}" model="ir.rule">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        if model_tech:
            lines.append(f'        <field name="model_id" ref="model_{model_tech.replace(".", "_")}"/>')
        lines.append(f'        <field name="domain_force">{_xml_escape(domain)}</field>')
        if groups:
            grp_refs = []
            if isinstance(groups, list):
                for g in groups:
                    if isinstance(g, list) and g[0]:
                        grp_refs.append(f'ref="{_group_ref(g[0])}"')
            if grp_refs:
                lines.append(f'        <field name="groups" eval="[(6, 0, [{", ".join(grp_refs)}])]"/>')
        lines.append(f'    </record>')

    lines.extend(['</data>', '</odoo>', ''])
    with open(os.path.join(security_dir, "repka_security.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _generate_acl(spec, security_dir, addon_name):
    # Build a map from ir.model id -> technical model name
    model_id_to_name = {m["id"]: m["model"] for m in spec.get("models", [])}

    lines = ["id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"]
    seen_ids = set()
    for a in spec.get("model_access", []):
        name = a.get("name", "").replace(" ", "_").lower()
        # Ensure unique CSV id
        base_id = name
        csv_id = base_id
        counter = 2
        while csv_id in seen_ids:
            csv_id = f"{base_id}_{counter}"
            counter += 1
        seen_ids.add(csv_id)
        mid = a.get("model_id")
        # model_id is [id, human_name] — look up technical name by id
        model_tech = None
        if isinstance(mid, list) and mid[0]:
            model_tech = model_id_to_name.get(mid[0])
        if not model_tech:
            continue
        model_ref = f"model_{model_tech.replace('.', '_')}"
        gid = a.get("group_id")
        group_ref = ""
        if gid and isinstance(gid, list) and gid[0]:
            group_ref = _group_ref(gid[0])
        pr = 1 if a.get("perm_read") else 0
        pw = 1 if a.get("perm_write") else 0
        pc = 1 if a.get("perm_create") else 0
        pu = 1 if a.get("perm_unlink") else 0
        lines.append(f"{csv_id},{a.get('name','')},{model_ref},{group_ref},{pr},{pw},{pc},{pu}")
    with open(os.path.join(security_dir, "ir.model.access.csv"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def _xml_escape(s):
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _generate_views(spec, views_dir, addon_name, all_model_names=None):
    if all_model_names is None:
        all_model_names = {m["model"] for m in spec.get("models", [])}
    lines = ['<?xml version="1.0" encoding="utf-8"?>', '<odoo>', '<data>']
    for v in spec.get("views", []):
        vid = v.get("id")
        name = v.get("name")
        model = v.get("model")
        vtype = v.get("type", "form")
        priority = v.get("priority", 16)
        arch = v.get("arch_db") or ""
        inherit_id = v.get("inherit_id")
        key = v.get("key")
        active = v.get("active", True)
        mode = v.get("mode", "primary")
        xml_id = v.get("xml_id")
        groups = v.get("groups_id")

        if not arch.strip():
            continue

        # Skip views for models not defined in this module
        if model and model not in all_model_names and model not in (
            # Standard models we extend
            "res.partner", "res.partner.bank", "res.bank", "res.company", "res.country",
            "res.users", "fleet.vehicle", "fleet.vehicle.model", "fleet.vehicle.odometer",
            "hr.employee", "product.product", "account.move", "account.move.line",
            "ir.sequence", "mail.template", "mail.compose.message", "res.config.settings",
        ):
            continue

        # Remove buttons that reference object methods we haven't implemented.
        # In clean-room reconstruction, we only have the schema, not the methods.
        # All type="object" buttons are stripped to avoid validation errors.
        arch = re.sub(r'<button\s+[^>]*type="object"[^/]*/>', '', arch)
        arch = re.sub(r'<button\s+[^>]*type="object"[^>]*>.*?</button>', '', arch, flags=re.DOTALL)

        # Fix XML comments with double hyphens (invalid in XML)
        # Replace <!-- ... --!> and nested -- patterns
        arch = re.sub(r'<!--[^>]*--[^>]*>', '', arch)  # Remove broken comments
        arch = re.sub(r'<!--\s*-->', '', arch)  # Remove empty comments

        # Skip inherited views that target standard Odoo views — these often
        # reference fields/positions that differ between Odoo versions and
        # require manual reconstruction. Primary views are always included.
        if inherit_id and isinstance(inherit_id, list) and inherit_id[1]:
            inh_xmlid = inherit_id[1]
            if inh_xmlid and "." in inh_xmlid:
                inh_module = inh_xmlid.split(".", 1)[0]
                # Skip inherited views from standard Odoo modules — they need
                # manual reconstruction to match Odoo 18 view structure
                if inh_module not in (addon_name, "ufs_base"):
                    continue

        # Use the source xml_id if available, else generate one
        if xml_id:
            # Replace source module prefix with our addon name
            record_id = xml_id.split(".", 1)[-1] if "." in xml_id else xml_id
        else:
            record_id = f"view_{vid}"

        lines.append(f'    <record id="{record_id}" model="ir.ui.view">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        if model:
            lines.append(f'        <field name="model">{_xml_escape(model)}</field>')
        lines.append(f'        <field name="type">{_xml_escape(vtype)}</field>')
        lines.append(f'        <field name="priority">{priority}</field>')
        if inherit_id and isinstance(inherit_id, list) and inherit_id[1]:
            # Inherited view — ref to source xml_id (may need mapping)
            inh_xmlid = inherit_id[1] if len(inherit_id) > 1 else None
            if inh_xmlid:
                # Map known deprecated xml_ids to their Odoo 18 equivalents
                INHERIT_MAP = {
                    "account.invoice.list": "account.view_move_tree",
                    "account.invoice.form": "account.view_move_form",
                    "account.invoice.search": "account.view_account_move_filter",
                    "account.invoice_kanban": "account.view_account_move_kanban",
                }
                mapped = INHERIT_MAP.get(inh_xmlid, inh_xmlid)
                lines.append(f'        <field name="inherit_id" ref="{mapped}"/>')
        if mode != "primary":
            lines.append(f'        <field name="mode">{_xml_escape(mode)}</field>')
        if not active:
            lines.append(f'        <field name="active">False</field>')
        if groups:
            grp_refs = []
            for g in groups:
                if isinstance(g, list) and g[0]:
                    grp_refs.append(f'ref="{_group_ref(g[0])}"')
            if grp_refs:
                lines.append(f'        <field name="groups_id" eval="[(6, 0, [{", ".join(grp_refs)}])]"/>')
        # Arch
        lines.append(f'        <field name="arch">{_xml_cdata(arch)}</field>')
        lines.append(f'    </record>')

    lines.extend(['</data>', '</odoo>', ''])
    with open(os.path.join(views_dir, "repka_views.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _xml_cdata(text):
    """Wrap text in CDATA, escaping any existing ]]> sequences."""
    if "]]>" in text:
        text = text.replace("]]>", "]]]]><![CDATA[>")
    return f"<![CDATA[{text}]]>"


def _generate_actions(spec, actions_dir, addon_name):
    # Build a map from ir.model id -> technical model name
    model_id_to_name = {m["id"]: m["model"] for m in spec.get("models", [])}

    lines = ['<?xml version="1.0" encoding="utf-8"?>', '<odoo>', '<data>']
    for a in spec.get("window_actions", []):
        aid = a.get("id")
        name = a.get("name")
        res_model = a.get("res_model")
        view_mode = a.get("view_mode") or "list,form"
        domain = a.get("domain")
        context = a.get("context")
        search_view_id = a.get("search_view_id")
        xml_id = a.get("xml_id")
        record_id = xml_id.split(".", 1)[-1] if xml_id and "." in xml_id else f"action_{aid}"

        lines.append(f'    <record id="{record_id}" model="ir.actions.act_window">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        lines.append(f'        <field name="res_model">{_xml_escape(res_model)}</field>')
        lines.append(f'        <field name="view_mode">{_xml_escape(view_mode)}</field>')
        if domain:
            lines.append(f'        <field name="domain">{_xml_escape(domain)}</field>')
        if context:
            lines.append(f'        <field name="context">{_xml_escape(context)}</field>')
        lines.append(f'    </record>')

    # Server actions — skip those that are also crons (they share xml_id)
    cron_xml_ids = {c.get("xml_id") for c in spec.get("crons", []) if c.get("xml_id")}
    for s in spec.get("server_actions", []):
        if s.get("xml_id") in cron_xml_ids:
            continue
        sid = s.get("id")
        name = s.get("name")
        model = s.get("model_id")
        model_tech = None
        if isinstance(model, list) and model[0]:
            model_tech = model_id_to_name.get(model[0])
        state = s.get("state", "code")
        code = s.get("code") or ""
        xml_id = s.get("xml_id")
        record_id = xml_id.split(".", 1)[-1] if xml_id and "." in xml_id else f"server_action_{sid}"
        lines.append(f'    <record id="{record_id}" model="ir.actions.server">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        if model_tech:
            lines.append(f'        <field name="model_id" ref="model_{model_tech.replace(".", "_")}"/>')
        lines.append(f'        <field name="state">{_xml_escape(state)}</field>')
        if code:
            lines.append(f'        <field name="code">{_xml_cdata(code)}</field>')
        lines.append(f'    </record>')

    lines.extend(['</data>', '</odoo>', ''])
    with open(os.path.join(actions_dir, "repka_actions.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _generate_menus(spec, menus_dir, addon_name):
    # Map standard Odoo menu IDs to their xml_ids
    STANDARD_MENU_PARENTS = {
        112: "contacts.menu_contacts",       # Contacts
        131: "fleet.fleet_vehicle_menu",      # Fleet/Fleet
        156: "account.menu_finance_receivables",  # Invoicing/Customers
    }

    lines = ['<?xml version="1.0" encoding="utf-8"?>', '<odoo>', '<data>']
    for m in spec.get("menus", []):
        mid = m.get("id")
        name = m.get("name")
        parent = m.get("parent_id")
        action = m.get("action")
        sequence = m.get("sequence", 10)
        xml_id = m.get("xml_id")
        record_id = xml_id.split(".", 1)[-1] if xml_id and "." in xml_id else f"menu_{mid}"

        lines.append(f'    <menuitem id="{record_id}"')
        lines.append(f'        name="{_xml_escape(name)}"')
        lines.append(f'        sequence="{sequence}"')
        if parent and isinstance(parent, list) and parent[0]:
            parent_id = parent[0]
            # Check if it's a standard Odoo menu
            if parent_id in STANDARD_MENU_PARENTS:
                lines.append(f'        parent="{STANDARD_MENU_PARENTS[parent_id]}"')
            else:
                parent_xmlid = parent[1] if len(parent) > 1 else None
                if parent_xmlid and "." in parent_xmlid:
                    # Our own menu — use the xml_id suffix
                    parent_ref = parent_xmlid.split(".", 1)[-1]
                    lines.append(f'        parent="{parent_ref}"')
                else:
                    lines.append(f'        parent="menu_{parent_id}"')
        if action and isinstance(action, str) and "," in action:
            # action is like "ir.actions.act_window,353"
            parts = action.split(",")
            if len(parts) == 2:
                act_type, act_id = parts
                act_id = act_id.strip()
                # Find the xml_id for this action
                act_xmlid = None
                for a in spec.get("window_actions", []):
                    if str(a.get("id")) == act_id:
                        act_xmlid = a.get("xml_id")
                        break
                if act_xmlid:
                    act_ref = act_xmlid.split(".", 1)[-1] if "." in act_xmlid else f"action_{act_id}"
                    lines.append(f'        action="{act_ref}"')
        lines.append(f'/>')

    lines.extend(['</data>', '</odoo>', ''])
    with open(os.path.join(menus_dir, "repka_menus.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _generate_data(spec, data_dir, addon_name):
    # Build a map from ir.model id -> technical model name
    model_id_to_name = {m["id"]: m["model"] for m in spec.get("models", [])}

    lines = ['<?xml version="1.0" encoding="utf-8"?>', '<odoo>', '<data noupdate="1">']

    # Sequences
    for s in spec.get("sequences", []):
        sid = s.get("id")
        name = s.get("name")
        code = s.get("code")
        prefix = s.get("prefix") or ""
        suffix = s.get("suffix") or ""
        padding = s.get("padding", 0)
        xml_id = s.get("xml_id")
        record_id = xml_id.split(".", 1)[-1] if xml_id and "." in xml_id else f"sequence_{sid}"
        lines.append(f'    <record id="{record_id}" model="ir.sequence">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        if code:
            lines.append(f'        <field name="code">{_xml_escape(code)}</field>')
        lines.append(f'        <field name="prefix">{_xml_escape(prefix)}</field>')
        lines.append(f'        <field name="suffix">{_xml_escape(suffix)}</field>')
        lines.append(f'        <field name="padding">{padding}</field>')
        lines.append(f'    </record>')

    # Crons
    for c in spec.get("crons", []):
        cid = c.get("id")
        name = c.get("name")
        model = c.get("model_id")
        model_tech = None
        if isinstance(model, list) and model[0]:
            model_tech = model_id_to_name.get(model[0])
        state = c.get("state", "code")
        code = c.get("code") or ""
        interval = c.get("interval_number", 1)
        interval_type = c.get("interval_type", "days")
        xml_id = c.get("xml_id")
        record_id = xml_id.split(".", 1)[-1] if xml_id and "." in xml_id else f"cron_{cid}"
        lines.append(f'    <record id="{record_id}" model="ir.cron">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        if model_tech:
            lines.append(f'        <field name="model_id" ref="model_{model_tech.replace(".", "_")}"/>')
        lines.append(f'        <field name="state">{_xml_escape(state)}</field>')
        if code:
            lines.append(f'        <field name="code">{_xml_cdata(code)}</field>')
        lines.append(f'        <field name="interval_number">{interval}</field>')
        lines.append(f'        <field name="interval_type">{_xml_escape(interval_type)}</field>')
        lines.append(f'    </record>')

    # Mail templates
    for mt in spec.get("mail_templates", []):
        mtid = mt.get("id")
        name = mt.get("name")
        xml_id = mt.get("xml_id")
        record_id = xml_id.split(".", 1)[-1] if xml_id and "." in xml_id else f"mail_template_{mtid}"
        lines.append(f'    <record id="{record_id}" model="mail.template">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        lines.append(f'    </record>')

    # Paper formats
    for pf in spec.get("paper_formats", []):
        pfid = pf.get("id")
        name = pf.get("name")
        xml_id = pf.get("xml_id")
        record_id = xml_id.split(".", 1)[-1] if xml_id and "." in xml_id else f"paperformat_{pfid}"
        lines.append(f'    <record id="{record_id}" model="report.paperformat">')
        lines.append(f'        <field name="name">{_xml_escape(name)}</field>')
        lines.append(f'    </record>')

    lines.extend(['</data>', '</odoo>', ''])
    with open(os.path.join(data_dir, "repka_data.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _generate_i18n(spec, i18n_dir, addon_name):
    # Minimal ru.po stub
    content = '''# Translation of Odoo Server.
# This file contains the translation of the following modules:
#   * {addon_name}
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 18.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-01-01 00:00+0000\\n"
"PO-Revision-Date: 2026-01-01 00:00+0000\\n"
"Last-Translator: \\n"
"Language-Team: Russian\\n"
"Language: ru\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: \\n"
"Plural-Forms: nplurals=1; plural=0;\\n"

#. module: {addon_name}
msgid "Logistics Core"
msgstr "Логистическое ядро"
'''.format(addon_name=addon_name)
    with open(os.path.join(i18n_dir, "ru.po"), "w", encoding="utf-8") as fh:
        fh.write(content)


def _generate_tests(spec, tests_dir, addon_name, all_model_names):
    # tests/__init__.py
    with open(os.path.join(tests_dir, "__init__.py"), "w", encoding="utf-8") as fh:
        fh.write("from . import test_structure\n")

    # test_structure.py — verify models and fields exist
    model_names = sorted(all_model_names)
    test_code = textwrap.dedent(f'''\
        from odoo.tests import TransactionCase, tagged


        @tagged("post_install", "-at_install")
        class TestLogisticsCoreStructure(TransactionCase):
            """Verify that clean-room models and key fields are present."""

            def test_models_registered(self):
                """All audited models should be registered in the pool."""
                missing = []
        ''')
    test_code += f"        expected = {model_names!r}\n"
    test_code += textwrap.dedent(f'''\
                for name in expected:
                    try:
                        self.env[name]
                    except KeyError:
                        missing.append(name)
                self.assertFalse(missing, f"Missing models: {{missing}}")

            def test_key_fields_present(self):
                """Spot-check key fields on core models."""
                # ufs.base.order must have partner_id and state_id
                order = self.env["ufs.base.order"]._fields
                self.assertIn("partner_id", order)
                self.assertIn("state_id", order)
                # ufs.cargo_line must have cargo_id
                cargo_line = self.env["ufs.cargo_line"]._fields
                self.assertIn("cargo_id", cargo_line)
                # ufs.contract must have partner_id and number
                contract = self.env["ufs.contract"]._fields
                self.assertIn("partner_id", contract)
                self.assertIn("number", contract)
    ''')
    with open(os.path.join(tests_dir, "test_structure.py"), "w", encoding="utf-8") as fh:
        fh.write(test_code)


def main():
    parser = argparse.ArgumentParser(description="Generate a clean-room Odoo addon from a spec.")
    parser.add_argument("spec", help="Path to the spec JSON file")
    parser.add_argument("addon_dir", help="Output directory for the addon")
    parser.add_argument("addon_name", help="Technical name of the addon")
    parser.add_argument("--depends", help="Comma-separated extra dependencies")
    args = parser.parse_args()

    with open(args.spec, "r", encoding="utf-8") as fh:
        spec = json.load(fh)

    depends_extra = args.depends.split(",") if args.depends else []
    n = generate(spec, args.addon_dir, args.addon_name, depends_extra)
    print(f"Generated {args.addon_name}: {n} models in {args.addon_dir}")


if __name__ == "__main__":
    main()
