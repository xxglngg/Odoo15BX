# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _compute_invoice(self):
        for order_line in self:
            invoices = order_line.mapped('invoice_lines.move_id')
            order_line.invoice_ids = invoices
            order_line.invoice_count = len(invoices)
    
    invoice_count = fields.Integer(compute="_compute_invoice", string='Bill Count', copy=False, default=0, store=True)
    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills', copy=False, store=True)
    
    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids

        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result

    def _getQtyWaitingDeliver(self):
        for rec in self:
            qty = 0
            # moves = rec.move_ids.filtered(lambda m: m.product_id == rec.product_id and m.state not in ['cancel'])
            moves = rec.order_id.picking_ids.mapped('move_lines').filtered(lambda m: m.product_id == rec.product_id and m.state not in ['cancel'])
            for move in moves:
                qty += move.product_qty
            rec.qty_waiting_deliver = qty
            # rec.remaining_qty = rec.product_uom_qty - rec.qty_delivered - rec.qty_waiting_deliver
            rec.remaining_qty = rec.product_qty - rec.qty_waiting_deliver

    qty_waiting_deliver = fields.Float(string="Qty waiting Deliver", compute=_getQtyWaitingDeliver,
                                       digits="Product Unit of Measure", )
    remaining_qty = fields.Float(
        string="Remaining Quantity",
        compute="_getQtyWaitingDeliver",
        readonly=True,
        digits="Product Unit of Measure",
    )

    flag_finish_bill = fields.Boolean()
    qty = fields.Float(default=0)
    flag_custom_split_sj = fields.Boolean(default=False)

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        if self.flag_custom_split_sj:
            self._check_orderpoint_picking_type()
            product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
            date_planned = self.date_planned or self.order_id.date_planned

            return {
                # truncate to 2000 to avoid triggering index limit error
                # TODO: remove index in master?
                'name': (self.name or '')[:2000],
                'product_id': self.product_id.id,
                'date': date_planned,
                'date_deadline': date_planned,
                'location_id': self.order_id.partner_id.property_stock_supplier.id,
                'location_dest_id': (self.orderpoint_id and not (
                            self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
                'picking_id': picking.id,
                'partner_id': self.order_id.dest_address_id.id,
                'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
                'state': 'assigned',
                'purchase_line_id': self.id,
                'company_id': self.order_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': self.order_id.picking_type_id.id,
                'group_id': self.order_id.group_id.id,
                'origin': self.order_id.name,
                'description_picking': product.description_pickingin or self.name,
                'propagate_cancel': self.propagate_cancel,
                'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
                'product_uom_qty': self.qty,
                'product_uom': product_uom.id,
                # 'product_packaging_id': self.product_packaging_id.id,
                'sequence': self.sequence,
                # 'quantity_done':self.qty,
            }

        else:
            res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
            return res

    def _create_stock_moves(self, picking):
        is_true = 0
        values = []
        for purchase_line in self:
            if purchase_line.flag_custom_split_sj:
                is_true = 1
                if purchase_line.qty > 0:

                    for val in purchase_line._prepare_stock_moves(picking):
                            values.append(val)
                    purchase_line.move_dest_ids.created_purchase_line_id = False

        if is_true == 1:
            return self.env['stock.move'].create(values)
        else:
            res = super(PurchaseOrderLine, self)._create_stock_moves(picking)
            return res



    def _prepare_account_move_line(self, move=False):
        if self.flag_custom_split_sj:
            self.ensure_one()
            aml_currency = move and move.currency_id or self.currency_id
            date = move and move.date or fields.Date.today()
            res = {
                'display_type': self.display_type,
                'sequence': self.sequence,
                'name': '%s: %s' % (self.order_id.name, self.name),
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                # 'quantity': self.qty_to_invoice,
                'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
                'tax_ids': [(6, 0, self.taxes_id.ids)],
                'analytic_account_id': self.account_analytic_id.id,
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                'purchase_line_id': self.id,

            }
            if not move:
                return res

            if self.currency_id == move.company_id.currency_id:
                currency = False
            else:
                currency = move.currency_id

            res.update({
                'move_id': move.id,
                'currency_id': currency and currency.id or False,
                'date_maturity': move.invoice_date_due,
                'partner_id': move.partner_id.id,
            })
            return res
        else:
            # super(PurchaseOrderLine, purchase_line)._prepare_account_move_line(picking)
            return super(PurchaseOrderLine, self)._prepare_account_move_line(move)

    # def _prepare_account_move_line(self, move=False):
    #     res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)

    #     total_packaging = 0.0
    #     if self.product_packaging_qty:
    #         if self.product_packaging_qty > 0:
    #             total_packaging = self.qty_received / self.product_packaging_qty
    #     res.update({
    #         'product_packaging_id': self.product_packaging_id.id,
    #         'product_packaging_qty': self.product_packaging_qty,
    #         'total_packaging':total_packaging,
    #     })
    #     return res