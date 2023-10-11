# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    "name": "syscoon Partner Credit Accounts Automation on Purchase Orders",
    "version": "16.0.0.0.7",
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "category": "Accounting",
    "website": "https://syscoon.com",
    "depends": ["syscoon_partner_accounts_automatic"],
    "description": """
If a purchase order is confirmed, a new credit account will be created automatically.
""",
    'data': [
        'data/automatic_mode.xml',
    ],
    'active': False,
    'installable': True
}
