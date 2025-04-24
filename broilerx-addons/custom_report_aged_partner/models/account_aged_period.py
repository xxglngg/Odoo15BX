from odoo import api, fields, models

SEQUENCE_SELECTION = [
                        ('1', '1'),
                        ('2', '2'),
                        ('3', '3'),
                        ('4', '4'),
                        ('5', '5')
                    ]

class AccountAgedPeriod(models.Model):
    _name = 'account.aged.period'

    name = fields.Char("Period")
    sequence = fields.Selection(SEQUENCE_SELECTION, string="Sequence")
    period_start = fields.Integer("Period Start")
    period_end = fields.Integer("Period End")
    active = fields.Boolean("Active", default=True)

