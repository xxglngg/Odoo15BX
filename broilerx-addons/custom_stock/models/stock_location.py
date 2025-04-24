# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Account Analytic")
    is_peternak = fields.Boolean(string="Is Peternak")
        
    @api.constrains('analytic_account_id')
    def _check_short_code(self):
        self.ensure_one()
        if self.analytic_account_id:
            domain = [
                ('id', '!=', self.id),
                ('analytic_account_id', '=', self.analytic_account_id.id),
            ]
            existing = self.env['stock.location'].search_count(domain)
            if existing:
                raise ValidationError('Analytic account %s already exists in location %s' % (self.analytic_account_id.name, self.name))
