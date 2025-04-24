{
    'name': "Custom Purchase",

    'summary': """
        Custom Purchase :
        - CORE MODULE INHERIT FROM PURCHASE
        - add menu pembelian
        - custom report purchase
        - 
        -  
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
    'depends': ['base','purchase','purchase_stock'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'wizards/create_split_bill_wizard_view.xml',
        'wizards/create_split_ttb_wizard_view.xml',
        'views/purchase_order.xml',
        # 'views/purchase_order_line_views.xml',
        # 'reports/paper_format.xml',
        # 'reports/reports.xml',
        # 'reports/purchase_order_report.xml',
        # 'reports/purchase_order_dot_matrix_report.xml'

    ],
    # only loaded in demonstration modes
}
# -*- coding: utf-8 -*-