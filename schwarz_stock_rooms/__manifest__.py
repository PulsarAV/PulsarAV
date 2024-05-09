# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Schwarz Stock Rooms',
    'version' : '1.0',
    'category': 'Services/Project',
    'summary': 'Schwarz Stock Rooms',
    'description': """ Schwarz Stock Rooms""",
    'author': 'schwarz',
    'license' : 'OPL-1',
    'depends' : ['project','stock','sale_stock','purchase'],
    'data': [
        "security/ir.model.access.csv",
        'views/project_rooms.xml',
        'views/project.xml',
        'views/stock_picking.xml',
        'views/stock_lot.xml',
        'views/report_stock_body_print.xml',
        ],
    'assets': {
        'web.assets_backend': [
            'schwarz_stock_rooms/static/src/xml/stock_traceability_report_backend.xml',
        ],
    },
    'installable' : True,
    'auto_install': False,
    'application' : False,
}
