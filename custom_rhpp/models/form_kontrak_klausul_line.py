# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class FormKontrakKlausulLine(models.Model):
    _name = 'klausul.kontrak.line'

    klausul = fields.Char('Klausul')
    content = fields.Html('Content')
    klausul_id = fields.Many2one('klausul.kontrak', string='Klausul Kontrak')
    form_kontrak_id = fields.Many2one('form.kontrak', string='Form Kontrak')
