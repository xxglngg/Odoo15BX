# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartnerSegmentasi(models.Model):
    _name = 'res.partner.segmentasi'
    _description = 'Res Partner Segmentasi'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)

    @api.constrains('code')
    def _check_code(self):
        self.ensure_one()
        domain = [
            ('id', '!=', self.id),
            ('code', 'ilike', self.code),
        ]
        existing = self.env['res.partner.segmentasi'].search_count(domain)
        if existing:
            raise ValidationError('Code segmentasi %s already exists' % (self.code))
