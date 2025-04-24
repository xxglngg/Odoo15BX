# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request, content_disposition, route
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

class additional_field(models.Model):
    _inherit = 'stock.warehouse'
    _description = "Additional Field In Stock Warehouse"

    kode_doc = fields.Char()