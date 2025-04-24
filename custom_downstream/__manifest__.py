# -*- coding: utf-8 -*-
{
    'name': "BROILERX Downstream",

    'summary': """
        Module Downstream""",

    'description': """
        .
    """,

    'author': "Arief Afandy",
    'license': "AGPL-3",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'BROILERX',
    'version': '15.0.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mrp',
        'stock_landed_costs',
        'mrp',
        'mrp_landed_costs',
        'stock_landed_costs',
        'account',
    ],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizard/mrp_bom_wizard.xml',
        'views/sale_order.xml',
        'views/mrp_bom.xml',
        'views/mrp_production.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
        'views/stock_manifest.xml',
        'views/stock_valuation_layer.xml',
        'views/account.xml',
        'report/stock_manifest.xml',
        'report/stock_quant.xml',
        'report/stock_picking.xml',
        'report/account_move.xml',
        'views/menu.xml',
        'views/product_template.xml',
        'views/sale_order_line.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
}
