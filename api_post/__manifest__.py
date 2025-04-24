# -*- coding: utf-8 -*-
{
    'name': "api_post",

    'summary': "Config and setting value for API POST",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/res_api_key_views.xml',
        'views/external_api_key_views.xml',
        'views/external_api_log_views.xml',
        'views/webhook_api_token_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'api_post/static/src/js/widget_button.js',
        ],

    },
}
