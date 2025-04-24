# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

REGION_SELECTION = [
    ('jateng', 'Jawa Tengah'),
    ('jatim', 'Jawa Timur'),
    ('lampung', 'Lampung'),
]

class UnitRhpp(models.Model):
    _name = 'unit.rhpp'
    _description = 'Setup and Config for Unit RHPP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    short_code = fields.Char(string='Short Code', size=5, required=True, track_visibility='always')
    name = fields.Char(string='Unit', required=True, track_visibility='always')
    region = fields.Selection(REGION_SELECTION, string='Region', required=True, track_visibility='always')
    color = fields.Integer('Color Index', default=0)

    @api.constrains('short_code')
    def _check_short_code(self):
        self.ensure_one()
        domain = [
            ('id', '!=', self.id),
            ('short_code', 'ilike', self.short_code),
        ]
        existing = self.env['unit.rhpp'].search_count(domain)
        if existing:
            raise ValidationError('Unit rhpp %s already exists' % (self.short_code))
