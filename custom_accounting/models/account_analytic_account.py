from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    state = fields.Selection([('unlocked','Unlocked'),('locked','Locked')], default='unlocked', 
                                    string='Status')
    
    def action_lock_analytic_account(self):
        for rec in self:
            rec.write({'state': 'locked'})
    
    def action_unlock_analytic_account(self):
        for rec in self:
            rec.write({'state': 'unlocked'})
