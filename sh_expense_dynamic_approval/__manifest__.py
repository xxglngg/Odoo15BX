# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "Expense Dynamic Approval",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "summary": "Dynamic Expense Approval,Expense Approval Process, Expenses Approval Process,Dynamic Expense Approval,Dynamic Expenses Approval,Expense Multi Approval,Expense Multiple Approval,Expense Double Approval,User Wise Approval,Group Wise Approval Odoo",
    "description": """This module allows you to set dynamic and multi-level approvals in the employee expense so each expense can be approved by many levels. Expense is approved by particular users or groups they get emails notification about the expense that waiting for approval. When the expense approves or rejects employee gets a notification about it.""",
    "version": "15.0.3",
    "depends": ["hr_expense", "bus","sh_base_dynamic_approval"],
    "data": [
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'views/rejection_wizard.xml',
        'views/expense_approval_line.xml',
        'views/expense_approval_config.xml',
        'views/approval_info.xml',
        'views/hr_expense_sheet.xml',
      
        

    ],
    "license": "OPL-1",
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "application": True,
    "price": 30,
    "currency": "EUR"
}
