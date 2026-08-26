{
    "name": "Fleet Batteries",
    "summary": "Manage batteries installed in fleet vehicles",
    "version": "18.0.1.1.0",
    "category": "Human Resources/Fleet",
    "license": "LGPL-3",
    "depends": ["fleet"],
    "data": [
        "security/repka_fleet_battery_security.xml",
        "security/ir.model.access.csv",
        "views/fleet_battery_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/fleet_battery_menus.xml",
    ],
    "installable": True,
    "application": False,
}
