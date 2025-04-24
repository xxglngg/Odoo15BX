{
    'name': "Custom Approvals",

    'summary': """
        Custom Approvals :
        - add kanban view for mobile
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
    'depends': ['base','approvals'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
        'views/approval_product_line_inherit_views.xml',
    ],
    # only loaded in demonstration modes
}
# -*- coding: utf-8 -*-
