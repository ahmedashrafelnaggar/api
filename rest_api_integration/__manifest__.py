# -*- encoding: utf-8 -*-
{
    "name": "ODOO REST API Integration",
    "version": "1.0.0",
    "category": "Apis, Extra Tools",
    'author': 'Mohamed Mtloob',
    'website': 'https://www.linkedin.com/in/mohamed-mtloob-62b33b76/',
    'license': 'OPL-1',
    'support': 'mohamedmtloob87@gmail.com',

    "summary": "Odoo Rest Api Integration",
    "description": """
        There are URIs available:
        
        /web/session/erp_authenticate  POST    - Login in Odoo and set cookies
        
        /api/<model>                GET     - Read all (with optional domain, fields, offset, limit, order)
        /api/<model>/<id>           GET     - Read one (with optional fields)
        /api/<model>                POST    - Create one
        /api/<model>/<id>           PUT     - Update one
        /api/<model>/<id>           DELETE  - Delete one
        /api/<model>/<id>/<method>  PUT     - Call method (with optional parameters)

    """,
    "depends": ['hr_recruitment','ipmc_bot_custom'],
    "data": [
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
