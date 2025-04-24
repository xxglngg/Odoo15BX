# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sequence = fields.Integer(string='Delivery Order', default=1)
    address = fields.Char(related='partner_id.street', string='Address')
    mobile = fields.Char(related='partner_id.mobile', string='Phone Number')
    operation_type_code = fields.Selection(related='picking_type_id.code', string='Operation Type', store=True)
    is_trading_karkas = fields.Boolean('Is Trading Karkas', compute="_compute_is_trading_karkas")

    def _compute_is_trading_karkas(self):
        group_downstream_team = self.env.user.has_group('custom_downstream.group_broilerx_downstream')   

        is_trading_karkas = group_downstream_team
        for rec in self:
            rec.is_trading_karkas = is_trading_karkas or False


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    price_unit = fields.Integer(string='Price Unit')