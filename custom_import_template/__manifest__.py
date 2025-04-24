{
    'name': "Custom Import Template",

    'summary': """
        Custom Import Template
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "erpana_team",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations/Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','purchase_stock', 'web', 'base_import'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
    ],
    # only loaded in demonstration modes
    'assets': {'web.assets_backend': ['custom_import_template/static/src/js/import_action.js'], 'web.assets_qweb': ['custom_import_template/static/src/xml/import_buttons.xml']},

}
# -*- coding: utf-8 -*-