# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime

STATE_SELECTION = [
    ('new', 'New'),
    ('closing', 'Closing'),
    ('unit', 'Admin Unit'),
    ('region', 'Admin Prod Region'),
    ('ho', 'Admin Prod HO'),
    ('finance', 'Finance'),
    ('done', 'Done'),
]

JENIS_KONTRAK_SELECTION = [
    ('farming', 'Farming'),
    ('maklon', 'Maklon'),
]

JENIS_KANDANG_SELECTION = [
    ('close', 'Close House'),
    ('semi', 'Semi Close House'),
    ('open', 'Open House'),
    ('panggung', 'Panggung'),
    ('postal', 'Postal'),
]

class AnalyticRhpp(models.Model):
    _name = 'analytic.rhpp'
    _description = 'Setup and Config for Analytic Rhpp'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    state = fields.Selection(STATE_SELECTION, string='State',default='new', tracking=True)
    company_id = fields.Many2one('res.company', store=True, copy=False, string="Company", default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency", related='company_id.currency_id')

    id_mitra = fields.Many2one('account.analytic.account', string='Id Mitra', required=True, tracking=True)
    name = fields.Many2one('res.partner', string='Nama', tracking=True, readonly=True)
    jenis_kontrak = fields.Selection(JENIS_KONTRAK_SELECTION, string='Jenis Kontrak', default='farming', tracking=True, readonly=True)
    periode = fields.Char(string='Periode', readonly=True)
    tanggal_pengajuan = fields.Date(string='Tanggal Pengajuan')
    bank_id = fields.Many2one('res.partner.bank', string="Bank")
    unit = fields.Many2one('unit.rhpp', string='Unit', tracking=True, readonly=True)
    ppl = fields.Char(string="PPL", readonly=True)
    jenis_kandang = fields.Selection(JENIS_KANDANG_SELECTION, string='Jenis Kandang', default='close', tracking=True, readonly=True)
    populasi = fields.Float(string='Populasi', readonly=True)
    tanggal_doc_in = fields.Date(string='Tgl DOC In', readonly=True)

    populasi_awal = fields.Float(string='Populasi Awal', digits=(2,0), compute="_compute_populasi_awal")
    deplesi = fields.Float(string='Deplesi', digits=(2,0))
    deplesi_percentage = fields.Float(string='Deplesi (%)', compute="_compute_deplesi_percentage")
    panen = fields.Float(string='Panen', digits=(2,0), compute="_compute_panen")
    panen_tonase = fields.Float(string='Panen Tonase', compute="_compute_panen_tonase")
    selisih_produksi = fields.Float(string='Selisih Produksi', digits=(2,0), compute="_compute_selisih_produksi")

    pakan_terkirim = fields.Float(string='Pakan Terkirim', digits=(2,0), compute="_compute_pakan_terkirim")
    pakan_terpakai = fields.Float(string='Pakan Terpakai', digits=(2,0), compute="_compute_pakan_terpakai")
    pakan_sisa = fields.Float(string='Pakan Sisa', digits=(2,0), compute="_compute_pakan_sisa")
    pakan_retur = fields.Float(string='Pakan Retur', digits=(2,0), compute="_compute_pakan_retur")
    pakan_ratio = fields.Float(string='Pakan/Ekor Ratio', compute="_compute_pakan_ratio")
    efisiensi_pakan = fields.Float(string='Efisiensi Pakan (%)', compute="_compute_efisiensi_pakan")

    bobot_rata = fields.Float(string='Bobot Rata-rata', compute="_compute_bobot_rata_rata")
    umur = fields.Float(string='Umur', compute="_compute_umur")
    fcr = fields.Float(string='FCR', digits=(2,3), compute="_compute_fcr")
    diff_fcr = fields.Char(string='Diff FCR', default="0.000", compute="_compute_diff_fcr")
    adg = fields.Float(string='ADG', compute="_compute_adg")
    ip = fields.Float(string='IP', compute="_compute_ip")

    doc = fields.Monetary(string='DOC', compute='_compute_doc_lines')
    pakan = fields.Monetary(string='Pakan', compute='_compute_pakan_lines')
    obat_vaksin_kimia = fields.Monetary(string='Obat, Vaksin & Kimia', compute='_compute_obat_vaksin_kimia_lines')
    live_bird = fields.Monetary(string='Live Bird', compute='_compute_live_bird_lines')
    sale = fields.Monetary(string='Sale', compute='_compute_sale_lines')
    iot = fields.Monetary(string='Internet of Things', compute='_compute_iot_lines')
    
    pendapatan_awal = fields.Monetary(string='Pendapatan Awal', compute='_compute_pendapatan_awal_lines')
    kompensasi = fields.Monetary(string='Kompensasi')
    bonus_ch = fields.Monetary(string='Bonus CH', compute='_compute_bonus_ch_lines')
    bonus_ip = fields.Monetary(string='Bonus IP', compute='_compute_bonus_ip_lines')
    bonus_pasar = fields.Monetary(string='Bonus Pasar', compute='_compute_bonus_pasar_lines')
    bonus_capaian_fcr = fields.Monetary(string='Bonus Capaian FCR', compute='_compute_bonus_fcr_lines')
    bonus_daya_hidup = fields.Monetary(string='Bonus Daya Hidup', compute='_compute_bonus_bdh_lines')
    pendapatan_akhir = fields.Monetary(string='Pendapatan Akhir', compute='_compute_pendapatan_akhir_lines')
    pendapatan_ratio = fields.Monetary(string='Pendapatan/Populasi Ratio', compute='_compute_populasi_ratio_lines')
    dpp = fields.Monetary(string='DPP', compute='_compute_dpp_lines')

    pph_21 = fields.Monetary(string='PPh Pasal 21', compute='_compute_pph_21_lines')
    selisih_pakan_rhpp = fields.Monetary(string='Potongan Selisih Pakan - RHPP')
    selisih_pakan_tunai = fields.Monetary(string='Potongan Selisih Pakan - Tunai')

    saldo_awal = fields.Monetary(string='Saldo Utang - Awal')
    cicilan_rhpp = fields.Monetary(string='Saldo Utang - RHPP')
    cicilan_tunai = fields.Monetary(string='Saldo Utang - Tunai')
    saldo_akhir = fields.Monetary(string='Saldo Utang - Akhir')

    saldo_tabungan_awal = fields.Monetary(string='Saldo Tabungan - Awal')
    tabungan_baru = fields.Monetary(string='Tabungan Baru')
    saldo_tabungan_akhir = fields.Monetary(string='Saldo Tabungan - Akhir')
    penarikan_tabungan = fields.Monetary(string='Penarikan Tabungan')
    is_penarikan_tabungan = fields.Boolean(string='Is Penarikan Tabungan', default=True)
    
    iot_count = fields.Integer(compute='_compute_iot_count')
    ovk_count = fields.Integer(compute='_compute_ovk_count')
    pakan_count = fields.Integer(compute='_compute_pakan_count')
    doc_count = fields.Integer(compute='_compute_doc_count')
    hasil_panen_count = fields.Integer(compute='_compute_hasil_panen_count')
    journal_rhpp_count = fields.Integer(compute='_compute_journal_rhpp_count')

    inv_avg = fields.Float(compute='_compute_inv_avg', string='Inv Avg')
    bill_avg = fields.Float(compute='_compute_bill_avg', string='Bill Avg')
    selisih = fields.Float(compute='_compute_selisih', string='Selisih')
    bp = fields.Float(compute='_compute_bp', string='BP')
    pendapatan_bersih = fields.Monetary(compute='_compute_pendapatan_bersih', string='Pendapatan Bersih')

    doc_ids = fields.One2many('account.analytic.line', compute='_compute_doc_ids', string='DOC')
    pakan_ids = fields.One2many('account.analytic.line', compute='_compute_pakan_ids', string='Pakan')
    ovk_ids = fields.One2many('account.analytic.line', compute='_compute_ovk_ids', string='OVK')
    live_bird_ids = fields.One2many('account.analytic.line', compute='_compute_live_bird_ids', string='Live Bird')
    iot_ids = fields.One2many('account.analytic.line', compute='_compute_iot_ids', string='IoT')

    is_bonus_ch = fields.Boolean(compute='_compute_bonus_ch', string='Is Bonus CH')
    is_bonus_ip = fields.Boolean(compute='_compute_bonus_ip', string='Is Bonus IP')
    is_bonus_pasar = fields.Boolean(compute='_compute_bonus_pasar', string='Is Bonus Pasar')
    is_bonus_fcr = fields.Boolean(compute='_compute_bonus_fcr', string='Is Bonus Fcr')
    is_bonus_bdh = fields.Boolean(compute='_compute_bonus_bdh', string='Is Bonus Daya Hidup')

    def _compute_bonus_ch(self):
        for rec in self:
            rec.is_bonus_ch = False
            form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)])
            if form_kontrak:
                if form_kontrak.template_kontrak_id:
                    if form_kontrak.template_kontrak_id.bonus_jenis_kandang_id:
                        rec.is_bonus_ch = True
    
    def _compute_bonus_ip(self):
        for rec in self:
            rec.is_bonus_ip = False
            form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)])
            if form_kontrak:
                if form_kontrak.template_kontrak_id:
                    if form_kontrak.template_kontrak_id.bonus_ip_id:
                        rec.is_bonus_ip = True
    
    def _compute_bonus_pasar(self):
        for rec in self:
            rec.is_bonus_pasar = False
            form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)])
            if form_kontrak:
                if form_kontrak.template_kontrak_id:
                    if form_kontrak.template_kontrak_id.bonus_pasar_id:
                        rec.is_bonus_pasar = True
    
    def _compute_bonus_fcr(self):
        for rec in self:
            rec.is_bonus_fcr = False
            form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)])
            if form_kontrak:
                if form_kontrak.template_kontrak_id:
                    if form_kontrak.template_kontrak_id.bonus_capaian_fcr_id:
                        rec.is_bonus_fcr = True
    
    def _compute_bonus_bdh(self):
        for rec in self:
            rec.is_bonus_bdh = False
            form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)])
            if form_kontrak:
                if form_kontrak.template_kontrak_id:
                    if form_kontrak.template_kontrak_id.bonus_daya_hidup_id:
                        rec.is_bonus_bdh = True

    def _compute_doc_ids(self):
        for rec in self:
            if rec.id_mitra:
                analytic_account = self.env['account.analytic.account'].search([('id', '=', rec.id_mitra.id)])
                product_categories = self.env['product.category'].search([('name', '=', 'DOC FS')])
                analytic_account_line = self.env['account.analytic.line'].search([('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)], order="date asc")
                rec.doc_ids = analytic_account_line
    
    def _compute_pakan_ids(self):
        for rec in self:
            if rec.id_mitra:
                analytic_account = self.env['account.analytic.account'].search([('id', '=', rec.id_mitra.id)])
                product_categories = self.env['product.category'].search([('name', 'in', ['Starter', 'Pre Starter', 'Finisher'])])
                analytic_account_line = self.env['account.analytic.line'].search([('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)], order="date asc")
                rec.pakan_ids = analytic_account_line
    
    def _compute_ovk_ids(self):
        for rec in self:
            if rec.id_mitra:
                analytic_account = self.env['account.analytic.account'].search([('id', '=', rec.id_mitra.id)])
                product_categories = self.env['product.category'].search([('name', '=', 'Obat, Vaksin & Kimia')])
                analytic_account_line = self.env['account.analytic.line'].search([('account_id', '=', analytic_account.id), ('product_id.categ_id', 'in', product_categories.ids)], order="date asc")
                rec.ovk_ids = analytic_account_line

    def _compute_live_bird_ids(self):
        for rec in self:
            if rec.id_mitra:
                analytic_account = self.env['account.analytic.account'].search([('id', '=', rec.id_mitra.id)])
                product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
                analytic_account_line = self.env['account.analytic.line'].search([('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'purchase'), ('product_id.categ_id', 'in', product_categories.ids)], order="date asc")
                rec.live_bird_ids = analytic_account_line

    def _compute_iot_ids(self):
        for rec in self:
            if rec.id_mitra:
                analytic_account = self.env['account.analytic.account'].search([('id', '=', rec.id_mitra.id)])
                product_categories = self.env['product.category'].search([('name', '=', 'IoT')])
                analytic_account_line = self.env['account.analytic.line'].search([('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)], order="date asc")
                rec.iot_ids = analytic_account_line

    @api.depends('populasi')
    def _compute_populasi_awal(self):
        for rec in self:
            rec.populasi_awal = 0.0
            if rec.populasi:
                rec.populasi_awal = rec.populasi
    
    @api.depends('deplesi', 'populasi_awal')
    def _compute_deplesi_percentage(self):
        for rec in self:
            rec.deplesi_percentage = 0.0
            if rec.deplesi and rec.populasi_awal:
                rec.deplesi_percentage = (rec.deplesi / rec.populasi_awal) * 100
    
    @api.depends('populasi_awal', 'pakan_terpakai')
    def _compute_pakan_ratio(self):
        for rec in self:
            rec.pakan_ratio = 0.0
            if rec.populasi_awal and rec.pakan_terpakai:
                rec.pakan_ratio = (rec.pakan_terpakai / rec.populasi_awal)
    
    @api.depends('fcr')
    def _compute_efisiensi_pakan(self):
        for rec in self:
            rec.efisiensi_pakan = 0.0
            if rec.fcr:
                rec.efisiensi_pakan = round(100 / rec.fcr)
    
    @api.depends('pakan_terpakai', 'panen_tonase')
    def _compute_fcr(self):
        for rec in self:
            rec.fcr = 0.0
            if rec.pakan_terpakai and rec.panen_tonase:
                rec.fcr = round(rec.pakan_terpakai / rec.panen_tonase, 2)

    @api.depends('id_mitra', 'populasi_awal', 'deplesi')
    def _compute_selisih_produksi(self):
        for rec in self:
            rec.selisih_produksi = 0.0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', '=', product_categories.id)])
                    if move_lines:
                        ekor_panen = 0.0
                        for move in move_lines:
                            jumlah_ekoran = self._get_jumlah_ekoran(move)
                            if jumlah_ekoran:
                                ekor_panen += jumlah_ekoran                   
                        rec.selisih_produksi = ekor_panen - (rec.populasi_awal - rec.deplesi)
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', 'in', product_categories)])
                    if move_lines:
                        ekor_panen = 0.0
                        for move in move_lines:
                            jumlah_ekoran = self._get_jumlah_ekoran(move)
                            if jumlah_ekoran:
                                ekor_panen += jumlah_ekoran                   
                        rec.selisih_produksi = ekor_panen - (rec.populasi_awal - rec.deplesi)

    @api.depends('id_mitra')
    def _compute_bobot_rata_rata(self):
        for rec in self:
            rec.bobot_rata = 0.0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', '=', product_categories.id)])
                    if move_lines:
                        bobot_panen = 0.0
                        ekor_panen = 0.0
                        for move in move_lines:
                            jumlah_ekoran = self._get_jumlah_ekoran(move)
                            if move.quantity:
                                bobot_panen += move.quantity
                            if jumlah_ekoran:
                                ekor_panen += jumlah_ekoran
                        try:
                            rec.bobot_rata = bobot_panen / ekor_panen
                        except ZeroDivisionError:
                            rec.bobot_rata = 0.0
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', 'in', product_categories)])
                    if move_lines:
                        bobot_panen = 0.0
                        ekor_panen = 0.0
                        for move in move_lines:
                            jumlah_ekoran = self._get_jumlah_ekoran(move)
                            if move.quantity:
                                bobot_panen += move.quantity
                            if jumlah_ekoran:
                                ekor_panen += jumlah_ekoran
                        try:
                            rec.bobot_rata = bobot_panen / ekor_panen
                        except ZeroDivisionError:
                            rec.bobot_rata = 0.0
    
    @api.depends('id_mitra')
    def _compute_panen(self):
        for rec in self:
            rec.panen = 0.0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', '=', product_categories.id)])
                    if move_lines:
                        panen = 0.0
                        for move in move_lines:
                            jumlah_ekoran = self._get_jumlah_ekoran(move)
                            if jumlah_ekoran:
                                panen += jumlah_ekoran
                        rec.panen = panen
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', 'in', product_categories)])
                    if move_lines:
                        panen = 0.0
                        for move in move_lines:
                            jumlah_ekoran = self._get_jumlah_ekoran(move)
                            if jumlah_ekoran:
                                panen += jumlah_ekoran
                        rec.panen = panen
    
    @api.depends('id_mitra')
    def _compute_panen_tonase(self):
        for rec in self:
            rec.panen_tonase = 0.0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', '=', product_categories.id)])
                    if move_lines:
                        panen_tonase = 0.0
                        for move in move_lines:
                            if move.quantity:
                                panen_tonase += move.quantity
                        rec.panen_tonase = panen_tonase
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', 'in', product_categories)])
                    if move_lines:
                        panen_tonase = 0.0
                        for move in move_lines:
                                if move.quantity:
                                    panen_tonase += move.quantity
                        rec.panen_tonase = panen_tonase

    @api.depends('pakan_terkirim', 'pakan_terpakai')
    def _compute_pakan_sisa(self):
        for rec in self:            
            rec.pakan_sisa = 0.0
            if rec.pakan_terkirim and rec.pakan_terpakai:
                rec.pakan_sisa = rec.pakan_terkirim - rec.pakan_terpakai
    
    @api.depends('id_mitra')
    def _compute_pakan_terkirim(self):
        for rec in self:
            rec.pakan_terkirim = 0.0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', 'in', ['Starter', 'Pre Starter', 'Finisher'])])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                    if move_lines:
                        total_terkirim = 0.0
                        for move in move_lines:
                            if move.quantity:
                                if 'RJSL' not in move.move_id.name or move.move_id.move_type != 'out_refund':
                                    total_terkirim += move.quantity
                        rec.pakan_terkirim = total_terkirim
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)])
                    if move_lines:
                        total_terkirim = 0.0
                        for move in move_lines:
                            if move.quantity:
                                if 'RJSL' not in move.move_id.name or move.move_id.move_type != 'out_refund':
                                    total_terkirim += move.quantity
                        rec.pakan_terkirim = total_terkirim
    
    @api.depends('id_mitra')
    def _compute_pakan_terpakai(self):
        for rec in self:
            rec.pakan_terpakai = 0.0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', 'in', ['Starter', 'Pre Starter', 'Finisher'])])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                    if move_lines:
                        total_penambah = 0.0
                        total_pengurang = 0.0
                        for move in move_lines:
                            if move.quantity:
                                if 'RJSL' in move.move_id.name or move.move_id.move_type == 'out_refund':
                                    total_pengurang += move.quantity
                                else:
                                    total_penambah += move.quantity
                        rec.pakan_terpakai = total_penambah - total_pengurang
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)])
                    if move_lines:
                        total_penambah = 0.0
                        total_pengurang = 0.0
                        for move in move_lines:
                            if move.quantity:
                                if 'RJSL' in move.move_id.name or move.move_id.move_type == 'out_refund':
                                    total_pengurang += move.quantity
                                else:
                                    total_penambah += move.quantity
                        rec.pakan_terpakai = total_penambah - total_pengurang        
    
    @api.depends('id_mitra')
    def _compute_pakan_retur(self):
        for rec in self:
            rec.pakan_retur = 0.0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', 'in', ['Starter', 'Pre Starter', 'Finisher'])])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                    if move_lines:
                        total_retur = 0.0
                        for move in move_lines:
                            if move.quantity:
                                if 'RJSL' in move.move_id.name:
                                    total_retur += move.quantity
                        rec.pakan_retur = total_retur
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)])
                    if move_lines:
                        total_retur = 0.0
                        for move in move_lines:
                            if move.quantity:
                                if 'RJSL' in move.move_id.name:
                                    total_retur += move.quantity
                        rec.pakan_retur = total_retur

    @api.depends('id_mitra', 'tanggal_doc_in', 'panen')
    def _compute_umur(self):
        for rec in self:
            rec.umur = 0.0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', '=', product_categories.id)])
                    if move_lines:
                        total_umur_ekor = 0.0
                        for move in move_lines:
                            if rec.tanggal_doc_in and rec.panen and move.move_id:
                                jumlah_ekoran = self._get_jumlah_ekoran(move)
                                total_umur_ekor += (move.move_id.invoice_date - rec.tanggal_doc_in).days * jumlah_ekoran
                        try:
                            rec.umur = total_umur_ekor / rec.panen
                        except ZeroDivisionError:
                            rec.umur = 0
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', 'in', product_categories)])
                    if move_lines:
                        total_umur_ekor = 0.0
                        for move in move_lines:
                            if rec.tanggal_doc_in and rec.panen and move.move_id:
                                jumlah_ekoran = self._get_jumlah_ekoran(move)
                                total_umur_ekor += (move.move_id.invoice_date - rec.tanggal_doc_in).days * jumlah_ekoran
                        try:
                            rec.umur = total_umur_ekor / rec.panen
                        except ZeroDivisionError:
                            rec.umur = 0

    @api.depends('fcr', 'bobot_rata')
    def _compute_diff_fcr(self):
        for rec in self:
            rec.diff_fcr = 0.000
            if rec.fcr and rec.bobot_rata:
                standar_fcr = self.env['standar.fcr'].search([('body_weight', '=', round(rec.bobot_rata,2))], limit=1)
                if len(standar_fcr) > 0:
                    diff_fcr = rec.fcr - standar_fcr.feed_converion_ratio
                    rec.diff_fcr = str(round(diff_fcr, 2)) + "0"
    
    @api.depends('bobot_rata', 'umur')
    def _compute_adg(self):
        for rec in self:
            rec.adg = 0.0
            if rec.bobot_rata and rec.umur:
                rec.adg = round((rec.bobot_rata * 1000) / rec.umur,2)
    
    @api.depends('deplesi_percentage', 'bobot_rata', 'fcr', 'umur')
    def _compute_ip(self):
        for rec in self:
            rec.ip = 0.0
            if rec.deplesi_percentage and rec.bobot_rata and rec.fcr and rec.umur:
                rec.ip = (((100 - rec.deplesi_percentage) * rec.bobot_rata) / (rec.umur * rec.fcr)) * 100
                    
    def _compute_pendapatan_bersih(self):
        for rec in self:
            potongan = rec.pph_21 + rec.selisih_pakan_rhpp +  rec.selisih_pakan_tunai + rec.saldo_awal + rec.cicilan_rhpp + rec.cicilan_tunai + rec.saldo_akhir + rec.saldo_tabungan_awal + rec.tabungan_baru + rec.saldo_tabungan_akhir
            rec.pendapatan_bersih = rec.pendapatan_akhir - potongan

    def _compute_inv_avg(self):
        product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
        line_inv = self.env['account.invoice.report'].search([('journal_id.type', '=', 'sale'),('product_categ_id', '=', product_categories.id)])
        for rec in self:
            if line_inv:
                rec.inv_avg = sum(l.price_average for l in line_inv)
            else:
                rec.inv_avg = 0.0

    def _compute_bill_avg(self):
        product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
        line_bill = self.env['account.invoice.report'].search([('journal_id.type', '=', 'purchase'),('product_categ_id', '=', product_categories.id)])
        for rec in self:
            if line_bill:
                rec.bill_avg = sum(l.price_average for l in line_bill)
            else:
                rec.bill_avg = 0.0

    @api.depends('inv_avg', 'bill_avg')
    def _compute_selisih(self):
        for record in self:
            if record.inv_avg > record.bill_avg:
                record.selisih = record.inv_avg - record.bill_avg
            else:
                record.selisih = 0.0

    @api.depends('selisih', 'panen_tonase')
    def _compute_bp(self):
        for record in self:
            record.bp = record.selisih * record.panen_tonase

    def _compute_bonus_pasar_lines(self):
        for record in self:
            record.bonus_pasar = 0
            form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', record.id_mitra.id),('contact_peternak', '=', record.name.id),('unit', '=', record.unit.id)])
            if form_kontrak:
                bonus_pasar_obj = form_kontrak.template_kontrak_id.bonus_pasar_id
                if bonus_pasar_obj:
                    if len(bonus_pasar_obj.bonus_pasar_line):
                        for bonus in bonus_pasar_obj.bonus_pasar_line:
                            if bonus.diff_fcr_start <= record.diff_fcr and bonus.diff_fcr_end >= record.diff_fcr:
                                record.bonus_pasar = (bonus.presentase_bonus / 100) * record.bp

    def _compute_bonus_bdh_lines(self):
        for rec in self:
            if self._check_rhpp_rugi(rec):
                rec.bonus_daya_hidup = 0
            else:
                rec.bonus_daya_hidup = 0
                form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)])
                if form_kontrak:
                    bonus_bdh_obj = form_kontrak.template_kontrak_id.bonus_daya_hidup_id
                    if bonus_bdh_obj:    
                        if bonus_bdh_obj.presentasi_hidup <= rec.deplesi_percentage:
                            rec.bonus_daya_hidup = bonus_bdh_obj.nilai_bonus * rec.panen
                        elif bonus_bdh_obj.presentasi_hidup >= rec.deplesi_percentage:
                            rec.bonus_daya_hidup = 0
                        else:
                            rec.bonus_daya_hidup = 0

    def _compute_dpp_lines(self):
        for rec in self:
            rec.dpp = rec.pendapatan_akhir * (50/100)

    def _compute_pph_21_lines(self):
        for rec in self:
            kontrak_vals = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)], limit=1, order='id desc').no_surat_pp_23
            pph_21_obj = self.env['pph.pasal.21'].search([('pendapatan_min', '<=', rec.dpp),('pendapatan_max', '>=', rec.dpp)], limit=1)
            if kontrak_vals:
                rec.pph_21 = rec.pendapatan_akhir * (0.5/100)
            if kontrak_vals == False:
                if pph_21_obj:
                    pph_21_obj_lapis_1 = self.env['pph.pasal.21'].search([('lapis', '=', 1)], limit=1)
                    if pph_21_obj.lapis == 1:
                        rec.pph_21 = rec.dpp * pph_21_obj_lapis_1.pajak_percentage/100
                    pph_21_obj_lapis_2 = self.env['pph.pasal.21'].search([('lapis', '=', 2)], limit=1)
                    if pph_21_obj.lapis == 2:
                        rec.pph_21 = (pph_21_obj_lapis_1.pendapatan_max * pph_21_obj_lapis_1.pajak_percentage/100) + (rec.dpp - pph_21_obj_lapis_2.pendapatan_min * pph_21_obj_lapis_2.pajak_percentage/100)
                    pph_21_obj_lapis_3 = self.env['pph.pasal.21'].search([('lapis', '=', 3)], limit=1)
                    if pph_21_obj.lapis == 3:
                        rec.pph_21 = (pph_21_obj_lapis_1.pendapatan_max * pph_21_obj_lapis_1.pajak_percentage/100) + (pph_21_obj_lapis_2.pendapatan_max - pph_21_obj_lapis_2.pendapatan_min * pph_21_obj_lapis_2.pajak_percentage/100) + (pph_21_obj_lapis_3.pendapatan_min * pph_21_obj_lapis_3.pajak_percentage/100)
                    pph_21_obj_lapis_4 = self.env['pph.pasal.21'].search([('lapis', '=', 4)], limit=1)
                    if pph_21_obj.lapis == 4:
                        rec.pph_21 = 0
                    pph_21_obj_lapis_5 = self.env['pph.pasal.21'].search([('lapis', '=', 5)], limit=1)
                    if pph_21_obj.lapis == 5:
                        rec.pph_21 = 0
                elif self.dpp <= 0:
                    rec.pph_21 = 0
                else:
                    raise ValidationError(_('PPh 21 not yet available in configuration PPh Pasal 21.'))
    
    def _compute_bonus_ch_lines(self):
        for rec in self:
            if self._check_rhpp_rugi(rec):
                rec.bonus_ch = 0
            else:
                rec.bonus_ch = 0
                form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)])
                if form_kontrak:
                    bonus_ch_obj = form_kontrak.template_kontrak_id.bonus_jenis_kandang_id
                    if bonus_ch_obj:
                        if len(bonus_ch_obj.bonus_jenis_kandang_type_ids) > 0:
                            for bonus in bonus_ch_obj.bonus_jenis_kandang_type_ids:
                                if bonus.kandang_bjk == rec.jenis_kandang:
                                    rec.bonus_ch = bonus.nilai_bonus * rec.populasi_awal
    
    def _compute_bonus_ip_lines(self):
        for rec in self:
            if self._check_rhpp_rugi(rec):
                rec.bonus_ip = 0
            else:
                rec.bonus_ip = 0
                form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)])
                if form_kontrak:
                    bonus_ip_obj = form_kontrak.template_kontrak_id.bonus_ip_id
                    if bonus_ip_obj:
                        if len(bonus_ip_obj.bonus_ip_line) > 0:
                            for ip_line in bonus_ip_obj.bonus_ip_line:
                                if ip_line.ip_start <= rec.ip and ip_line.ip_end >= rec.ip:
                                    if bonus_ip_obj.type_bip == 'ekor':
                                        rec.bonus_ip = ip_line.nominal_bonus * rec.panen                                        
                                    if bonus_ip_obj.type_bip == 'pertonase':
                                        rec.bonus_ip = ip_line.nominal_bonus * rec.panen_tonase
                                    else:
                                        rec.bonus_ip = 0              

    def _compute_bonus_fcr_lines(self):
        for rec in self:
            if self._check_rhpp_rugi(rec):
                rec.bonus_capaian_fcr = 0
            else:
                rec.bonus_capaian_fcr = 0
                form_kontrak = self.env['form.kontrak.peternak'].search([('analytic_account', '=', rec.id_mitra.id),('contact_peternak', '=', rec.name.id),('unit', '=', rec.unit.id)])
                if form_kontrak:
                    bonus_fcr_obj = form_kontrak.template_kontrak_id.bonus_capaian_fcr_id
                    if bonus_fcr_obj:
                        if len(bonus_fcr_obj.bonus_capaian_fcr_line) > 0:
                            for bonus in bonus_fcr_obj.bonus_capaian_fcr_line:
                                if bonus.pencapaian_fcr_start <= rec.diff_fcr and bonus.pencapaian_fcr_end >= rec.diff_fcr:
                                    if bonus_fcr_obj.type_bcf == 'ekor':
                                        rec.bonus_capaian_fcr = bonus.nominal_bonus * rec.panen
                                    if bonus_fcr_obj.type_bcf == 'pertonase':
                                        rec.bonus_capaian_fcr = bonus.nominal_bonus * rec.panen_tonase


    def _compute_pendapatan_awal_lines(self):
        for rec in self:
            rec.pendapatan_awal = rec.live_bird - (rec.doc + rec.pakan + rec.obat_vaksin_kimia)
    
    def _compute_pendapatan_akhir_lines(self):
        for rec in self:
            rec.pendapatan_akhir = rec.pendapatan_awal + rec.kompensasi + rec.bonus_ch + rec.bonus_ip + rec.bonus_pasar + rec.bonus_capaian_fcr + rec.bonus_daya_hidup
    
    def _compute_populasi_ratio_lines(self):
        for rec in self:
            if rec.pendapatan_akhir != 0 and rec.populasi_awal != 0:
                rec.pendapatan_ratio = rec.pendapatan_akhir / rec.populasi_awal
            else:
                rec.pendapatan_ratio = rec.pendapatan_akhir
    
    def _compute_iot_lines(self):
        for rec in self:
            rec.iot = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'IoT')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.iot = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.iot = sum(total_amount.mapped('amount'))
                else:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.iot = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.iot = sum(total_amount.mapped('amount'))
    
    def _compute_iot_count(self):
        for record in self:
            record.iot_count = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', record.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'IoT')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    record.iot_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                else:
                    record.iot_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories)])

    def _compute_doc_lines(self):
        for rec in self:
            rec.doc = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'DOC FS')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.doc = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.doc = sum(total_amount.mapped('amount'))
                else:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.doc = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.doc = sum(total_amount.mapped('amount'))
    
    def _compute_doc_count(self):
        for record in self:
            record.doc_count = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', record.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'DOC FS')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    record.doc_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                else:
                    record.doc_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories)])
    
    def _compute_pakan_lines(self):
        for rec in self:
            rec.pakan = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', 'in', ['Starter', 'Pre Starter', 'Finisher'])])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.pakan = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.pakan = sum(total_amount.mapped('amount'))
                else:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.pakan = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.pakan = sum(total_amount.mapped('amount'))
    
    def _compute_pakan_count(self):
        for record in self:
            record.pakan_count = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', record.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', 'in', ['Starter', 'Pre Starter', 'Finisher'])])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    record.pakan_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                else:
                    record.pakan_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)])

    def _compute_obat_vaksin_kimia_lines(self):
        for rec in self:
            rec.obat_vaksin_kimia = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Obat, Vaksin & Kimia')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('product_id.categ_id', '=', product_categories.id)])
                    if sum(total_amount.mapped('after_tax')) <= 0:
                        rec.obat_vaksin_kimia = sum(total_amount.mapped('after_tax'))*(-1)
                    else:
                        rec.obat_vaksin_kimia = sum(total_amount.mapped('after_tax'))
                else:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('product_id.categ_id', 'in', product_categories)])
                    if sum(total_amount.mapped('after_tax')) <= 0:
                        rec.obat_vaksin_kimia = sum(total_amount.mapped('after_tax'))*(-1)
                    else:
                        rec.obat_vaksin_kimia = sum(total_amount.mapped('after_tax'))

    def _compute_ovk_count(self):
        for record in self:
            record.ovk_count = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', record.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Obat, Vaksin & Kimia')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    record.ovk_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('product_id.categ_id', '=', product_categories.id)])
                else:
                    record.ovk_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('product_id.categ_id', 'in', product_categories)])
                    
    def _compute_live_bird_lines(self):
        for rec in self:
            rec.live_bird = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'purchase'), ('product_id.categ_id', '=', product_categories.id)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.live_bird = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.live_bird = sum(total_amount.mapped('amount'))
                else:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'purchase'), ('product_id.categ_id', 'in', product_categories)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.live_bird = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.live_bird = sum(total_amount.mapped('amount'))
    
    def _compute_sale_lines(self):
        for rec in self:
            rec.sale = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', rec.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', '=', product_categories.id)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.sale = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.sale = sum(total_amount.mapped('amount'))
                else:
                    total_amount = self.env['account.analytic.line'].search(
                        [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories)])
                    if sum(total_amount.mapped('amount')) <= 0:
                        rec.sale = sum(total_amount.mapped('amount'))*(-1)
                    else:
                        rec.sale = sum(total_amount.mapped('amount'))
                    
    def _compute_hasil_panen_count(self):
        for record in self:
            record.hasil_panen_count = 0
            analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', record.id_mitra.id)])
            product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
            if len(product_categories) > 0 and len(analytic_account) > 0:
                if len(product_categories) == 1:
                    record.hasil_panen_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', '=', product_categories.id)])
                else:
                    record.hasil_panen_count = self.env['account.move.line'].search_count(
                        [('analytic_account_id', '=', analytic_account.id), ('journal_id.type', '=', 'purchase'), ('product_id.categ_id', 'in', product_categories)])
    
    def _compute_journal_rhpp_count(self):
        for record in self:
            record.journal_rhpp_count = 0
            account_move = self.env['account.move'].search([('analytic_rhpp_id', '=', record.id)])
            if len(account_move) > 0:
                record.journal_rhpp_count = len(account_move)
    
    def action_kalkulasi_tabungan(self):
        for rec in self:
            analytic_rhpp = self.env['analytic.rhpp'].search([('name', '=', rec.name.id), ('periode', '<', rec.periode)])
            if analytic_rhpp:
                rec.saldo_tabungan_awal = sum(x.saldo_tabungan_akhir for x in analytic_rhpp)
            if rec.pendapatan_ratio > 3000:
                rec.tabungan_baru = (rec.pendapatan_awal+rec.bonus_ch+rec.bonus_ip+rec.bonus_capaian_fcr+rec.bonus_daya_hidup+rec.kompensasi) * 0.10
            rec.saldo_tabungan_akhir = rec.saldo_tabungan_awal + rec.tabungan_baru
            if int(rec.periode) > 3:
                rec.penarikan_tabungan = rec.saldo_tabungan_akhir * 0.75
    
    def action_closing(self):
        self.state = 'closing'

    def action_admin_unit(self):
        if self.penarikan_tabungan > 0:
            return {
                'name': 'Confirm Tabungan RHPP',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                "view_type": "form",
                'res_model': 'popup.tabungan.rhpp.wizard',
                'target': 'new',
                'view_id': self.env.ref('custom_rhpp.popup_tabungan_rhpp_wizard_form').id,
                'context': {'active_id': self.id},
            }
        else:
            self.state = 'unit'
    
    def action_admin_prod_region(self):
        self.state = 'region'
    
    def action_admin_prod_ho(self):
        self.state = 'ho'
    
    def action_finance(self):
        if self.journal_rhpp_count > 0:
            return {
                'name': 'Confirm Journal RHPP',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                "view_type": "form",
                'res_model': 'analytic.rhpp.journal.wizard',
                'target': 'new',
                'view_id': self.env.ref
                ('custom_rhpp.analytic_rhpp_journal_wizard_form').id,
                'context': {'active_id': self.id},
            }
        else:    
            journal = self.env['account.journal'].search([('name', '=', 'Jurnal Umum'), ('company_id', '=', self.env.company.id)], limit=1)
            if not journal:
                raise ValidationError('Jurnal Umum Not Exists, please contact admin for create account journal')
            profit_loss = self.live_bird - (self.doc + self.pakan + self.obat_vaksin_kimia + self.iot)
            if profit_loss > 0:
                try:
                    penjualan_debit = self.env['account.account'].search([('code', '=', '1130001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (1130001101)'))
                    
                try:
                    penjualan_credit = self.env['account.account'].search([('code', '=', '1140001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (1140001101)'))
                    
                try:
                    pembelian_debit = self.env['account.account'].search([('code', '=', '2110001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (2110001101)'))
                
                try:
                    pembelian_credit = self.env['account.account'].search([('code', '=', '1130001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (1130001101)'))
                
                try:
                    pendapatan_awal = self.env['account.account'].search([('code', '=', '2110001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (2110001101)'))
                
                try:
                    biaya_produksi = self.env['account.account'].search([('code', '=', '5150001102')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (5150001102)'))
                    
                try:
                    pph21 = self.env['account.account'].search([('code', '=', '2160001103')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (2160001103)'))
                    
                try:
                    utang_titipan = self.env['account.account'].search([('code', '=', '2180001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (2180001101)'))
                    
                try:
                    utang_rhpp = self.env['account.account'].search([('code', '=', '2180001102')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (2180001102)'))
                tabungan_peternak = 0
                if self.pendapatan_ratio > 3000:
                    tabungan_peternak = (self.pendapatan_awal+self.bonus_ch+self.bonus_ip+self.bonus_capaian_fcr+self.bonus_daya_hidup+self.kompensasi) * 0.10
                move = {
                    'name': '/',
                    'journal_id': journal.id,
                    'date': datetime.now(),
                    'ref': 'RHPP Peternak ' + self.name.name + ' Periode '+ self.periode,
                    'analytic_rhpp_id': self.id,
                    'line_ids': [
                                    (0, 0, {
                                            'name': 'Penjualan',
                                            'debit': self.sale,
                                            'account_id': penjualan_debit,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                            }
                                    ), 
                                    (0, 0, {
                                            'name': 'Penjualan',
                                            'credit': self.sale,
                                            'account_id': penjualan_credit,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Pembelian Livebird',
                                            'debit': self.live_bird,
                                            'account_id': pembelian_debit,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Pembelian Livebird',
                                            'credit': self.live_bird,
                                            'account_id': pembelian_credit,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Pendapatan Awal',
                                            'debit': self.pendapatan_awal,
                                            'account_id': pendapatan_awal,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Kompensasi',
                                            'debit': self.kompensasi,
                                            'account_id': biaya_produksi,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Bonus CH',
                                            'debit': self.bonus_ch,
                                            'account_id': biaya_produksi,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Bonus IP',
                                            'debit': self.bonus_ip,
                                            'account_id': biaya_produksi,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Bonus Pasar',
                                            'debit': self.bonus_pasar,
                                            'account_id': biaya_produksi,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Bonus Capaian FCR',
                                            'debit': self.bonus_capaian_fcr,
                                            'account_id': biaya_produksi,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Bonus Daya Hidup',
                                            'debit': self.bonus_daya_hidup,
                                            'account_id': biaya_produksi,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'PPh Ps 21',
                                            'credit': self.pph_21,
                                            'account_id': pph21,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Tabungan Peternak',
                                            'credit': tabungan_peternak,
                                            'account_id': utang_titipan,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Pencairan RHPP',
                                            'credit': (self.pendapatan_awal+self.bonus_ch+self.bonus_ip+self.bonus_capaian_fcr+self.bonus_daya_hidup+self.kompensasi)-(self.pph_21 + tabungan_peternak),
                                            'account_id': utang_rhpp,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    })
                                ] 
                }
                self.env['account.move'].create(move)
            else:
                try:
                    penjualan_debit = self.env['account.account'].search([('code', '=', '1130001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (1130001101)'))
                    
                try:
                    penjualan_credit = self.env['account.account'].search([('code', '=', '1140001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (1140001101)'))
                    
                try:
                    pembelian_debit = self.env['account.account'].search([('code', '=', '2110001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (2110001101)'))
                
                try:
                    pembelian_credit = self.env['account.account'].search([('code', '=', '1130001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (1130001101)'))
                
                try:
                    pendapatan_awal = self.env['account.account'].search([('code', '=', '1140001101')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (1140001101)'))
                    
                try:
                    biaya_produksi_rhpp = self.env['account.account'].search([('code', '=', '5150001102')], limit=1).id
                except:
                    raise ValidationError(_('Chart Of Account Does Not Exists, code number (5150001102)'))
                    
                move = {
                    'name': '/',
                    'journal_id': journal.id,
                    'date': datetime.now(),
                    'ref': 'RHPP Rugi ' + self.name.name + ' Periode '+ self.periode,
                    'analytic_rhpp_id': self.id,
                    'line_ids': [
                                    (0, 0, {
                                            'name': 'Penjualan',
                                            'debit': self.sale,
                                            'account_id': penjualan_debit,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                            }
                                    ), 
                                    (0, 0, {
                                            'name': 'Penjualan',
                                            'credit': self.sale,
                                            'account_id': penjualan_credit,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Pembelian Livebird',
                                            'debit': self.live_bird,
                                            'account_id': pembelian_debit,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Pembelian Livebird',
                                            'credit': self.live_bird,
                                            'account_id': pembelian_credit,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Pendapatan Awal',
                                            'credit': self.pendapatan_awal,
                                            'account_id': pendapatan_awal,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    }), 
                                    (0, 0, {
                                            'name': 'Sisa AR',
                                            'debit': self.pendapatan_awal,
                                            'account_id': biaya_produksi_rhpp,
                                            'analytic_account_id': self.id_mitra.id,
                                            'partner_id': self.name.id
                                    })
                                ] 
                }
                self.env['account.move'].create(move)
            self.state = 'finance'
    
    def action_analytic_rhpp_done(self):
        self.state = 'done'
        self.id_mitra.write({'state':'locked'})
        self.action_expired_kontrak_peternak()
        self.action_end_date_vendor_pricelist()
    
    def action_expired_kontrak_peternak(self):
        state_vals = self.env['form.kontrak.peternak'].search([('analytic_account', '=', self.id_mitra.id),('contact_peternak', '=', self.name.id),('unit', '=', self.unit.id)])
        print("PETERNAK",state_vals.id)
        for rec in state_vals:
            if rec:
                rec.state = 'expired'
    
    def action_end_date_vendor_pricelist(self):
        peternak_vals = self.env['form.kontrak.peternak'].search([('analytic_account', '=', self.id_mitra.id),('contact_peternak', '=', self.name.id),('unit', '=', self.unit.id)])
        print("PRICELIST",peternak_vals.id)
        pricelist_vals = self.env['product.supplierinfo'].search([('name', '=', self.name.id), ('reference', '=', peternak_vals.id)])
        print("PRICELIST",pricelist_vals.ids)
        for vendor in pricelist_vals:
            vendor.date_end = fields.Date.today()
    
    def action_print_rhpp(self):
        return self.env.ref('custom_rhpp.action_report_rhpp').report_action(self)
    
    def action_back_state(self):
        for rec in self:
            if rec.state == 'region':
                rec.state = 'unit'
            if rec.state == 'ho':
                rec.state = 'region'
            if rec.state == 'finance':
                rec.state = 'ho'

    def action_open_iot(self):
        self.ensure_one()
        analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', self.id_mitra.id)])
        product_categories = self.env['product.category'].search([('name', '=', 'IoT')])
        return {
            'name': _('Account Analytic Line'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': self.env.ref('analytic.view_account_analytic_line_tree').id,
            'res_model': 'account.analytic.line',
            'context': "{'create': False}",
            'domain': [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)],
        }

    def action_open_ovk(self):
        self.ensure_one()
        analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', self.id_mitra.id)])
        product_categories = self.env['product.category'].search([('name', '=', 'Obat, Vaksin & Kimia')])
        return {
            'name': _('Account Analytic Line'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': self.env.ref('analytic.view_account_analytic_line_tree').id,
            'res_model': 'account.analytic.line',
            'context': "{'create': False}",
            'domain': [('account_id', '=', analytic_account.id), ('product_id.categ_id', 'in', product_categories.ids)],
        }

    def action_open_pakan(self):
        self.ensure_one()
        analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', self.id_mitra.id)])
        product_categories = self.env['product.category'].search([('name', 'in', ['Starter', 'Pre Starter', 'Finisher'])])
        return {
            'name': _('Account Analytic Line'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': self.env.ref('analytic.view_account_analytic_line_tree').id,
            'res_model': 'account.analytic.line',
            'context': "{'create': False}",
            'domain': [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)],
        }
    
    def action_open_doc(self):
        self.ensure_one()
        analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', self.id_mitra.id)])
        product_categories = self.env['product.category'].search([('name', '=', 'DOC FS')])
        return {
            'name': _('Account Analytic Line'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': self.env.ref('analytic.view_account_analytic_line_tree').id,
            'res_model': 'account.analytic.line',
            'context': "{'create': False}",
            'domain': [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'sale'), ('product_id.categ_id', 'in', product_categories.ids)],
        }
    
    def action_open_hasil_panen(self):
        self.ensure_one()
        analytic_account = self.env['account.analytic.account'].search(
                [('id', '=', self.id_mitra.id)])
        product_categories = self.env['product.category'].search([('name', '=', 'Live Bird')])
        return {
            'name': _('Account Analytic Line'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': self.env.ref('analytic.view_account_analytic_line_tree').id,
            'res_model': 'account.analytic.line',
            'context': "{'create': False}",
            'domain': [('account_id', '=', analytic_account.id), ('move_id.journal_id.type', '=', 'purchase'), ('product_id.categ_id', 'in', product_categories.ids)],
        }
    
    def action_open_journal_rhpp(self):
        self.ensure_one()
        return {
            'name': _('Journal RHPP'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'context': "{'create': False}",
            'domain': [('analytic_rhpp_id', '=', self.id)],
        }
    
    def _check_rhpp_rugi(self, data):
        doc_pakan_ovk = data.doc + data.pakan + data.obat_vaksin_kimia
        if data.live_bird < doc_pakan_ovk:
            return True
        else:
            return False
    
    def _get_jumlah_ekoran(self, data):
        jumlah_ekoran = 0
        if data.note:
            try:
                note = data.note
                if ',' in note:
                    note = note.replace(",", "")
                jumlah_ekoran = int(note)
            except ZeroDivisionError:
                jumlah_ekoran = 0 
        else:
            jumlah_ekoran = data.jumlah_ekoran
        return jumlah_ekoran
