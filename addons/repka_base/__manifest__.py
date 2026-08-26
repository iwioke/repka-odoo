{
    "name": "РЕПКА: Базовый модуль",
    "summary": "Общие настройки и группы безопасности проекта РЕПКА",
    "version": "18.0.1.1.0",
    "category": "Administration",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/repka_security.xml",
        "security/ir.model.access.csv",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
