from odoo import fields, models, api


class StorageCategory(models.Model):
    _inherit = "stock.storage.category"

    allow_new_product = fields.Selection([
        ('empty', 'If the location is empty'),
        ('same', 'If all products are same'),
        ('two_products', 'Allow max 2 products'),
        ('mixed', 'Allow mixed products')], default='mixed', required=True)
