# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class PricelistSapronakRHPP(models.Model):
    _name = 'pricelist.sapronak.rhpp'
    _description = 'Form Pricelist Sapronak'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    unit = fields.Many2many('unit.rhpp', string='Unit', required=True, tracking=True)
    harga_doc_vaksin = fields.Monetary()
    harga_prestarter = fields.Monetary()
    harga_starter = fields.Monetary()
    harga_finisher = fields.Monetary()
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    date = fields.Date(string='Date', required=True)
    active = fields.Boolean(default=True)

    # @api.onchange('name')
    # def _onchange_name(self):
    #     print(self)

    #     check_unit = self.env['pricelist.sapronak.rhpp'].search([])
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
    #             check_unit = self.env['pricelist.sapronak.rhpp'].search([('unit', '=', data_out)])
    #             if check_unit:
    #                 unit = self.env['unit.rhpp'].search([('id','=',data_out)])
    #                 raise UserError("%s Sudah Terpakai"% unit.name)

    #         for data_array in check_array:
    #             data_unit.append(data_array)
    #         vals['unit'] = [(6,0,data_unit)]


    #         super(PricelistSapronakRHPP, self).write(vals)
    #     else:
    #         super(PricelistSapronakRHPP, self).write(vals)

    # @api.onchange('unit')
    # def _onchange_unit(self):
    #     print(self)

    #     check_unit = self.env['pricelist.sapronak.rhpp'].search([])
    #     if check_unit.unit:
    #         check_unit = self.env['unit.rhpp'].search([('id', 'not in', check_unit.unit.ids)])
    #         return {'domain':
    #             {
    #                 'unit': [('id', 'in', check_unit.ids)],

    #             }
    #         }
    #     return