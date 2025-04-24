# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

TYPE_BCF_SELECTION = [
    ('pertonase', 'Pertonase(Kg)'),
    ('ekor', 'Jumlah Ekor'),
]

class BonusCapaianFcr(models.Model):
    _name = 'bonus.capaian.fcr'
    _description = 'Setup and Config for Bonus Capaian FCR'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, track_visibility='always')
    unit_bcf = fields.Many2many('unit.rhpp', string='Unit', required=True, track_visibility='always')
    type_bcf = fields.Selection(TYPE_BCF_SELECTION, string='Type Perhitungan', required=True, track_visibility='always')
    bonus_capaian_fcr_line = fields.One2many('bonus.capaian.fcr.line','bonus_capian_fcr_id')
    date = fields.Date(string='Date', required=True)
    active = fields.Boolean(default=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if len(self.bonus_capaian_fcr_line) > 0:
            line_ids = self.bonus_capaian_fcr_line
            data = []
            for line in line_ids:
                data.append((0,0,{
                    'pencapaian_fcr_start' : line.pencapaian_fcr_start,
                    'pencapaian_fcr_end': line.pencapaian_fcr_end,
                    'nominal_bonus':line.nominal_bonus
                    }))
            default['bonus_capaian_fcr_line'] = data
        return super(BonusCapaianFcr, self).copy(default)

    # @api.onchange('name')
    # def _onchange_name(self):
    #     print(self)

    #     check_unit = self.env['bonus.capaian.fcr'].search([])
    #     if check_unit.unit_bcf:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit_bcf.ids)])
    #         return {'domain':
    #             {
    #                 'unit_bcf': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # @api.onchange('unit_bcf')
    # def _onchange_unit_bcf(self):
    #     print(self)

    #     check_unit = self.env['bonus.capaian.fcr'].search([])
    #     if check_unit.unit_bcf:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit_bcf.ids)])
    #         return {'domain':
    #             {
    #                 'unit_bcf': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # def write(self, vals):

    #     print(self)
    #     if 'unit_bcf' in vals:
    #         data_unit = []
    #         check_array = vals['unit_bcf'][0][2]

    #         if len(self.unit_bcf.ids)>1:
    #             for data in self.unit_bcf.ids:
    #                 if data in check_array:
    #                     check_array.remove(data)
    #                     data_unit.append(data)

    #         else:
    #             if self.unit_bcf.id in check_array:
    #                 check_array.remove(self.unit_bcf.id)
    #                 data_unit.append(self.unit_bcf.id)


    #         for data_out in check_array:
    #             check_unit = self.env['bonus.capaian.fcr'].search([('unit_bcf', '=', data_out)])
    #             if check_unit:
    #                 unit = self.env['unit.rhpp'].search([('id','=',data_out)])
    #                 raise UserError("%s Sudah Terpakai"% unit.name)

    #         for data_array in check_array:
    #             data_unit.append(data_array)
    #         vals['unit_bcf'] = [(6,0,data_unit)]


    #         super(BonusCapaianFcr, self).write(vals)
    #     else:
    #         super(BonusCapaianFcr, self).write(vals)

class BonusCapaianFcrLine(models.Model):
    _name = 'bonus.capaian.fcr.line'
    _description = 'Setup and Config for Bonus Capaian FCR Line'

    pencapaian_fcr_start = fields.Char(string='Pencapaian FCR Start', required=True, track_visibility='always', default="0.000")
    pencapaian_fcr_end = fields.Char(string='Pencapaian FCR End', track_visibility='always', default="0.000")
    nominal_bonus = fields.Integer(string='Nominal Bonus', track_visibility='always')
    bonus_capian_fcr_id = fields.Many2one('bonus.capaian.fcr')