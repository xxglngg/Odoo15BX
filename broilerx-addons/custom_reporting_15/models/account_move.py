from num2words import num2words
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime, date
import json

class AccountMove(models.Model):
    _inherit = 'account.move'

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
                    record.amount_text = record.currency_id.name + ' ' + str(result.capitalize()).upper()

    # invoices = order.mapped('order_line.invoice_lines.move_id')

    def _getAllPO(self):
        for rec in self:
            po_arr = []
            po_name_arr = []
            po_ids = False
            if rec.invoice_line_ids:
                so_line = self.env['sale.order.line'].search([('invoice_lines', 'in', rec.invoice_line_ids.ids)],limit=1)
                po_line = self.env['purchase.order.line'].search([('invoice_lines', 'in', rec.invoice_line_ids.ids)])
                
                if so_line:
                    po_ids = self.env['purchase.order'].search([('origin', '=', so_line.order_id.name)])
                
                # for line in po_line:
                #     if line.order_id.id not in po_arr:
                #         po_arr.append(line.order_id)
                #         po_name_arr.append(line.order_id.name)
            # rec.po_ids = po_arr[0] if po_arr else False
            # print("fdsfdfs", po_arr)
            # print("fdsfdfs", po_name_arr)
            rec.po_ids = po_ids.ids if po_ids else False
            if po_ids:
                note =', '.join([po.name for po in po_ids])
                rec.no_po = note
    
    def _getAllSJ(self):
        for rec in self:
            sj_arr = []
            sj_name_arr = []
            picking_out = False
            if rec.invoice_line_ids:
                so_line = self.env['sale.order.line'].search([('invoice_lines', 'in', rec.invoice_line_ids.ids)],limit=1)
                
                if so_line:
                    picking_ids = self.env['stock.picking'].search([('sale_id', '=', so_line.order_id.id)])
                    picking_out = picking_ids.filtered(lambda l: l.picking_type_id.code == 'outgoing')
                    
                    for picking in picking_out:
                        if picking not in sj_arr:
                            sj_arr.append(picking)
                            sj_name_arr.append(picking.name)
            # print("fdsfdfs", sj_arr)
            # print("fdsfdfs", sj_name_arr)
            rec.sj_ids = picking_out.ids if picking_out else False

            if picking_out:
                note =', '.join([sj.name for sj in picking_out])
                rec.no_sj = note
    
    def _getLicensePlate(self):
        for rec in self:
            plate = None
            if rec.invoice_line_ids:
                so_line = self.env['sale.order.line'].search([('invoice_lines', 'in', rec.invoice_line_ids.ids)],limit=1)
                if so_line:
                    picking_ids = self.env['stock.picking'].search([('sale_id', '=', so_line.order_id.id)])
                    plate = picking_ids
            if plate:
                for lp in plate:
                    value = lp.license_plate
                    rec.no_mobil = value
            else:
                rec.no_mobil = None
    
    def _getBeratKarung(self):
        for rec in self:
            berat = None
            if rec.invoice_line_ids:
                po_line = self.env['purchase.order.line'].search([('invoice_lines', 'in', rec.invoice_line_ids.ids)], limit=1)
                if po_line:
                    picking_ids = self.env['stock.picking'].search([('purchase_id', '=', po_line.order_id.id)])
                    berat = picking_ids
            if berat:
                for bk in berat:
                    rec.berat_karung = bk.berat_karung
            else:
                rec.berat_karung = 0.0
    
    # def _getNettoBrutto(self):
    #     for rec in self:
    #         type_obj = None
    #         if rec.invoice_line_ids:
    #             po_line = self.env['purchase.order.line'].search([('invoice_lines', 'in', rec.invoice_line_ids.ids)], limit=1)
    #             if po_line:
    #                 picking_ids = self.env['stock.picking'].search([('purchase_id', '=', po_line.order_id.id)])
    #                 type_obj = picking_ids
    #         if type_obj:
    #             for nb in type_obj:
    #                 rec.netto_brutto = nb.netto_brutto
    #         else:
    #             rec.netto_brutto = None

    amount_text = fields.Char(string="Terbilang", compute=_amount_to_text, store=False)
    delivery_date = fields.Date(string='Delivery Date')
    no_po = fields.Char(string='No. PO')
    no_sj = fields.Char(string='No. SJ')
    no_mobil = fields.Char(string='No. Mobil', compute=_getLicensePlate)
    company_bank_name = fields.Char(compute="_get_default_bank")
    rekening = fields.Char(compute="_get_default_bank")
    bank_nama_rekening = fields.Char(compute="_get_default_bank")
    company_bank_id = fields.Many2one('res.partner.bank', string='Bank Company')
    atas_nama = fields.Char(string='Atas Nama',compute="_get_default_bank")
    keuangan_user_id = fields.Many2one(comodel_name="res.users", string="Keuangan")
    default_signature = fields.Char(string='Default Signature', compute="_get_default_signature",) # store=True
    default_user_signature = fields.Binary(string="Signature", compute="_get_default_signature",)

    po_ids = fields.Many2many('purchase.order', compute=_getAllPO, string='No. PO')
    sj_ids = fields.Many2many('stock.picking', compute=_getAllSJ, string='No. SJ')
    ### 230207 add by tio compute payment date ###
    payment_date = fields.Char(compute='_compute_payment_date')

    berat_karung = fields.Float(string="Berat Karung", compute=_getBeratKarung)
    # netto_brutto = fields.Selection([
    #     ('netto','Hitung by Netto'),
    #     ('brutto','Hitung by Brutto')], string="Hitung Netto/Brutto", compute=_getNettoBrutto)
    total_cost_price = fields.Float(string="Total Cost Price", compute="_get_total_cost_price")
    # is_company_itu = fields.Boolean('Is Company ITU', compute="_compute_is_company_itu", store=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', compute='_compute_purchase_order', )

    @api.depends('invoice_line_ids.purchase_order_id')
    def _compute_purchase_order(self):
        for bill in self:
            purchase_orders = bill.invoice_line_ids.mapped('purchase_order_id')
            if purchase_orders:
                bill.purchase_order_id = purchase_orders[0]
            else:
                bill.purchase_order_id = False
    
    # @api.depends('company_id')
    # def _compute_is_company_itu(self):
    #     for rec in self:
    #         rec.is_company_itu = False
    #         if rec.company_id.name == 'PT Integrasi Teknologi Unggas':
    #             rec.is_company_itu = True

    # @api.onchange('invoice_line_ids')
    # def _onchange_kode_transaksi(self):
    #     for rec in self:
    #         if rec.invoice_line_ids:
    #             product_line = rec.invoice_line_ids.mapped('product_id')
    #             if product_line.categ_id.name == 'Obat, Vaksin & Kimia':
    #                 rec.l10n_id_kode_transaksi = '01'
    #             if product_line.categ_id.name == 'DOC FS':
    #                 rec.l10n_id_kode_transaksi = '08'
    #             if product_line.categ_id.name == 'Starter' or product_line.categ_id.name == 'Pre Starter' or product_line.categ_id.name == 'Finisher':
    #                 rec.l10n_id_kode_transaksi = '08'
    #             if product_line.categ_id.name == 'Live Bird':
    #                 rec.l10n_id_kode_transaksi = '08'

    @api.depends('invoice_line_ids')
    def _get_total_cost_price(self):
        for rec in self:
            rec.total_cost_price = 0.0
            if len(rec.invoice_line_ids) > 0:
                rec.total_cost_price = sum(x.total_cost_price for x in rec.invoice_line_ids)

    def _compute_payment_date(self):
        for inv in self:
            dates = []
            inv.payment_date = ''
            payments_widget_vals = []
            if inv.state == 'posted' and inv.is_invoice(include_receipts=True):
                payments_widget_vals = inv._get_reconciled_info_JSON_values()
            
            print(payments_widget_vals)
            for data in payments_widget_vals:
                if data['date']:
                    paid_date = datetime.strftime(data['date'], "%m/%d/%Y")
                    dates.append(paid_date)
            
            inv.payment_date = ', '.join(dates)

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     for rec in self:
    #         rec.atas_nama = rec.company_id.name

    def _get_default_signature(self):
        for rec in self:
            rec.default_signature = ''
            rec.default_user_signature = ''
            default_signature = self.env['ir.config_parameter'].sudo().get_param('invoice_signature')
            if default_signature:
                rec.default_signature = default_signature

                signature = self.env['res.users'].search([('name','=', default_signature)])
                if signature:
                    rec.default_user_signature = signature.user_signature

    @api.onchange('company_bank_id')
    def _onchange_company_id(self):
        print(self)
        for rec in self:
            rec.company_bank_name = rec.company_bank_id.display_name
            rec.rekening = rec.company_bank_id.acc_number
            rec.bank_nama_rekening = rec.company_bank_id.bank_id.name
            rec.atas_nama = rec.company_bank_id.acc_holder_name

    def _get_default_bank(self):
        print(self)
        for data in self:
            data.atas_nama = data.company_id.name
            if data.company_bank_id:
                data.company_bank_name = data.company_bank_id.display_name
                data.rekening = data.company_bank_id.acc_number
                data.bank_nama_rekening = data.company_bank_id.bank_id.name
                data.atas_nama = data.company_bank_id.acc_holder_name
            else:
                # if data.company_id.account_bank:
                #     data.company_bank_name = data.company_id.account_bank.display_name
                #     data.rekening = data.company_id.account_bank.acc_number
                #     data.bank_nama_rekening = data.company_id.account_bank.bank_id.name
                #     data.atas_nama = data.company_id.account_bank.acc_holder_name
                # else:
                data.company_bank_name = ''
                data.rekening = ''
                data.bank_nama_rekening = ''
                data.atas_nama = ''
    


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _getSourceLocation(self):
        for rec in self:
            location = None
            if rec.move_id.invoice_line_ids:
                so_line = self.env['sale.order.line'].search([('invoice_lines', 'in', rec.move_id.invoice_line_ids.ids)],limit=1)
                if so_line:
                    picking_ids = self.env['stock.picking'].search([('sale_id', '=', so_line.order_id.id)])
                    location = picking_ids
            if location:
                for loc in location:
                    value = loc.location_id.location_id.name
                    rec.gudang = str(value)
            else:
                rec.gudang = None

    note = fields.Char(string='Note')
    total_karung = fields.Integer(string="Total Karung", readonly=True)
    potong_karung = fields.Float(string="Total Potong Karung", readonly=True)
    profit_weight = fields.Float(string="Total Netto", readonly=True)
    gross_weight = fields.Float(string="Total Brutto", readonly=True)
    susut = fields.Float(string="Susut", readonly=True)
    total_berat = fields.Float(string="Total Berat", readonly=True)
    berat = fields.Float(string='Berat (Kg)')
    kode_produksi = fields.Char(string='Kode Produksi')
    gudang = fields.Char(string='Gudang', compute=_getSourceLocation, readonly=False)

    cost_price = fields.Float(string="Cost")
    total_cost_price = fields.Float(string="Total Cost", compute="_compute_total_cost_price")
    jumlah_ekoran = fields.Float(string="Jumlah Ekoran")

    @api.onchange('product_id')
    def _onchange_product_id_cost_price(self):
         for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue
            line.cost_price = line.product_id.standard_price
    
    @api.onchange('product_uom_id')
    def _onchange_uom_id_cost_price(self):
        if self.display_type in ('line_section', 'line_note'):
            return
        self.cost_price = self.product_id.standard_price
    
    @api.depends('quantity', 'cost_price')
    def _compute_total_cost_price(self):
        for rec in self:
            rec.total_cost_price = 0.0
            if rec.quantity != 0 and rec.cost_price != 0:
                rec.total_cost_price = rec.quantity * rec.cost_price

    # def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
    #     self.ensure_one()
    #     return self._get_price_total_and_subtotal_model(
    #         price_unit=self.price_unit if price_unit is None else price_unit,
    #         quantity=self.total_berat if quantity is None else quantity,
    #         discount=self.discount if discount is None else discount,
    #         currency=self.currency_id if currency is None else currency,
    #         product=self.product_id if product is None else product,
    #         partner=self.partner_id if partner is None else partner,
    #         taxes=self.tax_ids if taxes is None else taxes,
    #         move_type=self.move_id.move_type if move_type is None else move_type,
    #     )