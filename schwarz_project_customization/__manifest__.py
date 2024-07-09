# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.

{
    "name": "Project Sales Customization",
    'summary': "Show Sale Order history in Poroject view",
    'description': """
    """,
    'author': 'schwarz',
    'category': 'Sales',
    'version': '17.0.1.0',
    'depends' : [
        'sale_project', 'sale_stock'
    ],
    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}

