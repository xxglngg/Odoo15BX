# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Inventory - Secondary Unit of Measure",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Warehouse",
    "summary": """
inventory secondary uom,
stock unit of measure,
delivery incoming order secondary uom Module,
delivery incoming order secondary unit of measure,
inventory unit of measure Odoo
    """,
    "description": """
Do you have more than one unit of measure in the Inventory product?
Yes! So, You are at the right place,
We have created a beautiful module to manage a
secondary unit of measure in Inventory product.
It will help you to get easily secondary unit value.
so you don't need to waste your time to calculate that value.
    """,
    "version": "15.0.1",
    "depends": [
                    "sh_product_secondary",
                ],
    "application": True,
    "data": [
            "security/secondary_unit_group.xml",
            "views/sh_stock_picking_view.xml",
            "views/sh_stock_move_view.xml",
            "views/sh_stock_scrap_view.xml",
            "report/sh_report_stock_picking_operation.xml",
            ],
    "auto_install": False,
    "installable": True,
    "price": 5,
    "currency": "EUR",
    "images": ['static/description/background.png', ]
}
