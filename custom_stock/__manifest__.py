{
    'name': "Custom Stock",

    'summary': """
        Custom Stock :
        - add field ID inventory
        - 
        -  
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "erpana_tio",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock', 'web_domain_field', 'purchase_stock','sale_stock', 'account'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/picking_line_wizard_view.xml',
        'views/stock_picking_inherit_views.xml',
        'views/stock_picking_type_inherit_views.xml',
        'views/stock_quant_inherit_views.xml',
        'views/stock_move_line_inherit_views.xml',
        'views/company_product_rel_views.xml',
        'views/stock_location_inherit_views.xml',
        'views/account_analytic_account_views.xml'
    ],
    # only loaded in demonstration modes
}
# -*- coding: utf-8 -*-
