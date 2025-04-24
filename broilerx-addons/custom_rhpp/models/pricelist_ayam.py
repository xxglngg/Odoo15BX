# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PricelistAyamRHPP(models.Model):
    _name = 'pricelist.ayam.rhpp'
    _description = 'Form Pricelist Ayam'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    unit = fields.Many2many('unit.rhpp', string='Unit', required=True, track_visibility='always')
    pricelist_ayam_line_ids = fields.One2many('pricelist.ayam.line','pricelist_ayam_id')
    date = fields.Date(string='Date', required=True)
    active = fields.Boolean(default=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if len(self.pricelist_ayam_line_ids) > 0:
            line_ids = self.pricelist_ayam_line_ids
            data = []
            for line in line_ids:
                data.append((0,0,{
                    'product_ids' : line.product_ids,
                    'bobot_start': line.bobot_start,
                    'bobot_end':line.bobot_end,
                    'harga_ayam':line.harga_ayam
                    }))
            default['pricelist_ayam_line_ids'] = data
        return super(PricelistAyamRHPP, self).copy(default)

    @api.constrains('pricelist_ayam_line_ids')
    def _check_pricelist_ayam_line_ids(self):
        self.ensure_one()
        if self.pricelist_ayam_line_ids:
            for rec in self.pricelist_ayam_line_ids:
                if rec.harga_ayam == 0:
                    raise ValidationError(_('Harga Live Bird tidak boleh bernilai 0. Mohon masukkan harga yang valid untuk melanjutkan!'))
    
    def action_open_contract(self):
        return None
    
    def action_open_partners(self):
        return None

    # @api.onchange('name')
    # def _onchange_name(self):
    #     print(self)

    #     check_unit = self.env['pricelist.ayam.rhpp'].search([])
    #     if check_unit.unit:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit.ids)])
    #         return {'domain':
    #             {
    #                 'unit': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # @api.onchange('unit')
    # def _onchange_unit(self):
    #     print(self)

    #     check_unit = self.env['pricelist.ayam.rhpp'].search([])
    #     if check_unit.unit:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit.ids)])
    #         return {'domain':
    #             {
    #                 'unit': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return

    # def write(self, vals):

    #     print(self)
    #     if 'unit' in vals:
    #         data_unit = []
    #         check_array = vals['unit'][0][2]

    #         if len(self.unit.ids)>1:
    #             for data in self.unit.ids:
    #                 if data in check_array:
    #                     check_array.remove(data)
    #                     data_unit.append(data)

    #         else:
    #             if self.unit.id in check_array:
    #                 check_array.remove(self.unit.id)
    #                 data_unit.append(self.unit.id)


    #         for data_out in check_array:
    #             check_unit = self.env['pricelist.ayam.rhpp'].search([('unit', '=', data_out)])
    #             if check_unit:
    #                 unit = self.env['unit.rhpp'].search([('id','=',data_out)])
    #                 raise UserError("%s Sudah Terpakai"% unit.name)

    #         for data_array in check_array:
    #             data_unit.append(data_array)
    #         vals['unit'] = [(6,0,data_unit)]


    #         super(PricelistAyamRHPP, self).write(vals)
    #     else:
    #         super(PricelistAyamRHPP, self).write(vals)

class PricelistAyamLine(models.Model):
    _name = 'pricelist.ayam.line'
    _description = 'Pricelist Ayam Line'

    product_ids = fields.Many2many('product.template', string='Product', required=True, track_visibility='always', domain="[('categ_id.name', '=', 'Live Bird')]")
    bobot_start = fields.Float(string='Bobot Start', required=True, track_visibility='always')
    bobot_end = fields.Float(string='Bobot End', track_visibility='always')
    harga_ayam = fields.Float(string='Harga Ayam', track_visibility='always')
    pricelist_ayam_id = fields.Many2one('pricelist.ayam.rhpp')