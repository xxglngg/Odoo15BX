# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Invoice Quantity Pack | Bill Quantity Pack | Credit Note Quantity Pack | Debit Note Quantity Pack",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "15.0.1",

    "category": "Accounting",
	
    "license": "OPL-1",

    "summary": "Product Quantity Pack,Bundle Product Quantity,Invoice Bundle Product, Manage Product Package, Product Quantity In Bags,Invoice Products In Bunch, Combo Products Quantity,Bill Product Pack,Credit Note Product Quantity,Debit Note Product Qty Pack Odoo",

    "description": """This module will allow you to assign the product quantity in bags and then when you put bags quantity it will default count total quantity based on bags quantity in invoice/bill/credit note/debit note/payments. If you are selling some products in bulk quantity in the package, pack, bags. For example, a 25kg Sugar bag, so our module useful to add that bag quantity in line and it will auto calculate the final quantity. i,e 5 bags of 25kg sugar bag then auto calculate 125kg in the quantity field. You can hide/show bag size in invoice/bill/credit note/debit note/payments as well hide/show bag size in the reports.""",

    "depends": [
        "account","sh_base_uom_qty_pack",
    ],
    "data": [
        "views/sh_account_invoice_view.xml",
        "report/sh_report_account_invoice_view.xml",
        "views/res_config_setting.xml",
    ],
    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 15,
    "currency": "EUR"
}
