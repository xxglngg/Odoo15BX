# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class KlausulKontrakLine(models.Model):
    _name = 'klausul.kontrak.line'
    _description = 'Setup and Config for Klausul Kontrak Line RHPP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'klausul'

    klausul = fields.Char('Klausul')
    content = fields.Html('Content')
    klausul_id = fields.Many2one('klausul.kontrak', string='Klausul Kontrak')
