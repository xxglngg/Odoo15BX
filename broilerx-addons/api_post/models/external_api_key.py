from odoo import models, fields, api
import json
import requests
from uuid import uuid4
from odoo.exceptions import UserError
from urllib.parse import urlparse

class ExternalApiKey(models.Model):
    _name = "external.api.key"
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    base_url = fields.Char(string='Base URL',required=True)
    endpoint_url = fields.Char(string='Endpoint URL')
    username = fields.Char(string='Username',required=True)
    password = fields.Char(string='Password',required=True)
    token = fields.Text('Token', readonly=True)
    
    def generate_token(self):
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache",'User-Agent': 'ODOO_DEV'}
        json_data = {'username': self.username, 'password': self.password}
        response = requests.post(self.base_url, data=json.dumps(json_data), headers=headers)
        token = response.json()
        if 'accessToken' not in token:
            raise UserError(("API response connection Gagal, check Username dan Password"))
        self.write({'token': token['accessToken']})
