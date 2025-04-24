from odoo import models, fields, api


class CompanyProductRel(models.Model):
    _name = 'company.product.rel'

    name = fields.Char(string='Name')
    company_ids = fields.Many2many('res.company', string='Company')
    product_categ_ids = fields.Many2many('product.category', string='Product Category')
