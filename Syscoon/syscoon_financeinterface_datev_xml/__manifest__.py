# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Finanzinterface - Datev XML Export",
    "version": "16.0.0.0.11",
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
    "application": False,
}
