# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    "name": "syscoon Partner Debit and Credit Accounts Automation",
    "version": "16.0.0.0.8",
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "category": "Accounting",
    "website": "https://syscoon.com",
    "depends": ["syscoon_partner_accounts"],
    "description": """
If a partner is created, a new debit and credit account will be created automatically.
""",
    'data': [
        'data/automatic_mode.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'active': False,
    'installable': True
}
