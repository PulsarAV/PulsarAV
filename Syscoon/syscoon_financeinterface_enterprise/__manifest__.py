# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Finanzinterface for Enterprise",
    "version": "16.0.0.0.1",
    "depends": [
        "account_accountant",
        "account_reports",
        "l10n_de_reports",
        "syscoon_financeinterface",
    ],
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "website": "https://syscoon.com",
    'summary': 'Changes the main menu entry',
    'description': """Module that changes the main menu entry if enterprise is used.
                      It also removes several entries from the enterprise DATEV export that is not usable.""",
    "category": "Accounting",
    "data": ["views/l10n_de_report_views.xml", "views/syscoon_financeinterface.xml"],
    "active": False,
    "installable": True,
}
