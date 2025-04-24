# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    analysis_rhpp_count = fields.Integer(compute='_compute_analysis_rhpp_count')

    def _compute_analysis_rhpp_count(self):
        for record in self:
            record.analysis_rhpp_count = self.env['analytic.rhpp'].search_count(
                [('id_mitra', '=', record.id)])
            
    def action_analysis_rhpp(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Analysis RHPP',
            'view_mode': 'tree,form',
            'res_model': 'analytic.rhpp',
            'domain': [('id_mitra', '=', self.id)],
            'context': "{'create': False}"
        }
