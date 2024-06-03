# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Finanzinterface - Datev ASCII Account Export",
    "version": "17.0.0.0.2",
    "depends": ["syscoon_financeinterface_datev_ascii", "syscoon_partner_accounts"],
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "website": "https://syscoon.com",
    "summary": "Module for exporting DATEV ASCII accounts",
    "description": """The module that export the accounts (standard, debit, credit) to DATEV ASCII.""",
    "category": "Accounting",
    "data": [
        "wizards/syscoon_financeinterface_export.xml",
        "views/res_config_settings.xml",
        "views/syscoon_financeinterface.xml",
    ],
    "installable": True,
    "post_init_hook": "_init_ascii_export_accounts",
    "module_type": "official",
}
