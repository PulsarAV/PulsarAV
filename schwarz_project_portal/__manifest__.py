# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.
{
    'name': "Schwarz Project Portal",
    'summary': "Schwarz Project Portal",
    'description': """Schwarz Project Portal""",
    'version': '1.0',
    'license': 'OPL-1',
    'author': 'schwarz',
    'category': 'Uncategorized',
    'depends': ['project','website','project_enterprise'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'schwarz_project_portal/static/src/js/000.js',
            'schwarz_project_portal/static/src/scss/000.scss',
        ],
    },
}