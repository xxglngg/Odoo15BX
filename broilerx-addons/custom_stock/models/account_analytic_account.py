# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    location_id = fields.Many2one('stock.location', compute='compute_location', inverse='location_inverse')
    location_ids = fields.One2many('stock.location', 'analytic_account_id')

    @api.depends('location_ids')
    def compute_location(self):
        if len(self.location_ids) > 0:
            self.location_id = self.location_ids[0]

    def location_inverse(self):
        if len(self.location_ids) > 0:
            location = self.env['stock.location'].browse(self.stage_ids[0].id)
            location.analytic_account_id = False
        self.location_id.analytic_account_id = self
