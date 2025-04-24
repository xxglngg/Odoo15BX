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
from odoo.exceptions import ValidationError
import itertools
from operator import itemgetter
import operator
from datetime import datetime, date

class installment_payment(models.TransientModel):
    _name = 'dev.installment.payment'
    _description = 'Installment Payments'
    
    @api.model
    def default_get(self,vals):
        res = super(installment_payment, self).default_get(vals)
        ins_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
        if ins_id:
            invoice_id = ins_id.invoice_id
            if invoice_id:
                if not invoice_id.state == 'posted':
                    raise ValidationError(_('Please Confirm invoice then after create payment.'))
                journal_id = self.env['account.journal'].search([('company_id','=',invoice_id.company_id.id),
                                                                 ('type','in',['bank','cash'])], limit=1)
                res.update({
                    'company_id':ins_id.invoice_id.company_id.id or False,
                    'currency_id':ins_id.invoice_id.currency_id.id or False,
                    'memo':ins_id.invoice_id.name + ' - '+ ins_id.name,
                    'journal_id':journal_id and journal_id.id or False,
                    'invoice_id':invoice_id and invoice_id.id or False,
                    'inst_id':ins_id and ins_id.id or False,
                })
        
        return res
    
    journal_id = fields.Many2one('account.journal', string='Journal', required="1")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.env.company)
    memo = fields.Char('Memo')
    currency_id = fields.Many2one('res.currency', string='Currency')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    inst_id = fields.Many2one('invoice.installment.lines', string='Installment')
    
    def create_payment(self):
        domain = [('payment_type', '=', 'outbound')]
        available_payment_methods = self.env['account.payment.method'].search(domain, limit=1).id
        account = False
        if self.invoice_id.partner_id:
            account = self.invoice_id.partner_id.property_account_receivable_id or False
        vals= {
            'date': self.inst_id.date or date.today(),
            'amount': self.inst_id.payment_amount or 0.0,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'ref': self.memo,
            'journal_id': self.journal_id.id,
            'currency_id': self.invoice_id and self.invoice_id.currency_id.id or False,
            'company_id':self.invoice_id.company_id.id or False,
            'partner_id': self.invoice_id.partner_id.id or False,
            'payment_method_id': available_payment_methods or False,
            'destination_account_id': account and account.id or False,
            'installment_id':self.inst_id and self.inst_id.id or False,
        }
        self.inst_id.state = 'paid'
        payment_id = self.env['account.payment'].create(vals)
        payment_id.action_post()
        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
        payment_lines = payment_id.line_ids.filtered_domain(domain)
        inv_lines = self.invoice_id.line_ids.filtered_domain(domain)
        lines = payment_lines + inv_lines
        lines.reconcile()
        
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
