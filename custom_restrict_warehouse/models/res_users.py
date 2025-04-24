from odoo import api, fields, models


class ResUsers(models.Model):
    """This model adds additional fields to the `res.users` model to restrict
     user access to certain locations and warehouses."""
    _inherit = 'res.users'
    
    allowed_warehouse_ids = fields.Many2many(
        comodel_name='stock.warehouse', string='Allowed Warehouse',
        help='Allowed Warehouse for user.')
