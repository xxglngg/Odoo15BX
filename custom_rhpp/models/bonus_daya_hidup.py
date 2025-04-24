# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class BonusDayaHidup(models.Model):
    _name = 'bonus.daya.hidup'
    _description = 'Setup and Config for Bonus Daya Hidup'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, track_visibility='always')
    unit_bdh = fields.Many2many('unit.rhpp', string='Unit', required=True, track_visibility='always')
    presentasi_hidup = fields.Float(string='Presentasi Hidup', required=True, track_visibility='always')
    nilai_bonus = fields.Integer(string='Nilai Bonus/Ekor Panen', required=True, track_visibility='always')
    date = fields.Date(string='Date', required=True)
    active = fields.Boolean(default=True)

    # @api.onchange('name')
    # def _onchange_name(self):
    #     print(self)

    #     check_unit = self.env['bonus.daya.hidup'].search([])
    #     if check_unit.unit_bdh:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit_bdh.ids)])
    #         return {'domain':
    #             {
    #                 'unit_bdh': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # def write(self, vals):

    #     print(self)
    #     if 'unit_bdh' in vals:
    #         data_unit = []
    #         check_array = vals['unit_bdh'][0][2]

    #         if len(self.unit_bdh.ids)>1:
    #             for data in self.unit_bdh.ids:
    #                 if data in check_array:
    #                     check_array.remove(data)
    #                     data_unit.append(data)

    #         else:
    #             if self.unit_bdh.id in check_array:
    #                 check_array.remove(self.unit_bdh.id)
    #                 data_unit.append(self.unit_bdh.id)


    #         for data_out in check_array:
    #             check_unit = self.env['bonus.daya.hidup'].search([('unit_bdh', '=', data_out)])
    #             if check_unit:
    #                 unit = self.env['unit.rhpp'].search([('id','=',data_out)])
    #                 raise UserError("%s Sudah Terpakai"% unit.name)

    #         for data_array in check_array:
    #             data_unit.append(data_array)
    #         vals['unit_bdh'] = [(6,0,data_unit)]


    #         super(BonusDayaHidup, self).write(vals)
    #     else:
    #         super(BonusDayaHidup, self).write(vals)

    # @api.onchange('unit_bdh')
    # def _onchange_unit_bdh(self):
    #     print(self)

    #     check_unit = self.env['bonus.daya.hidup'].search([])
    #     if check_unit.unit_bdh:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit_bdh.ids)])
    #         return {'domain':
    #             {
    #                 'unit_bdh': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return