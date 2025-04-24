# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime

class account_move(models.Model):
    _inherit = 'account.move'
    
    apply_installment = fields.Boolean('Apply Installment', copy=False)
    installment = fields.Integer('Installment', copy=False, default=5)
    down_payment = fields.Monetary('Down Payment', copy=False)
    next_payment_date = fields.Date('Next Payment Date', copy=False)
    installment_amount = fields.Monetary('Installment Amount',compute='_get_installment_amount')
    installment_lines = fields.One2many('invoice.installment.lines','invoice_id', string='Installment Lines')

    @api.constrains('down_payment')
    def check_down_payment(self):
        for move in self:
            if move.down_payment:
                if move.down_payment >= move.amount_total:
                    raise ValidationError(_('Down Payment must be less of amount total.'))
                
    @api.depends('down_payment','amount_total')
    def _get_installment_amount(self):
        for move in self:
            move.installment_amount = move.amount_total - move.down_payment
            

    def generate_installment_lines(self):
        if self.installment_lines:
            self.installment_lines.unlink()
            
        start_date = self.next_payment_date
        pay_amount = self.installment_amount / self.installment
        for i in range(0, self.installment):
            c = i+1
            vals={
                'name':'INS-'+str(c),
                'payment_amount':pay_amount,
                'currency_id':self.currency_id.id,
                'date':start_date,
                'state':'draft',
                'invoice_id':self.id,
            }
            start_date = start_date +relativedelta(months=+1)
            self.env['invoice.installment.lines'].create(vals)
    
    def action_post(self):
        if self.apply_installment and self.installment > 0:
            self.generate_installment_lines()
        return super(account_move, self).action_post()
            

class invoice_installment_lines(models.Model):
    _name = 'invoice.installment.lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Invoice Installment Lines'
    
    invoice_id = fields.Many2one('account.move', string='Invoice', ondelete='cascade', index=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer', related='invoice_id.partner_id', store=True)
    company_id = fields.Many2one('res.company', string='Company', related='invoice_id.company_id', store=True)
    name = fields.Char('Name', copy=False, tracking="1")
    date = fields.Date('Payment Date', tracking="2")
    payment_amount = fields.Monetary('Payment Amount', tracking="2")
    state = fields.Selection([('draft','Draft'),('paid','Paid'),('cancel','Cancel')], default='draft', 
                                    string='State', copy=False, tracking="3")
    currency_id= fields.Many2one('res.currency',string='Currency', related='invoice_id.currency_id')
    payment_count = fields.Integer('Payment', compute='_get_payment_count')
    
    
    @api.depends('state')
    def _get_payment_count(self):
        for line in self:
            payment_id = self.env['account.payment'].search([('installment_id','=',line.id)])
            line.payment_count = len(payment_id)
            
    
    def view_installment_payment(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_payments")
        form_view = [(self.env.ref('account.view_account_payment_form').id, 'form')]
        payment_id = self.env['account.payment'].search([('installment_id','=',self.id)],limit=1)
        if payment_id:
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = payment_id.id
            action['context'] = {'create':0}
            return action
        else:
            action = {'type': 'ir.actions.act_window_close'}
    
    def action_cancel(self):
        self.state = 'cancel'
    
    def action_draft(self):
        self.state = 'draft'
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
