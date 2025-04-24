# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime

JENIS_KANDANG_SELECTION = [
    ('close', 'Close House'),
    ('semi', 'Semi Close House'),
    ('open', 'Open House'),
    ('panggung', 'Panggung'),
    ('postal', 'Postal'),
]

TINGKAT_KANDANG_SELECTION = [
    ('1', '1 Tingkat'),
    ('2', '2 Tingkat'),
    ('3', '3 Tingkat'),
    ('4', '4 Tingkat'),
    ('5', '5 Tingkat'),
    ('6', '6 Tingkat'),
    ('7', '7 Tingkat'),
    ('8', '8 Tingkat'),
    ('9', '9 Tingkat'),
    ('10', '10 Tingkat'),
    ('11', '11 Tingkat'),
    ('12', '12 Tingkat'),
    ('13', '13 Tingkat'),
    ('14', '14 Tingkat'),
    ('15', '15 Tingkat'),
    ('16', '16 Tingkat'),
    ('17', '17 Tingkat'),
    ('18', '18 Tingkat'),
    ('19', '19 Tingkat'),
    ('20', '20 Tingkat'),
    ('21', '21 Tingkat'),
    ('22', '22 Tingkat'),
    ('23', '23 Tingkat'),
    ('24', '24 Tingkat'),
    ('25', '25 Tingkat'),
    ('26', '26 Tingkat'),
    ('27', '27 Tingkat'),
    ('28', '28 Tingkat'),
    ('29', '29 Tingkat'),
    ('30', '30 Tingkat'),
    ('31', '31 Tingkat'),
    ('32', '32 Tingkat'),
    ('33', '33 Tingkat'),
    ('34', '34 Tingkat'),
    ('35', '35 Tingkat'),
    ('36', '36 Tingkat'),
    ('37', '37 Tingkat'),
    ('38', '38 Tingkat'),
    ('39', '39 Tingkat'),
    ('40', '40 Tingkat'),
    ('41', '41 Tingkat'),
    ('42', '42 Tingkat'),
    ('43', '43 Tingkat'),
    ('44', '44 Tingkat'),
    ('45', '45 Tingkat'),
    ('46', '46 Tingkat'),
    ('47', '47 Tingkat'),
    ('48', '48 Tingkat'),
    ('49', '49 Tingkat'),
    ('50', '50 Tingkat'),
]

class PopulasiKandang(models.Model):
    _name = 'populasi.kandang'
    _description = 'Setup and Config for Populasi Kandang'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Nama Kandang", required=True)
    
    kode_kandang = fields.Char(string="Kode Kandang", readonly=True, select=True, copy=False, default='New', compute="_compute_kode_kandang")
    peternak = fields.Many2one('res.partner', string="Peternak", domain="[('category_id.name', '=', 'peternak')]", required=True)
    jenis_kandang = fields.Selection(JENIS_KANDANG_SELECTION, string="Jenis Kandang", default='close', track_visibility='always')
    tingkat_kandang = fields.Selection(TINGKAT_KANDANG_SELECTION, string="Tingkat Kandang", default='1', track_visibility='always')
    unit_kandang = fields.Many2one('unit.rhpp', string="Unit", required=True, track_visibility='always')

    populasi = fields.Float(string="Populasi", required=True)
    provinsi = fields.Many2one("res.country.state", string='Provinsi', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    kota_kabupaten = fields.Char(string="Kota/Kabupaten")
    kecamatan = fields.Char(string="Kecamatan")
    alamat_kandang = fields.Char(string="Alamat Kandang")
    nomor_kandang = fields.Char(string="Nomor Kandang", required=True)

    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', readonly=True, default= lambda self: self.env['res.country'].search([('name', '=', 'Indonesia')], limit=1))
    active = fields.Boolean(string="Is Active", default=True)
    
    @api.depends('nomor_kandang', 'peternak')
    def _compute_kode_kandang(self):
        for rec in self:
            rec.kode_kandang = 'New'
            if rec.peternak and rec.nomor_kandang:
                code_peternak = self.env['res.partner'].search([('id', '=', rec.peternak.id)]).ref
                if code_peternak:
                    rec.kode_kandang = code_peternak+'/'+rec.nomor_kandang       
