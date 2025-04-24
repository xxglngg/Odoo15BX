# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class BonusPasar(models.Model):
    _name = 'bonus.pasar'
    _description = 'Setup and Config for Bonus pasar'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, track_visibility='always')
    unit_bp = fields.Many2many('unit.rhpp', string='Unit', required=True, track_visibility='always')
    bonus_pasar_line = fields.One2many('bonus.pasar.line','bonus_pasar_id')
    date = fields.Date(string='Date', required=True)
    active = fields.Boolean(default=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if len(self.bonus_pasar_line) > 0:
            line_ids = self.bonus_pasar_line
            data = []
            for line in line_ids:
                data.append((0,0,{
                    'diff_fcr_start' : line.diff_fcr_start,
                    'diff_fcr_end': line.diff_fcr_end,
                    'presentase_bonus':line.presentase_bonus
                    }))
            default['bonus_pasar_line'] = data
        return super(BonusPasar, self).copy(default)

    # @api.onchange('name')
    # def _onchange_name(self):
    #     print(self)

    #     check_unit = self.env['bonus.pasar'].search([])
    #     if check_unit.unit_bp:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit_bp.ids)])
    #         return {'domain':
    #             {
    #                 'unit_bp': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # @api.onchange('unit_bp')
    # def _onchange_unit_bp(self):
    #     print(self)

    #     check_unit_jenis_kandang = self.env['bonus.pasar'].search([])
    #     if check_unit_jenis_kandang.unit_bp:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit_jenis_kandang.unit_bp.ids)])
    #         return {'domain':
    #             {
    #                 'unit_bp': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # def write(self, vals):

    #     print(self)
    #     if 'unit_bp' in vals:
    #         data_unit = []
    #         check_array = vals['unit_bp'][0][2]

    #         if len(self.unit_bp.ids)>1:
    #             for data in self.unit_bp.ids:
    #                 if data in check_array:
    #                     check_array.remove(data)
    #                     data_unit.append(data)

    #         else:
    #             if self.unit_bp.id in check_array:
    #                 check_array.remove(self.unit_bp.id)
    #                 data_unit.append(self.unit_bp.id)


    #         for data_out in check_array:
    #             check_unit = self.env['bonus.pasar'].search([('unit_bp', '=', data_out)])
    #             if check_unit:
    #                 unit = self.env['unit.rhpp'].search([('id','=',data_out)])
    #                 raise UserError("%s Sudah Terpakai"% unit.name)

    #         for data_array in check_array:
    #             data_unit.append(data_array)
    #         vals['unit_bp'] = [(6,0,data_unit)]


    #         super(BonusPasar, self).write(vals)
    #     else:
    #         super(BonusPasar, self).write(vals)
    
class BonusPasarLine(models.Model):
    _name = 'bonus.pasar.line'
    _description = 'Setup and Config for Bonus Pasar Line'

    diff_fcr_start = fields.Char(string='Diff FCR Start', required=True, track_visibility='always', default="0.000")
    diff_fcr_end = fields.Char(string='Diff FCR End', track_visibility='always', default="0.000")
    presentase_bonus = fields.Float(string='Presentase Bonus', track_visibility='always')
    bonus_pasar_id = fields.Many2one('bonus.pasar')