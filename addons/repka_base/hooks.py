def post_init_hook(env):
    language = env["res.lang"].with_context(active_test=False).search([
        ("code", "=", "ru_RU"),
    ], limit=1)
    if language and not language.active:
        env["res.lang"]._activate_lang("ru_RU")
