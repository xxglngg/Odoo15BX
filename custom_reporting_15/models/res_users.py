from odoo import api, fields, models




class ResUsers(models.Model):
    _inherit = 'res.users'

    user_signature = fields.Binary(string="Signature", )
