# -*- coding: utf-8 -*-
{
    'name': "report_surat_jalan",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "erpana_rio",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['sh_all_one_cancel','custom_reporting_15','om_credit_limit'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/format_paper_surat_jalan.xml',
        'views/template_surat_jalan.xml',
        'views/template_surat_jalan_dot_matrix.xml',
        'views/res_partner_inherit.xml',
        'views/stock_picking_inherit.xml',
        'views/stock_move_inherit.xml',
        'views/product_view_inherit.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [
        #"static/src/xml/add_button_role_user_master_data.xml",
        # "static/src/xml/web_assets_backend_inherit.xml",
    ],
}
