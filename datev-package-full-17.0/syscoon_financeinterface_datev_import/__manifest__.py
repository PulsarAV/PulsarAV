# © 2024 syscoon GmbH (<https://syscoon.com>)
# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Finanzinterface - Datev ASCII Import",
    "version": "17.0.0.0.3",
    "license": "OPL-1",
    "author": "syscoon Estonia OÜ",
    "category": "Accounting/Accounting",
    "website": "https://syscoon.com",
    "description": """The module allows you to import accounting entries.
        Details of the module:
        * Import of accounting entries
        """,
    "summary": "Import of DATEV Moves.",
    "depends": [
        "account",
        "syscoon_financeinterface_datev_ascii",
        "syscoon_partner_accounts",
    ],
    "data": [
        "views/import_datev.xml",
        "views/import_datev_config.xml",
        "views/import_datev_menu.xml",
        "views/account_tax.xml",
        "data/import_config.xml",
        "data/import_datev_sequence.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
