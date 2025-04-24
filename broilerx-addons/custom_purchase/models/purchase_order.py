# -*- coding: utf-8 -*-
from num2words import num2words

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo import api, fields, models, SUPERUSER_ID, _
from num2words import num2words
import json

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {}

    create_split_bill_split_ttb_bool = fields.Boolean(compute="_compute_split_ttb_split_bill_bool")
    finish_ttb = fields.Boolean(default=False)
    finish_bill = fields.Boolean(default=False)
    # date_order = fields.Datetime('Order Deadline', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Datetime.now,
    #     help="Depicts the date within which the Quotation should be confirmed and converted into a purchase order.")
    # date_approve = fields.Datetime('Confirmation Date', readonly=False, index=True, copy=False)
    # check_group_user = fields.Boolean(compute='compute_group_user')

    # def compute_group_user(self):
    #     print(self)
    def _compute_split_ttb_split_bill_bool(self):
        array_flag_create_ttb = []
        array_create_split_bill_split_ttb_bool = []
        array_flag_create_bill = []
        for rec in self:
            total_ttb = 0
            stock_picking = self.env['stock.picking'].search([('origin', '=', rec.name)])
            stock_move = self.env['stock.move.line'].search([('picking_id','in',stock_picking.ids)])
            for data_stock_move in stock_move:
                total_ttb = total_ttb + data_stock_move.qty_done

            total_bill = 0
            account_move = self.env['account.move'].search([('invoice_origin', '=', rec.name),('state','=','posted')])
            account_move_line = self.env['account.move.line'].search([('move_id', 'in', account_move.ids)])
            for data_account_move_line in account_move_line:
                if data_account_move_line.product_id.id and data_account_move_line.exclude_from_invoice_tab == False:
                    total_bill = total_bill + data_account_move_line.quantity

            for order_line in rec.order_line:

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
                rec.flag_create_bill = True
            else:
                rec.flag_create_bill = False
                rec.finish_bill = True

            if 'True' in array_flag_create_ttb:
                rec.flag_create_ttb = True
            else:
                rec.flag_create_ttb = False
                rec.finish_ttb = True

            rec.create_split_bill_split_ttb_bool = None

    @api.depends('partner_id', 'delivery_address_id')
    def _compute_cp_domain(self):
        for rec in self:
            domain = [('type', 'in', ['contact'])]
            partner_ids = []
            quant_domain = []
            if rec.delivery_address_id:
                domain += [('parent_id', '=', rec.delivery_address_id.id)]
            elif rec.partner_id:
                domain += [('parent_id', '=', rec.partner_id.id)]

            rec.cp_domain = json.dumps(domain)

    @api.depends('amount_total')
    def _amount_to_text(self):
        for record in self:
            record.amount_text = ''
            if record.amount_total:
                value = round(record.amount_total)
                result = num2words(value, lang="id")
                if record.currency_id.name == 'IDR':
                    amount_txt = str(result.capitalize()).upper() + ' RUPIAH'
                    # txt = amount_txt.replace("KOMA NOL", "")
                    record.amount_text = amount_txt
                else:
                    record.amount_text = record.currency_id.name + ' ' + str(result.capitalize())

    amount_text = fields.Char(string="Terbilang", compute=_amount_to_text, store=False)
    
    no_pr = fields.Char(string="PR No",)
    no_sr = fields.Char(string="SR No",)

    date_valid = fields.Datetime('Valid until', copy=False)

    # purchase_user_id = fields.Many2one(comodel_name="res.users", string="Purchasing", required=False, )
    # manager_user_id = fields.Many2one(comodel_name="res.users", string="Manager Unit", required=False, )
    # finance_user_id = fields.Many2one(comodel_name="res.users", string="GM Finance & Accounting", required=False, )
    warehouse_manager_id = fields.Many2one(comodel_name="res.users", string="Warehouse Logistic Procurement Manager", required=False, )

    delivery_address_id = fields.Many2one(comodel_name="res.partner", string="Delivery", required=False,)
    da_street = fields.Char(related="delivery_address_id.street", readonly=True)
    da_street2 = fields.Char(related="delivery_address_id.street2", readonly=True)
    da_city = fields.Char(related="delivery_address_id.city", readonly=True)
    da_state_id = fields.Many2one(related="delivery_address_id.state_id", readonly=True)
    da_zip = fields.Char(related="delivery_address_id.zip", readonly=True)

    cp_id = fields.Many2one(comodel_name="res.partner", string="CP Vendor",)
    cp_domain = fields.Char(
       compute="_compute_cp_domain",
       readonly=True,
       store=False,)
    
    # cp = fields.Char(string="Contact Person", required=False, )
    cp_name = fields.Char(string="CP Vendor", related="cp_id.name", readonly=True)
    cp_phone = fields.Char(string="Phone", related="cp_id.phone", readonly=True)
    cp_email = fields.Char(string="Email", related="cp_id.email", readonly=True)

    flag_create_bill = fields.Boolean()
    flag_create_ttb = fields.Boolean(default='False')

    ttb_ids = fields.Char(compute='_compute_get_all_ttb')

    picking_many_ids = fields.Many2many('stock.picking', 'picking_ids_rel',compute='compute_picking_ids')
    flag_receipt_manual = fields.Boolean()
    def compute_picking_ids(self):
        stock_picking = self.env['stock.picking'].search([('origin', '=', self.name), ('state', '=', 'done')])
        value = []
        arr = []
        if stock_picking:
            for value_stock_picking in stock_picking:
                value.append(value_stock_picking.name)
            check_bill = self.env['account.move'].search([('no_po', '=', self.name)])
            if len(check_bill.ids) > 1:
                for data_bill in check_bill:
                    if data_bill.no_sj in value:
                        sj_stock_picking = self.env['stock.picking'].search(
                            [('name', '=', data_bill.no_sj), ('state', '=', 'done')])
                        arr.append(sj_stock_picking.id)
                self.picking_many_ids = arr
            else:
                self.picking_many_ids = stock_picking.ids
        else:
            self.picking_many_ids = None

    def _compute_get_all_ttb(self):
        stock_picking = self.env['stock.picking'].search([('origin', '=', self.name), ('state', '=', 'done')])
        value = []
        arr = []
        if stock_picking:
            for value_stock_picking in stock_picking:
                value.append(value_stock_picking.name)
            check_bill = self.env['account.move'].search([('no_po', '=', self.name)])
            if len(check_bill.ids) > 1:
                for data_bill in check_bill:
                    if data_bill.no_sj in value:
                        sj_stock_picking = self.env['stock.picking'].search([('name', '=', data_bill.no_sj), ('state', '=', 'done')])
                        arr.append(sj_stock_picking.id)
                self.ttb_ids = arr
            else:
                self.ttb_ids = stock_picking.ids
        else:
            self.ttb_ids = None

    def button_confirm(self):
        print(self)
        self.flag_receipt_manual = True
        res = super(PurchaseOrder, self).button_confirm()
        return res

    # def sh_cancel(self):
    #     res = super(PurchaseOrder, self).sh_cancel()
    #     self.flag_receipt_manual = False
    #     self.finish_ttb = False
    #     return res

    def button_confirm_split(self):
        self.flag_receipt_manual = False
        self.finish_ttb = False
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True


    # REPLACE FUNGSI PICKING DARI PO
    def _create_picking(self):
        if self.flag_receipt_manual is True:
            StockPicking = self.env['stock.picking']
            for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
                if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
                    order = order.with_company(order.company_id)

                    res = order._prepare_picking()
                    picking = StockPicking.with_user(SUPERUSER_ID).create(res)

                    moves = order.order_line._create_stock_moves(picking)

                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': picking, 'origin': order},
                                                   subtype_id=self.env.ref('mail.mt_note').id)
                    # picking.sh_cancel()
            return True

        if self.finish_ttb:
            StockPicking = self.env['stock.picking']
            for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
                if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
                    order = order.with_company(order.company_id)

                    res = order._prepare_picking()
                    picking = StockPicking.with_user(SUPERUSER_ID).create(res)


                    moves = order.order_line._create_stock_moves(picking)

                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': picking, 'origin': order},
                                                   subtype_id=self.env.ref('mail.mt_note').id)
                    # picking.sh_cancel()
            return True
        else:
            self.finish_ttb = True

    def action_create_split_ttb(self):
        for data_purchase_line in self.order_line:
            data_purchase_line.write({
                'qty':0
            })
        get_wizard_split_ttb = self.env['create.split.ttb.wizard'].create({
            'purchase_id':self.id,
            'partner_id':self.partner_id.id,
        })
        for order_line in self.order_line:
            get_create_split_ttb_wizard_line = self.env['create.split.ttb.wizard.line'].create({
                'wizard_ttb_id':get_wizard_split_ttb.id,
                'purchase_order_line_id':order_line.id,
                'purchase_id':self.id,
                'name':order_line.product_id.name,
                'product_id':order_line.product_id.id,
                'product_qty':order_line.product_qty,
                'qty_invoiced':order_line.qty_invoiced,
                'qty_received':order_line.qty_received,
                'remaining_qty':order_line.remaining_qty,
                'qty':order_line.qty,
                'price_unit':order_line.price_unit,
                'product_uom':order_line.product_uom.id,
            })


        return {
            'name': "Split TTB",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.split.ttb.wizard',
            'view_id': self.env.ref('custom_purchase.view_create_split_ttb_wizard').id,
            'context':{
                'default_purchase_id': get_wizard_split_ttb.purchase_id.id,
                'default_partner_id': get_wizard_split_ttb.partner_id.id,
                'default_purchase_line_ids': get_wizard_split_ttb.purchase_line_ids.ids,

            },
            'target': 'new',
        }

    def action_create_split_bill(self):
        stock_picking = self.env['stock.picking'].search([('origin', '=', self.name), ('state', '=', 'done')])
        value = []
        arr = []
        if stock_picking:
            for value_stock_picking in stock_picking:
                value.append(value_stock_picking.name)
            check_bill = self.env['account.move'].search([('no_sj', 'in', value)])
            if len(check_bill.ids) > 0:
                for data_bill in check_bill:
                    value.remove(data_bill.no_sj)
                sj_stock_picking = self.env['stock.picking'].search([('name', 'in', value), ('state', '=', 'done')])
                ttb_ids = sj_stock_picking.ids
            else:
                ttb_ids = stock_picking.ids
        else:
            ttb_ids = None

        get_wizard_split_bill = self.env['create.split.bill.wizard'].create({
            'purchase_id': self.id,
            'ttb_ids': ttb_ids,
            'picking_many_ids':ttb_ids,
        })

        return {
            'name': "Split Bill",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.split.bill.wizard',
            'view_id': self.env.ref('custom_purchase.view_create_split_bill_wizard').id,
            'context': {
                'default_purchase_id': get_wizard_split_bill.purchase_id.id,
                'default_ttb_ids':get_wizard_split_bill.ttb_ids,
                'default_picking_many_ids':get_wizard_split_bill.picking_many_ids.ids,
            },
            'target': 'new',
        }


