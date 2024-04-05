# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Finanzinterface for Enterprise",
    "version": "17.0.0.0.2",
    "depends": [
        "account_accountant",
        "account_reports",
        "l10n_de_reports",
        "syscoon_financeinterface",
    ],
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "website": "https://syscoon.com",
    "summary": "Changes the main menu entry if enterprise is used.",
    "description": """Module that changes the main menu entry if enterprise is used.
                      It also removes several entries from the enterprise DATEV export that is not usable.""",
    "category": "Accounting",
    "data": ["views/l10n_de_report_views.xml", "views/syscoon_financeinterface.xml"],
    "installable": True,
    "module_type": "official",
}
