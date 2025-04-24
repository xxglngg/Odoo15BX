# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    picking_operation_type = fields.Selection([('cancel', 'Cancel Only'), ('cancel_draft', 'Cancel and Reset to Draft'), ('cancel_delete', 'Cancel and Delete')],
                                               default='cancel',string="Stock Picking Opration Type")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    picking_operation_type = fields.Selection(
                                               string="Stock Picking Opration Type", related="company_id.picking_operation_type", readonly=False)

