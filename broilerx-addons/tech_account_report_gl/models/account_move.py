from odoo import _, api, fields, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    no_sj = fields.Char(string='No. SJ', related='move_id.no_sj')
