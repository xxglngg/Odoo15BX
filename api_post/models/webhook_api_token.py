from odoo import models, fields, api

class WebhookApiToken(models.Model):
    _name = "webhook.api.token"
    
    token = fields.Text(string="Token")
    active = fields.Boolean(string="Is Active", default=True)
