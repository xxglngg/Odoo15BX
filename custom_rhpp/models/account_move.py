# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    
    analytic_rhpp_id = fields.Many2one('analytic.rhpp.', string="Analytic RHPP")
