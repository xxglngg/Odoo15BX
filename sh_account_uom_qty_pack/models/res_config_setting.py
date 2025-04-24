# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    sh_show_bag_size_account_move_line = fields.Boolean(
        "Show Bag Size in Invoice Line")
    sh_show_bag_size_in_account_invoice_report = fields.Boolean(
        "Show Bag Size in Invoice Report")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_show_bag_size_account_move_line = fields.Boolean(
        related="company_id.sh_show_bag_size_account_move_line", string="Show Bag Size in Invoice Line", readonly=False)
    sh_show_bag_size_in_account_invoice_report = fields.Boolean(
        related="company_id.sh_show_bag_size_in_account_invoice_report", string="Show Bag Size in Invoice Report", readonly=False)
