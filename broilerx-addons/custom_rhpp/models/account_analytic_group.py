# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountAnalyticGroup(models.Model):
    _inherit = 'account.analytic.group'
    _description = 'Account Analytic Group Inherit RHPP'

    unit = fields.Many2one('unit.rhpp', string="Unit", required=True, track_visibility='always')