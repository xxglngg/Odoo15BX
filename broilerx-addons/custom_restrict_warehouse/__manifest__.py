{
    'name': "Custom Restrict Warehouse",

    'summary': """
        Custom Restring Warehouse
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Erpana",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock_sms','stock'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/restrict_groups.xml',
        'security/restrict_rule.xml',
        'views/res_users_views.xml',
    ],
    # only loaded in demonstration modes
}
# -*- coding: utf-8 -*-
