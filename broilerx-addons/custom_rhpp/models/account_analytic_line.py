# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _description = 'Account Analytic Line Inherit RHPP'

    after_tax = fields.Monetary(string="After Tax", compute='_compute_after_tax')
    is_ovk = fields.Boolean(string="Is Ovk", default=False, compute="_compute_is_ovk")
    qty_terkirim = fields.Float(string="Qty Terkirim", compute="_compute_qty_terkirim")

    @api.depends('amount')
    def _compute_after_tax(self):
        for record in self:
            if record.amount:
                record.after_tax = record.amount + (record.amount * 11/100)
            else:
                record.after_tax = 0.0

    @api.depends('product_id')
    def _compute_is_ovk(self):
        for rec in self:
            if rec.product_id.categ_id.name == 'Obat, Vaksin & Kimia':
                rec.is_ovk = True
            else:
                rec.is_ovk = False
    
    @api.depends('unit_amount')
    def _compute_qty_terkirim(self):
        for rec in self:
            if 'RJSL' in rec.move_id.move_id.name or rec.move_id.move_id.move_type == 'out_refund':
                if rec.unit_amount > 0: 
                    rec.qty_terkirim = -abs(rec.unit_amount)
                else:
                    rec.qty_terkirim = rec.unit_amount
            else:
                rec.qty_terkirim = rec.unit_amount