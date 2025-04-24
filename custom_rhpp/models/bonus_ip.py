# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

TYPE_BIP_SELECTION = [
    ('pertonase', 'Pertonase(Kg)'),
    ('ekor', 'Jumlah Ekor'),
]

class BonusIP(models.Model):
    _name = 'bonus.ip'
    _description = 'Setup and Config for Bonus IP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, track_visibility='always')
    unit_bip = fields.Many2many('unit.rhpp', string='Unit', required=True, track_visibility='always')
    type_bip = fields.Selection(TYPE_BIP_SELECTION, string='Type Perhitungan', required=True, track_visibility='always')
    bonus_ip_line = fields.One2many('bonus.ip.line','bonus_ip_id')
    date = fields.Date(string='Date', required=True)
    active = fields.Boolean(default=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if len(self.bonus_ip_line) > 0:
            line_ids = self.bonus_ip_line
            data = []
            for line in line_ids:
                data.append((0,0,{
                    'ip_start' : line.ip_start,
                    'ip_end': line.ip_end,
                    'nominal_bonus':line.nominal_bonus
                    }))
            default['bonus_ip_line'] = data
        return super(BonusIP, self).copy(default)

    # @api.onchange('name')
    # def _onchange_name(self):
    #     print(self)

    #     check_unit = self.env['bonus.ip'].search([])
    #     if check_unit.unit_bip:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit_bip.ids)])
    #         return {'domain':
    #             {
    #                 'unit_bip': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # @api.onchange('unit_bip')
    # def _onchange_unit_bip(self):
    #     print(self)

    #     check_unit = self.env['bonus.ip'].search([])
    #     if check_unit.unit_bip:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit_bip.ids)])
    #         return {'domain':
    #             {
    #                 'unit_bip': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # def write(self, vals):

    #     print(self)
    #     if 'unit_bip' in vals:
    #         data_unit = []
    #         check_array = vals['unit_bip'][0][2]

    #         if len(self.unit_bip.ids)>1:
    #             for data in self.unit_bip.ids:
    #                 if data in check_array:
    #                     check_array.remove(data)
    #                     data_unit.append(data)

    #         else:
    #             if self.unit_bip.id in check_array:
    #                 check_array.remove(self.unit_bip.id)
    #                 data_unit.append(self.unit_bip.id)


    #         for data_out in check_array:
    #             check_unit = self.env['bonus.ip'].search([('unit_bip', '=', data_out)])
    #             if check_unit:
    #                 unit = self.env['unit.rhpp'].search([('id','=',data_out)])
    #                 raise UserError("%s Sudah Terpakai"% unit.name)

    #         for data_array in check_array:
    #             data_unit.append(data_array)
    #         vals['unit_bip'] = [(6,0,data_unit)]


    #         super(BonusIP, self).write(vals)
    #     else:
    #         super(BonusIP, self).write(vals)
    
class BonusIPLine(models.Model):
    _name = 'bonus.ip.line'
    _description = 'Setup and Config for Bonus IP Line'

    ip_start = fields.Integer(string='IP Start', required=True, track_visibility='always')
    ip_end = fields.Integer(string='IP End', track_visibility='always')
    nominal_bonus = fields.Integer(string='Nominal Bonus', track_visibility='always')
    bonus_ip_id = fields.Many2one('bonus.ip')