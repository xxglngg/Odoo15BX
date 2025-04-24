# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression

class ProductionTemplate(models.Model):
    _inherit = 'product.template'

    is_packaging = fields.Boolean('Is Pacakging')