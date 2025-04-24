{
    'name': "Custom Sale",

    'summary': """
        Custom Sale :
        - CORE MODULE INHERIT FROM SALE
        - add field Complete Address Customer
        - 
        -  
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
    'depends': ['base','sale'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_sj_wiz_view.xml',
        'wizard/sale_make_invoice_advance_views.xml',
        'views/sale_order_inherit_views.xml',
        'wizard/warehouse_sale_wizard_views.xml',
    ],
    # only loaded in demonstration modes
}
# -*- coding: utf-8 -*-
