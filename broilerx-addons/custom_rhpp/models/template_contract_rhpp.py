# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class TemplateKontrak(models.Model):
    _name = 'template.kontrak'
    _description = 'Setup and Config for Template Kontrak RHPP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    active = fields.Boolean(default=True)

    name = fields.Char(string='Name', required=True, track_visibility='always')
    template_date = fields.Date(string='Template Date', required=True)
    unit_ids = fields.Many2many('unit.rhpp', string='Unit', required=True, track_visibility='always')
    pricelist_ayam = fields.Many2one('pricelist.ayam.rhpp', string="Harga Ayam")
    pricelist_sapronak = fields.Many2one('pricelist.sapronak.rhpp', string="Harga Sapronak")
    bonus_jenis_kandang_id = fields.Many2one('bonus.jenis.kandang', string="Bonus Jenis Kandang")
    bonus_ip_id = fields.Many2one('bonus.ip', string="Bonus IP")
    bonus_pasar_id = fields.Many2one('bonus.pasar', string="Bonus Pasar")
    bonus_capaian_fcr_id = fields.Many2one('bonus.capaian.fcr', string="Bonus FCR")
    bonus_daya_hidup_id = fields.Many2one('bonus.daya.hidup', string="Bonus Daya Hidup")
    klausul_id = fields.Many2one('klausul.kontrak', string="Klausul Kontrak", required=True)
    klausul_kontrak_line = fields.One2many('klausul.kontrak.line', 'klausul_id', 'Klausul Kontrak')

    # @api.onchange('unit_ids', 'template_date')
    # def _onchange_unit_ids_and_template_date(self):
    #     for rec in self:
    #         rec.bonus_jenis_kandang_id = False
    #         rec.bonus_ip_id = False
    #         rec.bonus_capaian_fcr_id = False
    #         rec.bonus_pasar_id = False
    #         rec.bonus_daya_hidup_id = False
    #         if rec.unit_ids and rec.template_date:
    #             self.bonus_jenis_kandang_id = self.env['bonus.jenis.kandang'].search([('unit_bjk', 'in', rec.unit_ids.ids) ,('date', '<=', rec.template_date), ('active', '=', True)])
    #             self.bonus_ip_id = self.env['bonus.ip'].search([('unit_bip', 'in', rec.unit_ids.ids) ,('date', '<=', rec.template_date), ('active', '=', True)])
    #             self.bonus_capaian_fcr_id = self.env['bonus.capaian.fcr'].search([('unit_bcf', 'in', rec.unit_ids.ids) ,('date', '<=', rec.template_date), ('active', '=', True)])
    #             self.bonus_pasar_id = self.env['bonus.pasar'].search([('unit_bp', 'in', rec.unit_ids.ids) ,('date', '<=', rec.template_date), ('active', '=', True)])
    #             self.bonus_daya_hidup_id = self.env['bonus.daya.hidup'].search([('unit_bdh', 'in', rec.unit_ids.ids) ,('date', '<=', rec.template_date), ('active', '=', True)])

    @api.onchange('unit_ids')
    def _onchange_unit_template_kontrak(self):
        print(self)
        for data_self in self:
            if data_self.unit_ids:
                id_unit = data_self.unit_ids.ids
            else:
                id_unit = 0
            return {'domain':
                        {
                            'bonus_jenis_kandang_id': [('unit_bjk', 'in', id_unit)],
                            'bonus_ip_id': [('unit_bip', 'in', id_unit)],
                            'bonus_capaian_fcr_id': [('unit_bcf', 'in', id_unit)],
                            'bonus_pasar_id': [('unit_bp', 'in', id_unit)],
                            'bonus_daya_hidup_id': [('unit_bdh', 'in', id_unit)],
                            'pricelist_sapronak': [('unit', 'in', id_unit)],
                            'pricelist_ayam': [('unit', 'in', id_unit)],

                         }
                    }