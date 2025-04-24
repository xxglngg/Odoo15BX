# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##########################################################d####################
{
    'name': 'Invoice Payment Installment, Payment Installments on Invoice',
    'version': '15.0.1.0',
    'sequence':1,
    'description': """
        This module help to make invoice payment by installment.
        
Invoice payment installment management in Odoo
Odoo invoice installment feature
Flexible payment options in Odoo invoices
Managing invoice payments in installments with Odoo
Odoo invoice installment scheduling
Simplifying invoice installment tracking in Odoo
Odoo installment payment module
Streamlining invoice payment plans in Odoo
Odoo invoice installment management best practices
Efficient invoice payment installment system in Odoo
Odoo invoice installment calculation methods
Odoo invoice installment due dates and reminders
Customizing invoice payment installments in Odoo
Odoo invoice installment reporting and analysis
Automating invoice installment processes in Odoo    

odoo app allow to payment installments on invoice screen, invoice payment installment, installment payment report, installment payment reminder notification, invoice emi installment, invoice due amount installment, invoice due date payment installment expiry emi    
        
    """,
    "category": 'Accounting',
    'summary': 'odoo app allow to payment installments on invoice screen, invoice payment installment, installment payment report, installment payment reminder notification, invoice emi installment, invoice due amount installment, invoice due date payment installment expiry emi, partiall invoice payment',  
    'depends': ['sale_management','account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/installment_payment_views.xml',
        'views/account_move_views.xml',
        'views/installment_views.xml',
        'report/installment_report.xml',
        'report/report_menu.xml',
            ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':18.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'license':'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
