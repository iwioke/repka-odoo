from pathlib import Path

password = Path("/run/secrets/odoo_admin_password").read_text(encoding="utf-8").strip()
if not password:
    raise RuntimeError("The Odoo administrator password is empty")

values = {"password": password}
if env["res.lang"].search_count([("code", "=", "ru_RU"), ("active", "=", True)]):
    values["lang"] = "ru_RU"
env.ref("base.user_admin").write(values)
env.cr.commit()
