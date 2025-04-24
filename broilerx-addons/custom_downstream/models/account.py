# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    qty_secondary = fields.Float(string='Qty Secondary')
    uom_secondary_id = fields.Many2one('uom.uom', string='Secondary UoM')
