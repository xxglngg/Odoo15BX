# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Product Secondary Unit of Measure",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Productivity",
    "summary": """
product secondary uom app, set secondary unit of measure,
manage multiple goods uom odoo, double product uom module""",
    "description": """
Do you have more than one unit of measure in product?
Yes! So, You are at the right palce,
We have created beautiful module to manage secondary
unit of measure in product
It will help you to get easily secondary unit value.
so you don't need to waste your time to calculate that value.
product secondary uom app, set secondary unit of measure,
manage multiple goods uom odoo, double product uom module""",

    "version": "15.0.1",
    "depends": [
                    "product",
                    "stock",
                ],
    "application": True,
    "data": [
            "views/sh_product_custom.xml",
            "views/sh_product_template_custom.xml",
            ],
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": "EUR",
    "images": ['static/description/background.png', ],
    "live_test_url": "https://www.youtube.com/watch?v=KrX_zvlWRdI&feature=youtu.be",
}
