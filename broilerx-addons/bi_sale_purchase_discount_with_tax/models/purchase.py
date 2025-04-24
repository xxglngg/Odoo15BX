# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
from itertools import groupby
from odoo.tools.misc import formatLang
import json


class purchase_order(models.Model):
    _inherit = 'purchase.order'
    

    @api.depends('order_line','order_line.price_total','order_line.price_subtotal',\
        'order_line.product_qty','discount_amount',\
        'discount_method','discount_type' ,'order_line.discount_amount',\
        'order_line.discount_method')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        cur_obj = self.env['res.currency']
        for order in self:
            applied_discount = line_discount = sums = order_discount =  amount_untaxed = amount_tax  = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                applied_discount += line.discount_amt
                if line.discount_method == 'fix':
                    line_discount += line.discount_amount
                elif line.discount_method == 'per':
                    line_discount += line.price_subtotal * (line.discount_amount/ 100)
            if res_config:
                if res_config.tax_discount_policy == 'tax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax - line_discount,
                            'discount_amt_line' : line_discount,
                        })
                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00
                        if order.discount_method == 'per':
                            order_discount = amount_untaxed * (order.discount_amount / 100) 
                            
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt' : order_discount,
                            })
                        elif order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt' : order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax ,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax ,
                            })
                elif res_config.tax_discount_policy == 'untax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax - applied_discount,
                            'discount_amt_line' : applied_discount,
                        })
                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00
                        if order.discount_method == 'per':
                            order_discount = amount_untaxed * (order.discount_amount / 100)
                            if order.order_line:
                                for line in order.order_line:
                                    if line.taxes_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = ((order.discount_amount*line.price_subtotal)/100.0)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.taxes_id.compute_all(discount, \
                                                            order.currency_id,1.0, product=line.product_id, \
                                                            partner=order.partner_id)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt' : order_discount,  
                            })
                        elif order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            if order.order_line:
                                for line in order.order_line:
                                    if line.taxes_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = ((order.discount_amount*line.price_subtotal)/amount_untaxed)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.taxes_id._origin.compute_all(discount, \
                                                            order.currency_id,1.0, product=line.product_id, \
                                                            partner=order.partner_id,)
                                        # taxes = line.taxes_id.compute_all(discount, \
                                        #                     order.currency_id,1.0, product=line.product_id, \
                                        #                     partner=order.partner_id)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt' : order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax ,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax ,
                            })
                else:
                    order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax ,
                            })         
            else:
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax ,
                    })

    def _get_discount_id(self):
        self.ensure_one()
        discount_id = False
        if self.discount_amt_line or self.discount_amt:
            purchase_account = self.env['ir.config_parameter'].sudo().get_param('bi_sale_purchase_discount_with_tax.purchase_account_id')
            if purchase_account:
                purchase_account_id = self.env['account.account'].search([('id', '=', purchase_account)])
                if purchase_account_id:
                    discount_id = purchase_account_id
                else:
                    account_id = False
                    account_id = self.env['account.account'].sudo().search(
                        [('user_type_id.name', '=', 'Income'), ('discount_account', '=', True)], limit=1)
                    if not account_id:
                        raise UserError(_('Please define an purchase discount account for this company.'))
                    else:
                        discount_id = account_id.id
        return discount_id

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.partner_ref or '',
            'move_type': move_type,
            'narration': self.notes,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'discount_method': self.discount_method,
            'discount_type' : self.discount_type,
            'discount_amount':self.discount_amount,
            'discount_amt': self.discount_amt,
            'discount_amt_line': self.discount_amt_line,
        }
        return invoice_vals            

    
    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_account_move_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_account_move_line()))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

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
            new_moves = AccountMove.with_company(vals['company_id']).create(vals)
            price = 0
            name = ''
            if new_moves.discount_type == 'line':
                price = vals['discount_amt_line']
            elif new_moves.discount_type == 'global':
                price = vals['discount_amt']
            for line in moves.line_ids:
                name = line.name
            account_discount_id = self._get_discount_id()
            if new_moves.line_ids:
                if name != 'Discount':
                    if account_discount_id:       
                        discount_vals = {
                                'account_id': account_discount_id, 
                                'quantity': 1,
                                'price_unit': -price,
                                'name': "Discount", 
                                'exclude_from_invoice_tab': True,
                                }          
                        new_moves.with_context(check_move_validity=False).write({
                                'invoice_line_ids' : [(0,0,discount_vals)],
                                'discount_account_id': account_discount_id
                            })
            moves |= new_moves

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()
        return self.action_view_invoice(moves)                 

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

        action = self.env.ref('account.action_move_in_invoice_type').sudo()
        result = action.read()[0]
        invoices.write({
            'discount_method' : self.discount_method , 
            'discount_amt' : self.discount_amt,
            'discount_amount' : self.discount_amount ,
            'discount_type' : self.discount_type,
            'discount_amt_line' : self.discount_amt_line,
            'amount_untaxed' : self.amount_untaxed,
            'amount_total': self.amount_total,

        })
        
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

        
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method',default='fix')
    discount_amount = fields.Float('Discount Amount',default=0.0)
    discount_amt = fields.Monetary(compute='_amount_all',store=True,string='- Discount',readonly=True)
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')],string='Discount Applies to',default='global')
    discount_amt_line = fields.Float(compute='_amount_all', string='- Line Discount', digits_compute=dp.get_precision('Line Discount'), store=True, readonly=True)

    def _compute_tax_totals_json(self):
        super(purchase_order, self)._compute_tax_totals_json()
        for rec in self:
            if rec.tax_totals_json:
                tax_totals_json_dict = json.loads(rec.tax_totals_json)
                if rec.discount_type == 'line':
                    subtotal = rec.discount_amt_line + tax_totals_json_dict['amount_total']
                    tax_totals_json_dict.update(
                        {'amount_disc_line_formatted': formatLang(self.env, rec.discount_amt_line, currency_obj=rec.currency_id),
                        'amount_disc_line': rec.discount_amt_line, 
                        'amount_disc_formatted': False,
                        'amount_disc': False,
                        'amount_subtotal': formatLang(self.env, subtotal, currency_obj=rec.currency_id)
                        })
                if rec.discount_type == 'global':
                    subtotal = rec.discount_amt + tax_totals_json_dict['amount_total']
                    tax_totals_json_dict.update(
                        {'amount_disc_line_formatted': False,
                        'amount_disc_line': False, 
                        'amount_disc_formatted': formatLang(self.env, rec.discount_amt, currency_obj=rec.currency_id),
                        'amount_disc': rec.discount_amt,
                        'amount_subtotal': formatLang(self.env, subtotal, currency_obj=rec.currency_id)
                        })
                rec.tax_totals_json = json.dumps(tax_totals_json_dict)

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    discount_method = fields.Selection(
            [('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_type = fields.Selection(related='order_id.discount_type', string="Discount Applies to")
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float('Discount Final Amount')

    @api.depends('product_qty', 'price_unit', 'taxes_id','discount_method','discount_amount','discount_type')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
            if res_config:
                if res_config.tax_discount_policy == 'untax':
                    if line.discount_type == 'line':
                        if line.discount_method == 'fix':
                            price = (vals['price_unit'] * vals['quantity']) - line.discount_amount
                            taxes = line.taxes_id.compute_all(price,vals['currency'],1,vals['product'],vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + line.discount_amount,
                                'price_subtotal': taxes['total_excluded'] + line.discount_amount,
                                'discount_amt' : line.discount_amount,
                            })

                        elif line.discount_method == 'per':
                            price = (vals['price_unit'] * vals['quantity']) * (1 - (line.discount_amount or 0.0) / 100.0)
                            price_x = ((vals['price_unit'] * vals['quantity'])-((vals['price_unit'] * vals['quantity']) * (1 - (line.discount_amount or 0.0) / 100.0)))
                            taxes = line.taxes_id.compute_all(price,vals['currency'],1,vals['product'],vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + price_x,
                                'price_subtotal': taxes['total_excluded'] + price_x,
                                'discount_amt' : price_x,
                            })
                        else:
                            taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency'],vals['quantity'],vals['product'],vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                            })
                    else:
                        taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency'],vals['quantity'],vals['product'],vals['partner'])
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                elif res_config.tax_discount_policy == 'tax':
                    price_x = 0.0
                    if line.discount_type == 'line':
                        taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency'],vals['quantity'],vals['product'],vals['partner'])
                        if line.discount_method == 'fix':
                            price_x = (taxes['total_included']) - (taxes['total_included'] - line.discount_amount)
                        elif line.discount_method == 'per':
                            price_x = (taxes['total_included']) - (taxes['total_included'] * (1 - (line.discount_amount or 0.0) / 100.0))                        

                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                            'discount_amt' : price_x,
                        })
                    else:
                        taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency'],vals['quantity'],vals['product'],vals['partner'])
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                else:
                    taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency'],vals['quantity'],vals['product'],vals['partner'])
                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
            else:
                taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency'],vals['quantity'],vals['product'],vals['partner'])
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    def _prepare_account_move_line(self, move=False):

        res =super(purchase_order_line,self)._prepare_account_move_line(move)
        res.update({'discount_method':self.discount_method,'discount_amount':self.discount_amount,'quantity':self.product_qty})
        return res           
