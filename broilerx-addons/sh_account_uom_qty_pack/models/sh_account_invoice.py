# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class ShCustomerInvoiceLine(models.Model):
    _inherit = "account.move.line"

    sh_bag_qty = fields.Integer("Bag Quantity")
    sh_qty_in_bag = fields.Float(
        related="product_id.sh_qty_in_bag", string="Quantity in Bags")

    @api.onchange("sh_bag_qty")
    def onchange_product_uom_qty_sh(self):
        if self and self.sh_bag_qty > 0:
            self.quantity = self.sh_bag_qty * self.product_id.sh_qty_in_bag


class ShAccountMove(models.Model):
    _inherit = 'account.move'

    sh_enable_quantity = fields.Boolean(
        "Enable Quantity", related="company_id.sh_show_bag_size_account_move_line")
    sh_enable_quantity_in_report = fields.Boolean(
        "Enable Quantity In Report", related="company_id.sh_show_bag_size_in_account_invoice_report"
    )
