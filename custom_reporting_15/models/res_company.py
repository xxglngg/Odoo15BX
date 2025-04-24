from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    _columns = {
        'account_bank': fields.Many2one('res.partner.bank', string='Account Bank Company')
    }
    start_day = fields.Selection(string="Start Day", selection=[('senin', 'Senin'),
                                                            ('selasa', 'Selasa'),
                                                            ('rabu', 'Rabu'),
                                                            ('kamis', 'Kamis'),
                                                            ('jumat', 'Jumat'),
                                                            ('sabtu', 'Sabtu'),
                                                            ('minggu', 'Minggu')], required=False, )
    end_day = fields.Selection(string="End Day", selection=[('senin', 'Senin'),
                                                                ('selasa', 'Selasa'),
                                                                ('rabu', 'Rabu'),
                                                                ('kamis', 'Kamis'),
                                                                ('jumat', 'Jumat'),
                                                                ('sabtu', 'Sabtu'),
                                                                ('minggu', 'Minggu')], required=False, )
    hour_open = fields.Float(string="Open", required=False, )
    hour_close = fields.Float(string="Closed", required=False, )

    # account_bank= fields.Many2one('res.partner.bank', string='Account Bank Company')


