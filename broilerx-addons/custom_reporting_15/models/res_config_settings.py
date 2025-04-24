# -*- coding: utf-8 -*-
#############################################################################

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_signature = fields.Char(string="Default Invoice Signature", config_parameter='invoice_signature')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        data = ICPSudo.get_param('invoice_signature')
        res.update({'invoice_signature':data})
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('invoice_signature', self.invoice_signature)
        return res