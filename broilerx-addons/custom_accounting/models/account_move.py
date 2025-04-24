from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.tools import float_round, float_repr
from odoo.tools.misc import formatLang

import ast
import re
import json
import base64
from collections import defaultdict


FK_HEAD_LIST = ['FK', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK', 'TAHUN_PAJAK', 'TANGGAL_FAKTUR', 'NPWP', 'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN', 'JUMLAH_PPNBM', 'ID_KETERANGAN_TAMBAHAN', 'FG_UANG_MUKA', 'UANG_MUKA_DPP', 'UANG_MUKA_PPN', 'UANG_MUKA_PPNBM', 'REFERENSI', 'KODE_DOKUMEN_PENDUKUNG']

LT_HEAD_LIST = ['LT', 'NPWP', 'NAMA', 'JALAN', 'BLOK', 'NOMOR', 'RT', 'RW', 'KECAMATAN', 'KELURAHAN', 'KABUPATEN', 'PROPINSI', 'KODE_POS', 'NOMOR_TELEPON']

OF_HEAD_LIST = ['OF', 'KODE_OBJEK', 'NAMA', 'HARGA_SATUAN', 'JUMLAH_BARANG', 'HARGA_TOTAL', 'DISKON', 'DPP', 'PPN', 'TARIF_PPNBM', 'PPNBM']

def _csv_row(data, delimiter=',', quote='"'):
    return quote + (quote + delimiter + quote).join([str(x).replace(quote, '\\' + quote) for x in data]) + quote + '\n'

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    total_line_product = fields.Integer(string="Total Product", compute="_compute_total_line_product", store=True)
    no_invoice = fields.Char(string="No Invoice")
    no_efaktur = fields.Char(string="Nomor Faktur Pajak")
    analytic_account_assist = fields.Boolean('Analytic Account Assist')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',check_company=True)
    # tax_assist = fields.Boolean('Tax Assist')
    # tax_ids = fields.Many2many(
    #     comodel_name='account.tax',
    #     string="Taxes",
    #     check_company=True,
    #     help="Taxes that apply on the base amount")
    payment_paid = fields.Char(compute='_compute_payment_amount', string="Payment Paid")
    payment_name = fields.Char(compute='_compute_payment_amount', string="Payment Name")
    payment_journal = fields.Char(compute='_compute_payment_amount', string="Payment Journal")
    data_timbang = fields.Binary(string="Data Timbang", attachment=True, tracking=True)
    file_data_timbang = fields.Char(string="Data Timbang", tracking=True)

    @api.constrains('no_efaktur')
    def _check_no_efaktur(self):
        for record in self:
            if record.no_efaktur:
                if not record.no_efaktur.isdigit():
                    raise ValidationError("Nomor faktur pajak hanya boleh berisi angka.")
    
    @api.depends('invoice_line_ids')
    def _compute_total_line_product(self):
        for rec in self:
            rec.total_line_product = 0
            if rec.invoice_line_ids:
                if len(rec.invoice_line_ids) > 0:
                    invoice_line_ids = rec.invoice_line_ids.filtered(lambda x : x.product_id != False)
                    rec.total_line_product = len(invoice_line_ids)
    
    @api.onchange('analytic_account_assist', 'analytic_account_id')
    def _onchange_analytic_account_assist(self):
        for rec in self:
            if not rec.analytic_account_assist:
                rec.analytic_account_id = False
                if len(rec.invoice_line_ids) > 0:
                    rec.invoice_line_ids.analytic_account_id = False
            else:
                if len(rec.invoice_line_ids) > 0:
                    rec.invoice_line_ids.analytic_account_id = False
                    rec.invoice_line_ids.analytic_account_id = rec.analytic_account_id

    # @api.onchange('tax_assist', 'tax_ids')
    # def _onchange_tax_assist(self):
    #     for rec in self:
    #         if not rec.tax_assist:
    #             rec.tax_ids = False
    #             if len(rec.invoice_line_ids) > 0:
    #                 rec.invoice_line_ids.write({'tax_ids': False})
    #                 rec._onchange_tax_totals_json()
    #         else:
    #             if len(rec.invoice_line_ids) > 0:
    #                 rec.invoice_line_ids.write({'tax_ids': rec.tax_ids})
    #                 rec._onchange_tax_totals_json()
                    
    def _compute_payment_amount(self):
        for inv in self:
            payment_paid = []
            payment_journal = []
            payment_name = []
            inv.payment_paid = ''
            inv.payment_journal = ''
            inv.payment_name = ''
            payments_widget_vals = []
            if inv.state == 'posted' and inv.is_invoice(include_receipts=True):
                payments_widget_vals = inv._get_reconciled_info_JSON_values()
            
            for data in payments_widget_vals:
                if data['amount']:
                    amount = '{:,.2f}'.format(data['amount'])
                    payment_paid.append(amount)
                if data['journal_name']:
                    payment_journal.append(data['journal_name'])
                if data['account_payment_id']:
                    payment_id = self.env['account.payment'].search([('id', '=', data['account_payment_id'])])
                    payment_name.append(payment_id.name)
                else:
                    payment_name.append(data['ref'])
            
            inv.payment_paid = ', '.join(payment_paid)
            inv.payment_journal = ', '.join(payment_journal)
            inv.payment_name = ', '.join(payment_name)
    
    def _generate_efaktur_invoice(self, delimiter):
        """Generate E-Faktur for customer invoice."""
        # Invoice of Customer
        dp_product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')

        output_head = '%s%s%s' % (
            _csv_row(FK_HEAD_LIST, delimiter),
            _csv_row(LT_HEAD_LIST, delimiter),
            _csv_row(OF_HEAD_LIST, delimiter),
        )

        for move in self.filtered(lambda m: m.state == 'posted'):
            eTax = move._prepare_etax()

            commercial_partner = move.partner_id.commercial_partner_id
            nik = str(commercial_partner.l10n_id_nik) if not commercial_partner.vat else ''

            if move.l10n_id_replace_invoice_id:
                number_ref = str(move.l10n_id_replace_invoice_id.name) + " replaced by " + str(move.name) + " " + nik
            elif nik:
                number_ref = str(move.name) + " " + nik
            else:
                number_ref = str(move.name)

            street = ', '.join([x for x in (move.partner_id.street, move.partner_id.street2) if x])

            invoice_npwp = ''
            if commercial_partner.vat and len(commercial_partner.vat) >= 15:
                invoice_npwp = commercial_partner.vat
            elif commercial_partner.l10n_id_nik:
                invoice_npwp = commercial_partner.l10n_id_nik
            if not invoice_npwp:
                action_error = {
                    'view_mode': 'form',
                    'res_model': 'res.partner',
                    'type': 'ir.actions.act_window',
                    'res_id': commercial_partner.id,
                    'views': [[self.env.ref('base.view_partner_form').id, 'form']],
                }
                msg = _("Please make sure that you've input the appropriate NPWP or NIK for the following customer")
                raise RedirectWarning(msg, action_error, _("Edit Customer Information"))
            invoice_npwp = invoice_npwp.replace('.', '').replace('-', '')

            etax_name = commercial_partner.l10n_id_tax_name or move.partner_id.name
            if invoice_npwp[:15] == '000000000000000' and commercial_partner.l10n_id_nik:
                etax_name = "%s#NIK#NAMA#%s" % (commercial_partner.l10n_id_nik, etax_name)

            # Here all fields or columns based on eTax Invoice Third Party
            eTax['KD_JENIS_TRANSAKSI'] = move.l10n_id_tax_number[0:2] or 0
            eTax['FG_PENGGANTI'] = move.l10n_id_tax_number[2:3] or 0
            eTax['NOMOR_FAKTUR'] = move.l10n_id_tax_number[3:] or 0
            eTax['MASA_PAJAK'] = move.invoice_date.month
            eTax['TAHUN_PAJAK'] = move.invoice_date.year
            eTax['TANGGAL_FAKTUR'] = '{0}/{1}/{2}'.format(move.invoice_date.day, move.invoice_date.month, move.invoice_date.year)
            eTax['NPWP'] = invoice_npwp
            eTax['NAMA'] = etax_name
            eTax['ALAMAT_LENGKAP'] = move.partner_id.contact_address.replace('\n', '').strip() if eTax['NPWP'] == '000000000000000' else commercial_partner.l10n_id_tax_address or street
            eTax['JUMLAH_DPP'] = int(float_round(move.amount_untaxed, 0)) # currency rounded to the unit
            eTax['JUMLAH_PPN'] = int(float_round(move.amount_tax, 0, rounding_method="DOWN"))  # tax amount ALWAYS rounded down
            eTax['ID_KETERANGAN_TAMBAHAN'] = '1' if move.l10n_id_kode_transaksi == '07' else ''
            eTax['REFERENSI'] = number_ref
            eTax['KODE_DOKUMEN_PENDUKUNG'] = '0'

            lines = move.line_ids.filtered(lambda x: x.product_id.id == int(dp_product_id) and x.price_unit < 0 and not x.display_type)
            eTax['FG_UANG_MUKA'] = 0
            eTax['UANG_MUKA_DPP'] = float_repr(abs(sum(lines.mapped(lambda l: float_round(l.price_subtotal, 0)))), 0)
            eTax['UANG_MUKA_PPN'] = float_repr(abs(sum(lines.mapped(lambda l: float_round(l.price_total - l.price_subtotal, 0)))), 0)

            fk_values_list = ['FK'] + [eTax[f] for f in FK_HEAD_LIST[1:]]

            # HOW TO ADD 2 line to 1 line for free product
            free, sales = [], []

            for line in move.line_ids.filtered(lambda l: not l.exclude_from_invoice_tab and not l.display_type):
                # *invoice_line_unit_price is price unit use for harga_satuan's column
                # *invoice_line_quantity is quantity use for jumlah_barang's column
                # *invoice_line_total_price is bruto price use for harga_total's column
                # *invoice_line_discount_m2m is discount price use for diskon's column
                # *line.price_subtotal is subtotal price use for dpp's column
                # *tax_line or free_tax_line is tax price use for ppn's column
                free_tax_line = tax_line = bruto_total = total_discount = 0.0

                if move.l10n_id_kode_transaksi == '08':
                    tax_line += line.price_subtotal * (11 / 100.0)
                else:
                    for tax in line.tax_ids:
                        if tax.amount > 0:
                            tax_line += line.price_subtotal * (tax.amount / 100.0)

                discount = 1 - (line.discount / 100)
                # guarantees price to be tax-excluded
                invoice_line_total_price = line.price_subtotal / discount if discount else 0
                invoice_line_unit_price = invoice_line_total_price / line.quantity if line.quantity else 0

                line_dict = {
                    'KODE_OBJEK': line.product_id.default_code or '',
                    'NAMA': line.product_id.name or '',
                    'HARGA_SATUAN': float_repr(float_round(invoice_line_unit_price, 0), 0),
                    'JUMLAH_BARANG': line.quantity,
                    'HARGA_TOTAL': float_repr(float_round(invoice_line_total_price, 0), 0),
                    'DPP': float_round(line.price_subtotal, 0),
                    'product_id': line.product_id.id,
                }

                if line.price_subtotal < 0:
                    if move.l10n_id_kode_transaksi == '08':
                        free_tax_line += (line.price_subtotal * (11 / 100.0)) * -1.0
                    else:
                        for tax in line.tax_ids:
                            free_tax_line += (line.price_subtotal * (tax.amount / 100.0)) * -1.0

                    line_dict.update({
                        'DISKON': float_round(invoice_line_total_price - line.price_subtotal, 0),
                        'PPN': float_round(free_tax_line, 0),
                    })
                    free.append(line_dict)
                elif line.price_subtotal != 0.0:
                    invoice_line_discount_m2m = invoice_line_total_price - line.price_subtotal

                    line_dict.update({
                        'DISKON': float_round(invoice_line_discount_m2m, 0),
                        'PPN': float_round(tax_line, 0),
                    })
                    sales.append(line_dict)

            sub_total_before_adjustment = sub_total_ppn_before_adjustment = 0.0

            # We are finding the product that has affected
            # by free product to adjustment the calculation
            # of discount and subtotal.
            # - the price total of free product will be
            # included as a discount to related of product.
            for sale in sales:
                for f in free:
                    if f['product_id'] == sale['product_id']:
                        sale['DISKON'] = sale['DISKON'] - f['DISKON'] + f['PPN']
                        sale['DPP'] = sale['DPP'] + f['DPP']

                        tax_line = 0

                        if move.l10n_id_kode_transaksi == '08':
                            tax_line += sale['DPP'] * (11 / 100.0)
                        else:    
                            for tax in line.tax_ids:
                                if tax.amount > 0:
                                    tax_line += sale['DPP'] * (tax.amount / 100.0)

                        sale['PPN'] = int(float_round(tax_line, 0))

                        free.remove(f)

                sub_total_before_adjustment += sale['DPP']
                sub_total_ppn_before_adjustment += sale['PPN']
                bruto_total += sale['DISKON']
                total_discount += float_round(sale['DISKON'], 2)

                # Change the values to string format after being used
                sale.update({
                    'DPP': float_repr(sale['DPP'], 0),
                    'PPN': float_repr(sale['PPN'], 0),
                    'DISKON': float_repr(sale['DISKON'], 0),
                })

            output_head += _csv_row(fk_values_list, delimiter)
            for sale in sales:
                of_values_list = ['OF'] + [str(sale[f]) for f in OF_HEAD_LIST[1:-2]] + ['0', '0']
                output_head += _csv_row(of_values_list, delimiter)

        return output_head
