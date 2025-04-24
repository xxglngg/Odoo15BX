# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class NamaJabatan(models.Model):
    _name = 'nama.jabatan'
    _description = 'Setup and Config for Nama Jabatan RHPP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Nama Lengkap', required=True)
    jabatan = fields.Char(string='Jabatan', required=True)
    kode = fields.Integer(string='Kode', required=True)
    nomor = fields.Char(string='Nomor', readonly=True, copy=False, default='New')
    perusahaan = fields.Char(string='Perusahaan', required=True)
    bulan = fields.Char(string='Bulan', required=True)
    tahun = fields.Integer(string='Tahun', required=True)
    kop_surat = fields.Binary(string='Kop Surat', required=True)

    @api.model
    def create(self, vals):
        if vals.get('nomor', 'New') == 'New':
            vals['nomor'] = self.env['ir.sequence'].next_by_code('sequence.nomor.nama.jabatan') or 'New'
        result = super(NamaJabatan, self).create(vals)
        return result