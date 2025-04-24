# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from datetime import date, datetime, timedelta, time
from odoo.exceptions import UserError
import base64
import xlrd
import json
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from itertools import groupby

class CreateSplitBillWizard(models.TransientModel):
    _name = "create.split.bill.wizard"
    _description = "Create Split Bill Wizard"

    purchase_id = fields.Many2one('purchase.order')
    picking_ids = fields.Many2one('stock.picking','TTB')
    ttb_ids = fields.Char()
    picking_many_ids = fields.Many2many('stock.picking', 'picking_ids_rel')

    def create_split_bill(self):
        """Create the invoice associated to the PO.
                """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        sequence = 10
        for order in self:
            # if order.invoice_status != 'to invoice':
            #     continue

            # order = order.purchase_id.with_company(order.purchase_id.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = self._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.purchase_id.order_line:

                    picking = self.env['stock.move'].search([('picking_id', '=', order.picking_ids.id)])
                    # if pending_section:
                    quantity = 0
                    for data_picking in picking:
                        if data_picking.product_id.id == line.product_id.id:
                            quantity = data_picking.quantity_done
                            line_vals = line._prepare_account_move_line()
                            if data_picking.product_packaging_id.qty:
                                qty_package = data_picking.product_packaging_id.qty
                                if data_picking.quantity_done > 0:
                                    total = data_picking.quantity_done / qty_package
                                elif data_picking.product_uom_qty > 0:
                                    total = data_picking.product_uom_qty / qty_package
                                else:
                                    total = 0

                            else:
                                total = 0

                            line_vals.update({
                                'quantity': quantity,
                                # 'product_packaging_id': line.product_packaging_id.id,
                                # 'product_packaging_qty': line.product_packaging_qty,
                                # 'total_packaging':total,
                            })
                            line_vals.update({'sequence': sequence})
                            invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                            sequence += 1
                        # pending_section = None
                    # line_vals = line._prepare_account_move_line()
                    # line_vals.update({'sequence': sequence})
                    # invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                    # sequence += 1
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(
                _('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()

        array_flag_create_ttb = []
        array_create_split_bill_split_ttb_bool = []
        array_flag_create_bill = []

        total_ttb = 0
        stock_picking = self.env['stock.picking'].search([('origin', '=', self.purchase_id.name)])
        stock_move = self.env['stock.move.line'].search([('picking_id', 'in', stock_picking.ids)])
        for data_stock_move in stock_move:
            total_ttb = total_ttb + data_stock_move.qty_done

        total_bill = 0
        account_move = self.env['account.move'].search([('invoice_origin', '=', self.purchase_id.name),('state','=','posted')])
        account_move_line = self.env['account.move.line'].search([('move_id', 'in', account_move.ids)])
        for data_account_move_line in account_move_line:
            if data_account_move_line.product_id.id and data_account_move_line.exclude_from_invoice_tab == False:
                total_bill = total_bill + data_account_move_line.quantity

        for order_line in self.purchase_id.order_line:

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
            self.purchase_id.write({
                'flag_create_bill':True
            })
        else:
            self.purchase_id.write({
                'flag_create_bill':False,
                'finish_bill':True,
            })

        if 'True' in array_flag_create_ttb:
            self.purchase_id.write({
                'flag_create_ttb':True,
            })
        else:
            self.purchase_id.write({
                'flag_create_ttb':False,
                'finish_ttb':True,
            })

        return self.purchase_id.action_view_invoice(moves)

    def _prepare_invoice(self):

            """Prepare the dict of values to create the new invoice for a purchase order.
            """
            self.ensure_one()
            move_type = self.purchase_id._context.get('default_move_type', 'in_invoice')
            journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
            if not journal:
                raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.purchase_id.company_id.name, self.purchase_id.company_id.id))

            partner_invoice_id = self.purchase_id.partner_id.address_get(['invoice'])['invoice']
            partner_bank_id = self.purchase_id.partner_id.commercial_partner_id.bank_ids.filtered_domain(['|', ('company_id', '=', False), ('company_id', '=', self.purchase_id.company_id.id)])[:1]
            invoice_vals = {
                'ref': self.purchase_id.partner_ref or '',
                'move_type': move_type,
                'narration': self.purchase_id.notes,
                'currency_id': self.purchase_id.currency_id.id,
                'invoice_user_id': self.purchase_id.user_id and self.purchase_id.user_id.id or self.env.user.id,
                'partner_id': partner_invoice_id,
                'fiscal_position_id': (self.purchase_id.fiscal_position_id or self.purchase_id.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
                'payment_reference': self.purchase_id.partner_ref or '',
                'partner_bank_id': partner_bank_id.id,
                'invoice_origin': self.purchase_id.name,
                'invoice_payment_term_id': self.purchase_id.payment_term_id.id,
                'invoice_line_ids': [],
                'company_id': self.purchase_id.company_id.id,
                'no_po':self.purchase_id.name,
                'no_sj':self.picking_ids.name,
            }
            return invoice_vals


class CreateSplitBillWizardLine(models.TransientModel):
    _name = "create.split.bill.wizard.line"
    _description = "Create Split Bill Wizard Line"


    purchase_order_line_id = fields.Many2one("purchase.order.line")
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
    currency_id = fields.Many2one(
        "res.currency", related="purchase_order_line_id.currency_id"
    )
    # partner_id = fields.Many2one(
    #     "res.partner", related="purchase_order_line_id.address_cust_m2o", string="Customer",
    # )
    taxes_id = fields.Many2many(
        "account.tax", related="purchase_order_line_id.taxes_id"
    )
    
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = (
                line.product_qty - line.qty_invoiced
            )



