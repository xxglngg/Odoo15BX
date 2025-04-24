# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request, content_disposition, route
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

class additional_field_product_template(models.Model):
    _inherit = 'product.template'
    _description = "Inherit Module Product Template for WMU Custom"

    scale = fields.Float()

