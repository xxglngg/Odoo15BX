# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import api, fields, models, _

class InvoicePaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def cancel_due_installments(self, invoice_ids):
        for line_id in invoice_ids:
            installment_ids = self.env['invoice.installment.lines'].search([('invoice_id', '=', line_id.id), ('state', '=', 'draft')])
            if installment_ids:
                for line_id in installment_ids:
                    line_id.action_cancel()

    def action_create_payments(self):
        res = super().action_create_payments()
        invoice_ids = self.env['account.move'].browse(self._context.get('active_ids'))
        if invoice_ids:
            self.cancel_due_installments(invoice_ids)
        return res
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
