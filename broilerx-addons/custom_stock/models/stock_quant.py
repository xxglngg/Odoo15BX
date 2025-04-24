# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    id_inventory = fields.Char(string='ID Inventory')


    ### add field id_inventory to allowed field create stock quant ###
    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        res = super(StockQuant, self)._get_inventory_fields_create()
        res.append('id_inventory')
        # print("res",res)
        return res


    