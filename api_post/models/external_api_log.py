from odoo import models, fields, api

class ExternalApiLog(models.Model):
    _name = "external.api.log"
    
    name = fields.Char(string="Name")
    date = fields.Datetime(string='Date', default=lambda self: fields.datetime.now())
    base_url = fields.Char(string='Base URL')
    method = fields.Char(string='Method')
    data = fields.Char(string='Data')
    response = fields.Char(string='Response')
    is_posted = fields.Boolean(string='Is Posted')
