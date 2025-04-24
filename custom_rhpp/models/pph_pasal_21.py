# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PPhPasal21(models.Model):
    _name = 'pph.pasal.21'
    _description = 'Setup and Config for PPh Pasal 21 RHPP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    company_id = fields.Many2one('res.company', store=True, copy=False, string="Company", default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency", related='company_id.currency_id', default=lambda self: self.env.user.company_id.currency_id.id)

    name = fields.Char(string='Name', required=True, track_visibility='always')
    lapis = fields.Integer(string='Lapis', required=True)
    pendapatan_min = fields.Monetary(string='Pendapatan Min')
    pendapatan_max = fields.Monetary(string='Pendapatan Max')
    pajak_percentage = fields.Float(string='Pajak %')
