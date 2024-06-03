# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Finanzinterface - Datev XML Export",
    "version": "17.0.0.0.6",
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "category": "Accounting",
    "website": "https://syscoon.com",
    "summary": "Create XML exports that can be imported in DATEV.",
    "external_dependencies": {"python": ["PyPDF2"]},
    "depends": ["syscoon_financeinterface"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/res_config_settings.xml",
        "wizards/syscoon_financeinterface_export.xml",
    ],
    "installable": True,
    "module_type": "official",
}
