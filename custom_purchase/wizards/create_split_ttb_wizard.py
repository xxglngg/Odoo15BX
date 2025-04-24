# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from datetime import date, datetime, timedelta, time
from odoo.exceptions import UserError
import base64
import xlrd
import json


class CreateSplitTTBWizard(models.TransientModel):
    _name = "create.split.ttb.wizard"
    _description = "Create Split TTB Wizard"

    purchase_id = fields.Many2one('purchase.order')
    partner_id = fields.Many2one('res.partner')
    purchase_line_ids = fields.One2many('create.split.ttb.wizard.line', 'wizard_ttb_id')

    def create_split_ttb(self):

        self_purchase = self.env['purchase.order']
        purchase = self.env['purchase.order'].search([('id', '=', self.purchase_id.id)])
        # purchase_line = self.env['purchase.order.line'].search([('order_id', '=', purchase.id)])
        if self.purchase_line_ids:

            for check_line in self.purchase_line_ids:

                if (check_line.qty_received + check_line.qty) > check_line.product_qty:
                    raise UserError(_("Please Check Qty for SPlit TTB !"))

            for data_purchase_line in self.purchase_line_ids:
                purchase_line = self.env['purchase.order.line'].search(
                    [('id', '=', data_purchase_line.purchase_order_line_id.id)])
                purchase_line.write({
                    'flag_custom_split_sj': True,
                    'qty': data_purchase_line.qty,
                })

            purchase.write({
                'flag_create_ttb': True,
                'state': 'draft',
            })
            purchase.button_confirm()
            purchase.write({
                'state': 'purchase',
                'flag_create_bill': True,
                'flag_receipt_manual':False,
            })

            for data_purchase_line_upt in purchase.order_line:
                remaining = data_purchase_line_upt.remaining_qty
                receive = data_purchase_line_upt.product_qty - remaining

                data_purchase_line_upt.write({
                    'remaining_qty': remaining,
                    # 'qty_received': receive,
                    'flag_custom_split_sj': True,

                })

            array_flag_create_ttb = []
            array_create_split_bill_split_ttb_bool = []
            array_flag_create_bill = []

            total_ttb = 0
            stock_picking = self.env['stock.picking'].search([('origin', '=', purchase.name)])
            stock_move = self.env['stock.move.line'].search([('picking_id', 'in', stock_picking.ids)])
            for data_stock_move in stock_move:
                total_ttb = total_ttb + data_stock_move.qty_done

            total_bill = 0
            account_move = self.env['account.move'].search([('invoice_origin', '=', purchase.name)])
            account_move_line = self.env['account.move.line'].search([('move_id', 'in', account_move.ids)])
            for data_account_move_line in account_move_line:
                total_bill = total_bill + data_account_move_line.quantity

            for order_line in purchase.order_line:

                if order_line.product_qty == total_ttb:
                    array_flag_create_ttb.append('False')
                else:
                    array_flag_create_ttb.append('True')

                # total_bill = order_line.product_qty + order_line.qty

                if order_line.product_qty == total_bill:
                    array_flag_create_bill.append('False')
                else:
                    array_flag_create_bill.append('True')

            if 'True' in array_flag_create_bill:
                purchase.write({
                    'flag_create_bill': True,
                })
            else:
                purchase.write({
                    'flag_create_bill': False,
                    'finish_bill': True,
                })

            if 'True' in array_flag_create_ttb:
                purchase.write({
                    'flag_create_ttb': True,
                })
            else:
                purchase.write({
                    'flag_create_ttb': False,
                    'finish_ttb': True,
                })

        else:
            raise UserError(_("Check purchase line"))


class CreateSplitTTBWizardLine(models.TransientModel):
    _name = "create.split.ttb.wizard.line"
    _description = "Create Split TTB Wizard Line"
    #
    wizard_ttb_id = fields.Many2one('create.split.ttb.wizard')
    purchase_order_line_id = fields.Many2one("purchase.order.line")
    purchase_id = fields.Many2one('purchase.order')
    name = fields.Text(string="Description", readonly=True)
    product_id = fields.Many2one(
        "product.product",
        related="purchase_order_line_id.product_id",
        string="Product",
    )
    product_uom = fields.Many2one(
        "uom.uom",
        related="purchase_order_line_id.product_uom",
        string="Unit of Measure",
    )
    product_qty = fields.Float(
        string="Quantity",
        related="purchase_order_line_id.product_qty",
        digits="Product Unit of Measure",
    )
    qty_invoiced = fields.Float(
        string="In Delivery Quantity",
        related="purchase_order_line_id.qty_invoiced",
        digits="Product Unit of Measure",
    )
    qty_received = fields.Float(
        string="Received Quantity",
        related="purchase_order_line_id.qty_received",
        digits="Product Unit of Measure",
    )
    remaining_qty = fields.Float(
        string="Remaining Quantity",
        compute="_compute_remaining_qty",
        readonly=True,
        digits="Product Unit of Measure",
    )
    qty = fields.Float(
        string="Quantity to Deliver",
        digits="Product Unit of Measure",
        help="This is the quantity taken into account to create the picking",
    )
    price_unit = fields.Float(
        related="purchase_order_line_id.price_unit", readonly=True
    )

    total_remaining_packaging = fields.Float(compute="_get_qty_packaging_remaining")
    qty_packaging = fields.Float()


    #     currency_id = fields.Many2one(
    #         "res.currency", related="purchase_order_line_id.currency_id"
    #     )
    #     # partner_id = fields.Many2one(
    #     #     "res.partner", related="purchase_order_line_id.address_cust_m2o", string="Customer",
    #     # )
    #     taxes_id = fields.Many2many(
    #         "account.tax", related="purchase_order_line_id.taxes_id"
    #     )
    @api.onchange('qty')
    def _get_qty_packaging(self):
        print(self)
        for data in self:
            if data.purchase_order_line_id.product_packaging_id.id and data.purchase_order_line_id.product_packaging_qty:
                check_remaining = data.purchase_order_line_id.product_packaging_qty - (data.qty / data.purchase_order_line_id.product_packaging_id.qty)
                # if check_remaining.is_integer():
                data.qty_packaging = data.qty / data.purchase_order_line_id.product_packaging_id.qty
                # else:
                #     raise UserError(_("Please Check Qty for receive using packaging, contained Qty Receive on packaging :"+ str(self.purchase_order_line_id.product_packaging_id.qty)))
            else:
                data.qty_packaging = 0
    def _get_qty_packaging_remaining(self):
        print(self)
        for data in self:
            if data.purchase_order_line_id.product_packaging_id.id and data.purchase_order_line_id.product_packaging_qty:
                data.total_remaining_packaging = data.purchase_order_line_id.product_packaging_qty - (data.qty_received / data.purchase_order_line_id.product_packaging_id.qty)
            else:
                data.total_remaining_packaging = 0
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = (
                    line.product_qty - line.qty_received
            )
#
#     def _get_procurement_group(self):
#         return self.purchase_order_line_id.order_id.procurement_group_id
#
#     def _prepare_procurement_group_vals(self):
#         return {
#             'name': self.purchase_order_line_id.order_id.name,
#             'move_type': self.purchase_order_line_id.order_id.picking_policy,
#             'purchase_id': self.purchase_order_line_id.order_id.id,
#             'partner_id': self.partner_id.id,
#         }
#
#     def _prepare_stock_moves(self, picking):
#         for rec in self:
#             group_id = self._get_procurement_group()
#             if not group_id:
#                 group_id = self.env['procurement.group'].create(self._prepare_procurement_group_vals())
#                 self.purchase_id.procurement_group_id = group_id
#             else:
#                 # In case the procurement group is already created and the order was
#                 # cancelled, we need to update certain values of the group.
#                 updated_vals = {}
#                 if group_id.partner_id != self.partner_id:
#                     updated_vals.update({'partner_id': self.partner_id.id})
#                 if group_id.move_type != self.purchase_order_line_id.order_id.picking_policy:
#                     updated_vals.update({'move_type': self.purchase_order_line_id.order_id.picking_policy})
#                 if updated_vals:
#                     group_id.write(updated_vals)
#
#             print("group_id", group_id)
#
#             values = {}
#             if rec.qty:
#                 print(picking.purchase_id.commitment_date, picking.purchase_id.date_order, rec.purchase_order_line_id.customer_lead, group_id)
#                 date_deadline = picking.purchase_id.commitment_date or (picking.purchase_id.date_order + timedelta(days=rec.purchase_order_line_id.customer_lead or 0.0))
#                 values = {
#                         'purchase_line_id': rec.purchase_order_line_id.id,
#                         'partner_id': picking.partner_id.id,
#                         'group_id': group_id.id,
#                         'warehouse_id': picking.purchase_id.warehouse_id.id,
#                         'picking_id': picking.id,
#                         'origin': picking.origin,
#                         'date': picking.scheduled_date,
#                         'date_deadline': date_deadline,
#                         'picking_type_id': picking.picking_type_id.id,
#                         'location_id': picking.location_id.id,
#                         'location_dest_id': picking.location_dest_id.id,
#                         'name': rec.purchase_order_line_id.product_id.name,
#                         'description_picking': rec.purchase_order_line_id.product_id.name,
#                         'product_id': rec.purchase_order_line_id.product_id.id,
#                         'product_qty': rec.qty,
#                         'product_uom': rec.product_uom.id,
#                         'price_unit': rec.price_unit or 0.0,
#                 }
#             print("fsfsdsd", values)
#         return values
#
#     def _create_stock_moves(self, picking):
#         values = []
#         for line in self:
#             data = line._prepare_stock_moves(picking)
#             if data:
#                 data["product_qty"] = line.product_uom._compute_quantity(
#                     line.qty, line.product_uom, rounding_method="HALF-UP"
#                 )
#                 values.append(data)
#         return self.env["stock.move"].create(values)
