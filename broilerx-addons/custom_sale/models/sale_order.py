# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_in_report_sale_order = fields.Char()

    no_po_sutomer = fields.Char(string='No. PO Customer')

    file_po_cust = fields.Binary(string='File PO Customer', attachment=True)
    file_name_po = fields.Char("File Name")

    delivery_company_id = fields.Many2one(comodel_name="res.company", string="Delivery", required=False,default=lambda self: self.env.user.company_id.id)
    da_street = fields.Char(related="delivery_company_id.street")
    da_street2 = fields.Char(related="delivery_company_id.street2")
    da_city = fields.Char(related="delivery_company_id.city")
    da_state_id = fields.Many2one(related="delivery_company_id.state_id")
    da_zip = fields.Char(related="delivery_company_id.zip")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    # bx_warehouse_id = fields.Many2one(
    #     'stock.warehouse', string='Warehouse',
    #     required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, check_company=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, check_company=True)
    incoterm = fields.Many2one('account.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    picking_policy = fields.Selection([
        ('direct', 'As soon as possible'),
        ('one', 'When all products are ready')],
        string='Shipping Policy', required=True, readonly=True, default='direct',
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
        ,help="If you deliver all products at once, the delivery order will be scheduled based on the greatest "
        "product lead time. Otherwise, it will be based on the shortest.")
    effective_date = fields.Datetime("Effective Date", compute='_compute_effective_date', store=True, help="Completion date of the first delivery order.")
    expected_date = fields.Datetime( help="Delivery date you can promise to the customer, computed from the minimum lead time of "
                                          "the order lines in case of Service products. In case of shipping, the shipping policy of "
                                          "the order will be taken into account to either use the minimum or maximum lead time of "
                                          "the order lines.")
    json_popover = fields.Char('JSON data for the popover widget', compute='_compute_json_popover')
    show_json_popover = fields.Boolean('Has late picking', compute='_compute_json_popover')

    # def _prepare_invoice(self, **optional_values):
    #     res = super(SaleOrder, self)._prepare_invoice(**optional_values)
    #     kode_transaksi = False
    #     for rec in self:
    #         if self.env.company.name == 'PT Integrasi Teknologi Unggas':
    #             for line in rec.order_line.mapped('product_id'):
    #                 if line.categ_id.name == 'Obat, Vaksin & Kimia':
    #                     kode_transaksi = '01'
    #                 if line.categ_id.name == 'DOC FS' or line.categ_id.name == 'Live Bird' or line.categ_id.name == 'Starter' or line.categ_id.name == 'Pre Starter' or line.categ_id.name == 'Finisher':
    #                     kode_transaksi = '08'
    #     res.update({
    #         'l10n_id_kode_transaksi': kode_transaksi,
    #     })
    #     return res

    def button_warehouse_wizard(self):
        for rec in self:
            message_id = self.env['warehouse.sale.wizard'].create({
                'message': _("""Apakah anda yakin mengirim barang dari gudang %s ?""" %(rec.warehouse_id.name))})
                
            return {
                'name': _('Warning Message'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'warehouse.sale.wizard',
                'res_id': message_id.id,
                'target': 'new'
            }
    
    @api.constrains('file_po_cust')
    def _check_file(self):
        if self.file_po_cust:
            if str(self.file_name_po.split(".")[1]) != 'pdf':
                raise ValidationError("Cannot upload file different from .pdf file")

    def action_print_quotation_sale_order(self):
        print(self)
        total = 0
        for data_sale_order in self.order_line:
            print(data_sale_order)
            total = total + data_sale_order.product_uom_qty
            date_received = data_sale_order.date_received
            if date_received:
                print(date_received)
                date = date_received.strftime("%d %b %Y")
                print(date)
                data_sale_order.date_receive_another_format = date
        float_total = '{:,.2f}'.format(total)
        self.total_in_report_sale_order = float_total

        return self.env.ref('custom_reporting_15.action_report_sale_order').report_action(self)

    def _getAllProduct(self):
        for rec in self:
            product_arr = []
            if rec.order_line:
                product_arr = rec.order_line.mapped('product_template_id')
            rec.product_ids = product_arr
    
    def _compute_so_line_summary(self):
        for rec in self:
            note = ''
            if rec.order_line:
                note = '\n'.join('[{}] {}: Total Qty ({}), Delivered ({}), Invoiced ({})'.format(line.product_id.default_code, line.product_id.name, line.product_uom_qty, line.qty_delivered, line.qty_invoiced) for line in rec.order_line)
            rec.so_line_summary = note

    product_ids = fields.Many2many('product.template', compute=_getAllProduct, string='All Product')
    so_line_summary = fields.Text(compute=_compute_so_line_summary, readonly=True, store=False, string="Note")

    create_sj_bool = fields.Boolean(compute="_compute_create_sj_bool")
    #### return back picking state to draft ###
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            pickings_to_confirm = rec.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
            if pickings_to_confirm:
                pickings_to_confirm.action_picking_cancel_draft()
    
    def _compute_create_sj_bool(self):
        for rec in self:
            rec.create_sj_bool = False
            if any(line.remaining_qty > 0 for line in self.order_line):
                rec.create_sj_bool = True

    def action_create_sj(self):
        print(self)
        action = self.env.ref('custom_sale.action_create_sj')
        result = action.read()[0]
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _getQtyWaitingDeliver(self):
        for rec in self:
            qty = 0
            # moves = rec.move_ids.filtered(lambda m: m.product_id == rec.product_id and m.state not in ['cancel'])
            moves = rec.order_id.picking_ids.mapped('move_lines').filtered(lambda m: m.product_id == rec.product_id and m.state not in ['cancel'])
            for move in moves:
                qty += move.product_uom_qty
            rec.qty_waiting_deliver = qty
            # rec.remaining_qty = rec.product_uom_qty - rec.qty_delivered - rec.qty_waiting_deliver
            rec.remaining_qty = rec.product_uom_qty - rec.qty_waiting_deliver

    date_received = fields.Date(string='Date Received')
    return_address = fields.Char(string='Address')
    date_receive_another_format = fields.Char()
    get_res_partner_id = fields.Integer(compute="_get_res_partner_id")
    address_cust_m2o = fields.Many2one('res.partner', 'Address Customer',domain="[('commercial_partner_id', '=', get_res_partner_id)]")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', compute="_get_analytic_account")
    note = fields.Char('Note')
    kode_produksi = fields.Char(string='Kode Produksi')
    gudang = fields.Char(string='Gudang')

    @api.depends('order_id.analytic_account_id')
    def _get_analytic_account(self):
        for rec in self:
            rec.analytic_account_id = rec.order_id.analytic_account_id
    qty_waiting_deliver = fields.Float(string="Qty waiting Deliver", compute=_getQtyWaitingDeliver, digits="Product Unit of Measure",)
    remaining_qty = fields.Float(
        string="Remaining Quantity",
        compute="_getQtyWaitingDeliver",
        readonly=True,
        digits="Product Unit of Measure",
    )

    def _update_description(self):
        print(self)
        super()._update_description()
        self.update({'name': ' '})

    @api.onchange('product_template_id')
    def _get_res_partner_id(self):
        print(self)
        self.get_res_partner_id = None
        for data_sale_order_line in self.order_id:
            print(data_sale_order_line)
            if data_sale_order_line.partner_id:
                self.get_res_partner_id = data_sale_order_line.partner_id.id

    # def _prepare_invoice_line(self, **optional_values):
    #     res = super(SaleOrderLine, self)._prepare_invoice_line(
    #         **optional_values
    #     )
    #     res.update({
    #         'product_packaging_id': self.product_packaging_id.id,
    #         'product_packaging_qty': self.product_packaging_qty,
    #     })
    #     return res

    # @api.model
    # def onchange(self, values, field_name, field_onchange, data):
    #     print(self)
    #     print(field_name)
    #     if 'order_id' in field_name:
    #             if field_name['order_id']['partner_id']:
    #                 return {
    #                         'value':
    #                             {
    #                                 'get_res_partner_id': field_name['order_id']['partner_id'],
    #                             }
    #                         }