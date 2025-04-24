# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime

STATE_SELECTION = [
    ('new', 'New'),
    ('ready', 'Ready'),
    ('running', 'Running'),
    ('expired', 'Expired'),
    ('cancel', 'Cancel'),
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

class FormKontrakPeternak(models.Model):
    _name = 'form.kontrak.peternak'
    _description = 'Form Kontrak Peternak'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    state = fields.Selection(STATE_SELECTION, string='State',default='new', track_visibility='always')
    company_id = fields.Many2one('res.company', store=True, copy=False, string="Company", default=lambda self: self.env.user.company_id.id)
    
    name = fields.Char(string="Name", select=True, copy=False, default='New')
    populasi_kandang = fields.Many2one('populasi.kandang', string="Kandang", required=True, track_visibility='always')
    analytic_account = fields.Many2one('account.analytic.account', string="Analytic Account", select=True, copy=False)
    contact_peternak = fields.Many2one('res.partner', string="Peternak", readonly=True)
    nik = fields.Char(string="NIK", readonly=True)
    alamat = fields.Char(string="Alamat", readonly=True)
    populasi = fields.Float(string="Populasi", required=True)
    ovk = fields.Char(string="OVK", compute='_compute_default_ovk', default='Sesuai Kebutuhan', readonly=True)
    unit = fields.Many2one('unit.rhpp', string="Unit", readonly=True)
    jenis_kontrak = fields.Selection(JENIS_KONTRAK_SELECTION, string="Jenis Kontrak", default='farming', track_visibility='always')

    no_surat_pp_23 = fields.Char(string="No. Surat PP 23")
    template_kontrak_id = fields.Many2one('template.kontrak', string="Template Kontrak Peternak", required=True)
    # pricelist_ayam = fields.Many2one('pricelist.ayam.rhpp', string="Pricelist Ayam")
    # pricelist_sapronak = fields.Many2one('pricelist.sapronak.rhpp', string="Pricelist Sapronak")
    file_kontrak = fields.Binary(string="File Kontrak")
    filename = fields.Char(string="File Name")
    jenis_kandang = fields.Selection(JENIS_KANDANG_SELECTION, string="Jenis Kandang", readonly=True)
    contact_doc_in = fields.Date(string="Tgl DOC in", required=True)
    contract_ppl = fields.Char(string="PPL")
    # contract_tanggal_pengajuan = fields.Date(string="Tanggal Pengajuan")
    contract_periode = fields.Char(string="Periode", required=True)
    tanggal_surat = fields.Date(string="Tanggal Surat")
    is_periode_pertama = fields.Boolean(string="Cetak Kontrak PKS", default=False)
    # klausul_id = fields.Many2one('klausul.kontrak', string="Klausul Kontrak")
    # klausul_kontrak_line = fields.One2many('klausul.kontrak.line',
    #                             'klausul_id',
    #                             'Klausul Kontrak')
    # bonus_jenis_kandang_id = fields.Many2one('bonus.jenis.kandang', string="Bonus Jenis Kandang")
    # bonus_ip_id = fields.Many2one('bonus.ip', string="Bonus IP")
    # bonus_capaian_fcr_id = fields.Many2one('bonus.capaian.fcr', string="Bonus Capaian FCR")
    # bonus_pasar_id = fields.Many2one('bonus.pasar', string="Bonus Pasar")
    # bonus_daya_hidup_id = fields.Many2one('bonus.daya.hidup', string="Bonus Daya Hidup")
    is_running_transaction = fields.Boolean(string="Apakah Transaksi Berjalan")
    name_operasional = fields.Char(string="Name Operasional", compute='compute_name_jabatan_operasional')
    jabatan_operasional = fields.Char(string="Jabatan Operasional", compute='compute_name_jabatan_operasional')
    nomor_surat_operasional = fields.Char(string="Nomor Surat Operasional", compute='compute_name_jabatan_operasional')
    kop_surat_operasional = fields.Binary(string="Kop Surat Operasional", compute='compute_name_jabatan_operasional')
    is_have_pricelist = fields.Float(compute='_compute_is_have_pricelist', string='Is Have Pricelist')
    is_have_insentif = fields.Float(compute='_compute_is_have_insentif', string='Is Have Insentif')

    # @api.depends('contract_periode')
    # def _compute_is_periode_pertama(self):
    #     for rec in self:
    #         if rec.contract_periode == '1':
    #             rec.is_periode_pertama = True
    #         if rec.contract_periode != '1':
    #             rec.is_periode_pertama = False

    def action_print_perjanjian_mitra_peternak(self):
        return self.env.ref('custom_rhpp.action_report_perjanjian_mitra_peternak').report_action(self)

    def compute_name_jabatan_operasional(self):
        for rec in self:
            name_jabatan = self.env['nama.jabatan'].search([('jabatan', 'ilike', 'Direktur Operasional')], limit=1)
            if name_jabatan:
                rec.name_operasional = name_jabatan.name
                rec.jabatan_operasional = name_jabatan.jabatan
                rec.nomor_surat_operasional = str(name_jabatan.kode) + "." + name_jabatan.nomor + "/" + name_jabatan.perusahaan + "/" + name_jabatan.bulan + "/" + str(name_jabatan.tahun)
                rec.kop_surat_operasional = name_jabatan.kop_surat
            else:
                rec.name_operasional = False
                rec.jabatan_operasional = False
                rec.nomor_surat_operasional = False
                rec.kop_surat_operasional = False

    @api.onchange('unit')
    def _onchange_unit_kontrak(self):
        print(self)
        for data_self in self:
            if data_self.unit:
                id_unit = data_self.unit.id
            else:
                id_unit = 0
            return {'domain':
                        {
                            'template_kontrak_id': [('unit_ids', '=', id_unit)],
                         }
                    }
    
    def action_print_kontrak_peternak(self):
        return self.env.ref('custom_rhpp.action_report_kontrak_peternak').report_action(self)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            code_kandang = self.env['populasi.kandang'].search([('id', '=', vals.get('populasi_kandang'))]).kode_kandang
            if code_kandang:
                vals['name'] = code_kandang+'/'+'P'+vals['contract_periode']
        result = super(FormKontrakPeternak, self).create(vals)
        return result
    
    @api.onchange('populasi_kandang')
    def _onchange_populasi_kandang(self):
        for rec in self:
            if rec.populasi_kandang:
                for data in rec.populasi_kandang:
                    rec.populasi_kandang = data.populasi
    
    # @api.onchange('unit', 'contact_doc_in')
    # def _onchange_unit_and_doc_in(self):
    #     for rec in self:
    #         rec.bonus_jenis_kandang_id = False
    #         rec.bonus_ip_id = False
    #         rec.bonus_capaian_fcr_id = False
    #         rec.bonus_pasar_id = False
    #         rec.bonus_daya_hidup_id = False
    #         if rec.unit and rec.contact_doc_in:
    #             self.bonus_ip_id = self.env['bonus.ip'].search([('unit_bip', 'in', [rec.unit.id]) ,('date', '<=', rec.contact_doc_in), ('active', '=', True)], limit=1)
    #             self.bonus_capaian_fcr_id = self.env['bonus.capaian.fcr'].search([('unit_bcf', 'in', [rec.unit.id]) ,('date', '<=', rec.contact_doc_in), ('active', '=', True)], limit=1)
    #             self.bonus_pasar_id = self.env['bonus.pasar'].search([('unit_bp', 'in', [rec.unit.id]) ,('date', '<=', rec.contact_doc_in), ('active', '=', True)], limit=1)
    #             self.bonus_daya_hidup_id = self.env['bonus.daya.hidup'].search([('unit_bdh', 'in', [rec.unit.id]) ,('date', '<=', rec.contact_doc_in), ('active', '=', True)], limit=1)
    
    @api.onchange('populasi_kandang')
    def _onchange_populasi_kandang(self):
        for data_self in self:
            if data_self.populasi_kandang:
                for data in data_self.populasi_kandang:
                    contact_peternak = data.peternak.id
                    unit = data.unit_kandang.id
                    jenis_kandang = data.jenis_kandang
                    data_self.contact_peternak = contact_peternak
                    data_self.unit = unit
                    data_self.jenis_kandang = jenis_kandang

            else:
                data_self.contact_peternak = None
                data_self.unit = None
                data_self.jenis_kandang = None
    
    @api.onchange('contact_peternak')
    def _onchange_contact_peternak(self):
        for data_self in self:
            if data_self.contact_peternak:
                for data in data_self.contact_peternak:
                    nik = data.nik
                    alamat = data.street

                    data_self.nik = nik
                    data_self.alamat = alamat

            else:
                data_self.nik = None
                data_self.alamat = None
    
    @api.onchange('is_running_transaction')
    def _onchange_is_running_transaction(self):
        for rec in self:
            if not rec.is_running_transaction:
                rec.analytic_account = False

    def _compute_default_ovk(self):
        for rec in self:
            rec.ovk = 'Sesuai Kebutuhan'
    
    def action_run_approve_rhpp(self):
        for rec in self:
            rec.state = 'ready'

    def action_run_contract_rhpp(self):
        for rec in self:
            if rec.populasi == 0.0:
                raise ValidationError(_('Populasi belum diisi, harap diisi terlebih dahulu.'))
            else:
                rec.state = 'running'
                self.create_vendor_pricelist_multiple()
                analytic_acc_obj = self.env['account.analytic.account'].search([('name', '=', rec.name)], limit=1)
                if not rec.is_running_transaction:
                    analytic_acc_obj = self.env['account.analytic.account'].search([('name', '=', rec.name),('partner_id', '=', rec.contact_peternak.id),('code', '=', rec.contact_doc_in)], limit=1).id
                    if not analytic_acc_obj:
                        analytic_acc_obj = self.env['account.analytic.account'].create(self._prepare_analytic_account_vals())
                        rec.analytic_account = analytic_acc_obj
                    else:
                        rec.analytic_account = analytic_acc_obj
                self.env['analytic.rhpp'].create(self._prepare_analytic_rhpp_vals())
    
    def create_vendor_pricelist_multiple(self):
        for rec in self:
            line_obj = rec.template_kontrak_id.pricelist_ayam.pricelist_ayam_line_ids
            for i in line_obj:
                for prd in i.mapped('product_ids').ids:
                    vals = {
                        'name': rec.contact_peternak.id,
                        'reference': rec.id,
                        'product_tmpl_id': prd,
                        'price': i.harga_ayam,
                        'date_start': fields.Date.today(),
                    }
                    self.env['product.supplierinfo'].create(vals)
  
    def _prepare_analytic_account_vals(self):
        for rec in self:
            unit_grup = self.env['account.analytic.group'].search([('unit', '=', rec.unit.id)])
            return {
                'name': rec.name,
                'partner_id': rec.contact_peternak.id,
                'group_id': unit_grup.id,
                'code': rec.contact_doc_in,
            }
    
    def _prepare_analytic_rhpp_vals(self):
        for rec in self:
            analytic_acc_obj = self.env['account.analytic.account'].search([('id', '=', rec.analytic_account.id)])
            return {
                'id_mitra': analytic_acc_obj.id,
                'name': rec.contact_peternak.id,
                'jenis_kontrak': rec.jenis_kontrak,
                'periode': rec.contract_periode,
                # 'tanggal_pengajuan': self.contract_tanggal_pengajuan,
                'unit': rec.unit.id,
                'ppl': rec.contract_ppl,
                'jenis_kandang': rec.jenis_kandang,
                'populasi': rec.populasi,
                'tanggal_doc_in': rec.contact_doc_in,
            }

    def action_cancel(self):
        self.state = 'cancel'

    # @api.onchange('unit')
    # def _depend_unit(self):
    #     print(self)

    #     for data_self in self:
    #         if data_self.unit:
    #             id_unit = data_self.unit.id
    #         else:
    #             id_unit = 0
    #         return {'domain':
    #                     {
    #                         'pricelist_ayam': [('unit', 'in', [id_unit])],
    #                         'pricelist_sapronak': [('unit', 'in', [id_unit])],

    #                      }
    #                 }

    def action_open_rhpp(self):
        action = self.env["ir.actions.actions"]._for_xml_id("custom_rhpp.analytic_rhpp_action_window")
        action.update({
            'domain': [('id_mitra','=', self.analytic_account.id),('name','=',self.contact_peternak.id),('unit','=',self.unit.id)],
            'view_mode': 'tree',
            'context': "{'groub_by': 'state'}",
            'limit': 80,
        })
        return action

    def action_open_kontrak(self):
        if self.filename:

            if self.filename.endswith('.pdf'):
                id = self.id

                context = {
                    'default_id': id,
                    'default_file_kontrak': self.file_kontrak,
                    # 'default_commercial_code': self.commercial_code,
                    # 'default_internal_code': self.internal_code,
                    # 'default_product_label_id': self.id,
                }

                # form_view_id = self.env['ir.model.data'].xmlid_to_res_id('custom_rhpp.wizard_view_pdf')
                compose_form = self.env.ref(
                    'custom_rhpp.wizard_view_pdf'
                )
                # return {
                #     'name': ('PDF view'),
                #     'type': 'ir.actions.act_window',
                #     'res_model': 'form.kontrak.peternak',
                #     'views': [(form_view_id, 'form')],
                #     'target': 'new',
                #     'res_id': self.id,
                #     'context': context,
                #     'nodestroy': True,
                # }

                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'form.kontrak.peternak',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'views': [(compose_form.id, 'form')],
                    'view_id': compose_form.id,
                    'context': context,
                    'nodestroy': True,
                    'target': 'new',
                    'res_id':id,
                }

            if self.filename.endswith('.png') or self.filename.endswith('.jpg') or self.filename.endswith('.jpeg'):
                id = self.id

                context = {
                    'default_id': id,
                    'default_file_kontrak': self.file_kontrak,
                    # 'default_commercial_code': self.commercial_code,
                    # 'default_internal_code': self.internal_code,
                    # 'default_product_label_id': self.id,
                }

                # form_view_id = self.env['ir.model.data'].xmlid_to_res_id('custom_rhpp.wizard_view_image')
                compose_form = self.env.ref(
                    'custom_rhpp.wizard_view_image'
                )
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'form.kontrak.peternak',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'views': [(compose_form.id, 'form')],
                    'view_id': compose_form.id,
                    'context': context,
                    'nodestroy': True,
                    'target': 'new',
                    'res_id': id,
                }
    
    # @api.onchange('klausul_id')
    # def _onchange_klausul_id(self):
    #     for rec in self:
    #         rec.klausul_kontrak_line = False
    #         if rec.klausul_id:
    #             rec.klausul_kontrak_line = rec.klausul_id.klausul_kontrak_line
    
    def _compute_is_have_pricelist(self):
        for rec in self:
            if rec.template_kontrak_id.pricelist_ayam:
                rec.is_have_pricelist = True
            else:
                rec.is_have_pricelist = False
   
    def _compute_is_have_insentif(self):
        for rec in self:
            if rec.template_kontrak_id.bonus_capaian_fcr_id or rec.template_kontrak_id.bonus_pasar_id or rec.template_kontrak_id.bonus_daya_hidup_id or (rec.jenis_kandang == 'semi' or rec.jenis_kandang == 'close'):
                rec.is_have_insentif = True
            else:
                rec.is_have_insentif = False
