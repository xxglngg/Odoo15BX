# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    product_qty = fields.Float('Quantity', compute='_product_qty', store=True)

    # def name_get(self):
    #     result = []
    #     for account in self:
    #       if account.ref:
    #         # name = '['+ account.ref +'] ' + account.name
    #         name = account.ref +' ' + account.name
    #       else:
    #         name = account.name
    #       result.append((account.id, name))
    #     return result
    #
    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = ['|', ('name', operator, name), ('ref', operator, name)]
    #     lot = self.search(domain + args, limit=limit)
    #     return lot.name_get()
