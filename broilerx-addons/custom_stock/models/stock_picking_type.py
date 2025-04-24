# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json

class StockPicking(models.Model):
    _inherit = 'stock.picking.type'

    multi_location = fields.Boolean('Multi Location')