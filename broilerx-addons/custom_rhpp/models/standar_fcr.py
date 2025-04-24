# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class StandarFcr(models.Model):
    _name = 'standar.fcr'

    body_weight = fields.Float(string='Body Weight', digits=(2,3))
    feed_converion_ratio = fields.Float(string='Feed Converion Ratio', digits=(2,3))
    mortality = fields.Float(string='Mortality', digits=(2,3))
