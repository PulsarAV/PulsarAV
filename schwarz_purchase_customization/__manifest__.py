# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.
{
    "name": "Purchase Customization",
    'summary': "Show moves history on purchase order",
    'description': """
    """,
    'author': 'schwarz',
    'category': 'Inventory/Purchase',
    'version': '17.0.2.0',
    'depends' : [
        'purchase','stock', 'sale', 'project'
    ],
    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}

