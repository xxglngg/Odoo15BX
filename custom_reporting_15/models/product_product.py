from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    pcs_per_bag_ratio = fields.Float(string="PCS/Bag", related="product_tmpl_id.pcs_per_bag_ratio", readonly=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pcs_per_bag_ratio = fields.Float(string="PCS/Bag")
    company_id = fields.Many2one('res.company', string='Company', index=1, default=lambda self: self.env.user.company_id)