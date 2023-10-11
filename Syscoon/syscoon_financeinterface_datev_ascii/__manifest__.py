# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'syscoon Finanzinterface - DATEV ASCII Export',
    'version': '16.0.0.0.11',
    'author': 'syscoon Estonia OÜ',
    'license': 'OPL-1',
    'website': 'https://syscoon.com',
    'summary': 'DATEV ASCII Export ',
    'description': """The module account_financeinterface_datev provides the DATEV ASCII Export.""",
    'category': 'Accounting/Accounting',
    'depends': [
        'syscoon_financeinterface',
        'syscoon_partner_accounts',
    ],
    'data': [
        'data/ir_actions_server.xml',
        'views/account_journal.xml',
        'views/account_move_views.xml',
        'views/account_payment_term.xml',
        'views/account_views.xml',
        'views/res_config_settings.xml',
        'views/syscoon_financeinterface.xml',
        'wizards/syscoon_financeinterface_export.xml',
    ],
    'active': False,
    'installable': True,
}
