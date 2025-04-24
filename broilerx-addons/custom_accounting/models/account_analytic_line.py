from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    note = fields.Char(string="Note", compute='_compute_analytic_note')
    jumlah_ekoran = fields.Float(string="Jumlah Ekoran", compute='_compute_analytic_jumlah_ekoran')

    def _compute_analytic_note(self):
        for rec in self:
            rec.note = ''
            if rec.move_id.note:
                rec.note = rec.move_id.note
    
    def _compute_analytic_jumlah_ekoran(self):
        for rec in self:
            rec.jumlah_ekoran = 0
            if rec.move_id.jumlah_ekoran:
                rec.jumlah_ekoran = rec.move_id.jumlah_ekoran
