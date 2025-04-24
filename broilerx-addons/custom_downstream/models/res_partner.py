# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_policy = fields.Selection([('order', 'Ordered quantities'), ('delivery', 'Delivered quantities')],
                                      string='Invoicing Policy', default='delivery')
    