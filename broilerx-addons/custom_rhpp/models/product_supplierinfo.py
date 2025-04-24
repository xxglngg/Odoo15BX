# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'
    _description = 'Product SupplierInfo Inherit RHPP'

    reference = fields.Many2one('form.kontrak.peternak', string="Reference")