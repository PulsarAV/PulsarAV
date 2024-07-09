# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Financeinterface",
    "version": "17.0.0.0.5",
    "depends": ["base", "account"],
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "website": "https://syscoon.com",
    "summary": "Main Module for export of accounting moves",
    "description": """The main modul syscoon_financeinterface provides the basic
        methods for finance exports to accounting software.""",
    "category": "Accounting/Accounting",
    "data": [
        "reports/financeinterface_report.xml",
        "security/syscoon_financeinterface_security.xml",
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/analytic_plan_views.xml",
        "views/syscoon_financeinterface.xml",
        "views/res_config_settings.xml",
        "wizards/syscoon_financeinterface_export.xml",
    ],
    "installable": True,
    "module_type": "official",
}
