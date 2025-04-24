# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _

class payment_installment_report(models.AbstractModel): 
    _name = 'report.dev_invoice_payment_installment.report_pay_ins_tem'
    _description = "Payment Installment Report"

            
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': docs,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
