{
    'name': "Custom Reporting",

    'summary': """
        Custom Reporting :
        - Invoice
        - Purchase Order
        - Sales Order 
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "erpana_hanif(Hanifuddiny-hanifuddiny2@gmail.com)",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','custom_sale','purchase', 'stock','product_expiry', 'account'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_users.xml',
        # 'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/account_move.xml',
        'views/res_company.xml',
        'views/stock_picking_view.xml',
        'views/product_product_view.xml',
        'reports/paper_format.xml',
        'reports/payment_voucher_report.xml',
        'reports/reports.xml',
        'reports/sale_order_report.xml',
        'reports/purchase_order_report.xml',
        'reports/invoice_report.xml',
        'reports/bill_report.xml',
        'reports/invoice_report_with_amount_overdue.xml',
        'reports/invoice_report_surat_jalan.xml',
        'reports/sale_report_surat_perintah_muat.xml',
        'reports/spm_report.xml',
        'reports/spj_report.xml',
        'reports/ttb_report.xml',
        'reports/combine_bill_purchase_report.xml',
        'data/config_data.xml',
        'views/res_config_settings.xml',
    ],
    # only loaded in demonstration modes
}
# -*- coding: utf-8 -*-
