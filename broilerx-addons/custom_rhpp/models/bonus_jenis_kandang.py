# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

KANDANG_BJK_SELECTION = [
    ('close', 'Close House'),
    ('semi', 'Semi Close House'),
    ('open', 'Open House'),
    ('panggung', 'Panggung'),
    ('postal', 'Postal'),
]

class BonusJenisKandang(models.Model):
    _name = 'bonus.jenis.kandang'
    _description = 'Setup and Config for Bonus Jenis Kandang'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, track_visibility='always')
    unit_bjk = fields.Many2many('unit.rhpp', string='Unit', required=True, track_visibility='always')
    date = fields.Date(string='Date', required=True)
    active = fields.Boolean(default=True)
    bonus_jenis_kandang_type_ids = fields.One2many('bonus.jenis.kandang.type','bonus_jenis_kandang_id')

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if len(self.bonus_jenis_kandang_type_ids) > 0:
            line_ids = self.bonus_jenis_kandang_type_ids
            data = []
            for line in line_ids:
                data.append((0,0,{
                    'kandang_bjk' : line.kandang_bjk,
                    'nilai_bonus': line.nilai_bonus
                    }))
            default['bonus_jenis_kandang_type_ids'] = data
        return super(BonusJenisKandang, self).copy(default)

    # @api.onchange('name')
    # def _onchange_name(self):
    #     print(self)

    #     check_unit_jenis_kandang = self.env['bonus.jenis.kandang'].search([])
    #     if check_unit_jenis_kandang.unit_bjk:
    #         check_unit = self.env['unit.rhpp'].search([('id','not in',check_unit_jenis_kandang.unit_bjk.ids)])
    #         return {'domain':
    #                     {
    #                         'unit_bjk': [('id', 'in', check_unit.ids)],

    #                      }
    #                 }
    #     return

    # @api.onchange('unit_bjk')
    # def _onchange_unit_bjk(self):
    #     print(self)

    #     check_unit_jenis_kandang = self.env['bonus.jenis.kandang'].search([])
    #     if check_unit_jenis_kandang.unit_bjk:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit_jenis_kandang.unit_bjk.ids)])
    #         return {'domain':
    #             {
    #                 'unit_bjk': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # def write(self, vals):

    #     print(self)
    #     if 'unit_bjk' in vals:
    #         data_unit = []
    #         check_array = vals['unit_bjk'][0][2]

    #         if len(self.unit_bjk.ids)>1:
    #             for data in self.unit_bjk.ids:
    #                 check_array.remove(data)
    #                 data_unit.append(data)

    #         else:
    #             check_array.remove(self.unit_bjk.id)
    #             data_unit.append(self.unit_bjk.id)


    #         for data_out in check_array:
    #             check_unit_jenis_kandang_out = self.env['bonus.jenis.kandang'].search([('unit_bjk', '=', data_out)])
    #             if check_unit_jenis_kandang_out:
    #                 unit = self.env['unit.rhpp'].search([('id','=',data_out)])
    #                 raise UserError("%s Sudah Terpakai"% unit.name)

    #         for data_array in check_array:
    #             data_unit.append(data_array)
    #         vals['unit_bjk'] = [(6,0,data_unit)]


    #         super(BonusJenisKandang, self).write(vals)
    #     else:
    #         super(BonusJenisKandang, self).write(vals)



    # def _get_unit_selection(self):
    #     print(self)
    #     check_unit_jenis_kandang = self.env['bonus.jenis.kandang'].search([])
    #     if check_unit_jenis_kandang.unit_bjk:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit_jenis_kandang.unit_bjk.ids)])

    #         self.unit_bjk = check_unit.ids

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     print(self)

class BonusJenisKandangType(models.Model):
    _name = 'bonus.jenis.kandang.type'
    _description = 'Bonus Jenis Kandang Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    kandang_bjk = fields.Selection(KANDANG_BJK_SELECTION, string='Jenis Kandang', required=True,track_visibility='always')
    nilai_bonus = fields.Integer(string='Nilai Bonus/Ekor', required=True, track_visibility='always')
    bonus_jenis_kandang_id = fields.Many2one('bonus.jenis.kandang')