# -*- coding: utf-8 -*-
{
    'name': "Account Payment Report",

    'summary': """
        Module custom for Report Account Payment""",

    'description': """
        Print Voucher Payment
    """,

    'author': "erpana_tio",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_payment','web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/inherit_account_payment.xml',
        'views/format_paper_voucher.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
}
