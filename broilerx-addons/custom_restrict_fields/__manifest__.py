{
    'name': "Custom Restrict Fields",

    'summary': """
        Custom Restring Fields
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
    'depends': ['base','account','purchase','sale'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/restrict_groups.xml',
        # 'security/restrict_rule.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    # only loaded in demonstration modes
}
# -*- coding: utf-8 -*-
