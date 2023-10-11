# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Financeinterface",
    "version": "16.0.0.0.10",
    "depends": ["account", "hr_expense"],
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "website": "https://syscoon.com",
    "summary": "Main Module for export of accounting moves",
    "description": """The main modul syscoon_financeinterface provides the basic
        methods for finance exports to accounting software.""",
    'category': 'Accounting/Accounting',
    'data': [
        'data/syscoon_financeinterface_sequence.xml',
        'reports/financeinterface_report.xml',
        'security/syscoon_financeinterface_security.xml',
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/analytic_plan_views.xml',
        'views/syscoon_financeinterface.xml',
        'views/res_config_settings.xml',
        'wizards/syscoon_financeinterface_export.xml'
    ],
    "active": False,
    "installable": True,
}
