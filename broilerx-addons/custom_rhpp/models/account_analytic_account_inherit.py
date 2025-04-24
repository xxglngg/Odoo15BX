# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountAnalyticReportInheritRHPP(models.Model):
    _inherit = 'account.analytic.account'
    _description = 'Account Analytic Report Inherit RHPP'