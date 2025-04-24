# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, UserError, ValidationError
import json

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection([
        ('delivered', 'Regular invoice'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)'),
        ('split', 'Split by SJ')
        ], string='Create Invoice', default='delivered', required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing, \
        according to their invoicing policy (based on ordered or delivered quantity).")
    picking_id = fields.Many2one('stock.picking', string='SJ',)
    picking_domain = fields.Char(compute='_domain_picking_id', readonly=True, store=False,)

    @api.depends('picking_id', )
    def _domain_picking_id(self):
        for rec in self:
            sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

            if sale_orders:
                domain = [('sale_id','in',sale_orders.ids)]
                sj_already_created = sale_orders.invoice_ids.mapped('no_sj')
                if sj_already_created:
                    domain += [('name','not in',sj_already_created)]
            else:
                domain = []
                        
            rec.picking_domain = json.dumps(domain)

    
    def create_invoices_custom(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        if self.advance_payment_method == 'split':
            self.create_invoice_from_sj()
        else:
            self.create_invoices()
        
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _get_line_from_sj(self, order, sj_line):
        invoiceable_lines = []
        for line in sj_line:
            # line_vals = {
            #         'name': line.product_id.name,
            #         'price_unit': line.sale_order_line_id.price_unit,
            #         'quantity': line.product_qty,
            #         'product_id': line.product_id.id,
            #         'product_uom_id': line.sale_order_line_id.product_uom.id,
            #         'tax_ids': [(6, 0, line.sale_order_line_id.tax_id.ids)],
            #         'sale_line_ids': [(6, 0, [line.sale_order_line_id.id])],
            #         'analytic_tag_ids': [(6, 0, line.sale_order_line_id.analytic_tag_ids.ids)],
            #         'analytic_account_id': order.analytic_account_id.id or False,
            # }
            # invoice_item_sequence += 1 sequence=invoice_item_sequence,
            line_vals = line.sale_line_id._prepare_invoice_line(quantity=line.product_qty)
            invoiceable_lines.append((0, 0, line_vals))

        return invoiceable_lines
    
    def create_invoice_from_sj(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
    
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = 0 # Incremental sequencing to keep the lines order on the invoice.
        for order in sale_orders:
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']

            invoice_vals = order._prepare_invoice()
            
            ### add value sj
            invoice_vals['no_sj'] = self.picking_id.name
            invoice_vals['no_po'] = order.no_po_sutomer
            invoice_vals['delivery_date'] = self.picking_id.date_done

            sj_line =  self.picking_id.mapped('move_lines')
            invoice_line_vals = self._get_line_from_sj(order, sj_line)

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves


            

