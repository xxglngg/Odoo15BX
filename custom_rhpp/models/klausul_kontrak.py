# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KlausulKontrak(models.Model):
    _name = 'klausul.kontrak'
    _description = 'Setup and Config for Klausul Kontrak RHPP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char('Nama')
    code = fields.Char('Kode Klausul')
    # unit_ids = fields.Many2many('unit.rhpp', string='Unit', required=True, track_visibility='always')
    # date = fields.Date('Tanggal Berlaku')
    klausul_kontrak_line = fields.One2many('klausul.kontrak.line',
                                'klausul_id',
                                'Klausul Kontrak')
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if len(self.klausul_kontrak_line) > 0:
            line_ids = self.klausul_kontrak_line
            data = []
            for line in line_ids:
                data.append((0,0,{
                    'klausul' : line.klausul,
                    'content': line.content
                    }))
            default['klausul_kontrak_line'] = data
        return super(KlausulKontrak, self).copy(default)

