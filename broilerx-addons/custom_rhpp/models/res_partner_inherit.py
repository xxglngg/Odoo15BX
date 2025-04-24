from odoo import models, fields, api
from odoo.exceptions import UserError
import json
from urllib.parse import urlparse
from odoo.exceptions import UserError, ValidationError
import requests

class InheritResPartnerRHPP(models.Model):
    _inherit = 'res.partner'
    _description = 'Data Contract from Contact Res Partner RHPP'

    nik = fields.Char(size=16)
    is_peternak = fields.Boolean('peternak', compute='_compute_is_peternak')
    is_form_peternak = fields.Boolean('is form peternak', compute='_compute_is_form_peternak', default=False)
    category_id_domain = fields.Char(compute="_compute_category_id_domain", readonly=True, store=False)
    unit_rhpp = fields.Many2one('unit.rhpp', string="Unit", tracking=True)
    company_ids = fields.Many2many('res.company', string='Allowed Companies')
    company_id = fields.Many2one('res.company', string='Default Company', default=lambda self: self.env.company)
    is_company_itu = fields.Boolean('Is Company ITU', compute="_compute_is_company_itu", store=True)

    @api.constrains('nik')
    def _check_nik_length(self):
        for record in self:
            if record.nik:
                if len(record.nik) != 16 or not record.nik.isdigit():
                    raise ValidationError("NIK must be exactly 16 digits long and contain only numbers.")
    
    @api.depends('company_id')
    def _compute_is_company_itu(self):
        for rec in self:
            rec.is_company_itu = False
            if rec.company_id.name == 'PT Integrasi Teknologi Unggas':
                rec.is_company_itu = True
    
    @api.constrains('nik')
    def _check_nik(self):
        self.ensure_one()
        domain = [
            ('id', '!=', self.id),
            ('nik', '=', self.nik),
            ('category_id', '=', 'peternak')
        ]
        existing = self.env['res.partner'].search_count(domain)
        if existing:
            if self.is_company_itu == True:
                raise ValidationError('Nik %s already exists' % (self.nik))

    def _compute_is_form_peternak(self):
        for rec in self:
            check_active = self.env.context.get('res_partner_active')
            if check_active == 'active':
                rec.is_form_peternak = True
            else:
                rec.is_form_peternak = False

    @api.depends('is_peternak')
    def _compute_category_id_domain(self):
        for rec in self:
            if rec.is_form_peternak == True:
                rec.category_id_domain = json.dumps([('name', '=', 'peternak')])
            else:
                rec.category_id_domain = json.dumps([])
    
    @api.depends('category_id')
    def _compute_is_peternak(self):
        for rec in self:
            rec.is_peternak = False
            if rec.category_id:
                for category in rec.category_id:
                    if category.name == 'peternak':
                        rec.is_peternak = True
        
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        check_domain = len(domain)

        check_active = self.env.context.get('res_partner_active')
        print(check_active)
        res = super(InheritResPartnerRHPP, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
                                                             order=order)
        if check_active == 'active':

            if check_domain > 0:
                check_category = self.env['res.partner.category'].search([('name', '=', 'peternak')])
                domain.append(['category_id', '=', check_category.id])
            else:
                check_category = self.env['res.partner.category'].search([('name','=','peternak')])
                domain =[('category_id', '=', check_category.id)]
                data_partner = self.env['res.partner'].search([('category_id','=',check_category.id)])
                limit = len(data_partner.ids)
            res = super(InheritResPartnerRHPP, self).search_read(domain=domain, fields=fields, offset=offset,
                                                                 limit=limit,
                                                                 order=order)
        return res
    
    # @api.model
    # def create(self, vals):
    #     result = super(InheritResPartnerRHPP, self).create(vals)
    #     is_api = self.env.context.get('api_action')
    #     if not is_api:
    #         for rec in result:
    #             if rec.is_peternak:
    #                 base_url = 'https://app-be-dev.broilerx.com/v1/farmers/odoo'
    #                 api_apps = self.env['external.api.key'].search([('code', '=', 'api_apps_user')])
    #                 if not api_apps:
    #                     raise UserError(("Contact admin for settings external api key api_apps_user"))
    #                 api_apps.generate_token()
    #                 headers = {
    #                     "Content-Type": "application/json", 
    #                     "Accept": "application/json", 
    #                     "Catch-Control": "no-cache",
    #                     'Authorization':"Bearer "+api_apps.token,
    #                     'User-Agent': 'ODOO_DEV'
    #                 }
    #                 phone_numbers = rec.phone
    #                 if phone_numbers:
    #                     if phone_numbers[0] == '0':
    #                         phone_numbers = phone_numbers.replace('0', '62')
    #                     if phone_numbers[0:3] == '+62':
    #                         phone_numbers = phone_numbers.replace('+', '')
    #                         phone_numbers = phone_numbers.replace('-', '')
    #                         phone_numbers = phone_numbers.replace(' ', '')
    #                 json_data = {
    #                     "code": rec.ref,
    #                     "fullName": rec.name,
    #                     "phoneNumber": phone_numbers,
    #                     "odooId": rec.id
    #                 }
    #                 response = requests.post(base_url, data=json.dumps(json_data), headers=headers)
    #                 res = response.json()
    #                 if 'error' in res:
    #                     if type(res['error']) != str:
    #                         if 'phoneNumber' in res['error']:
    #                             raise UserError(('[Integration APPS] message : '+res['error']['phoneNumber']))
    #                         elif 'code' in res['error']:
    #                             raise UserError(('[Integration APPS] message : '+res['error']['code']))
    #                         elif 'odooId' in res['error']:
    #                             raise UserError(('[Integration APPS] message : '+res['error']['odooId']))
    #                         else:
    #                             raise UserError((json.dumps(res)))
    #                     else:    
    #                         raise UserError(('[Integration APPS] message : '+res['error']))
    #                 else:
    #                     logs = {
    #                         'name': 'API Create Peternak',
    #                         'base_url': base_url,
    #                         'method': 'POST',
    #                         'data': json_data,
    #                         'response': res,
    #                         'is_posted': True
    #                     }
    #                     self.env['external.api.log'].create(logs)
    #     return result
    
    # def write(self, vals):
    #     result = super(InheritResPartnerRHPP, self).write(vals)
    #     is_api = self.env.context.get('api_action')
    #     if not is_api:
    #         if vals.get('ref') or vals.get('name') or vals.get('phone'):
    #             for rec in self:
    #                 if rec.is_peternak:
    #                     base_url = 'https://app-be-dev.broilerx.com/v1/farmers/odoo'
    #                     api_apps = self.env['external.api.key'].search([('code', '=', 'api_apps_user')])
    #                     if not api_apps:
    #                         raise UserError(("Contact admin for settings external api key api_apps_user"))
    #                     api_apps.generate_token()
    #                     headers = {
    #                         "Content-Type": "application/json", 
    #                         "Accept": "application/json",
    #                         "Catch-Control": "no-cache",
    #                         'Authorization':"Bearer "+api_apps.token,
    #                         'User-Agent': 'ODOO_DEV'
    #                     }
    #                     phone_numbers = rec.phone
    #                     if phone_numbers:
    #                         if phone_numbers[0] == '0':
    #                             phone_numbers = phone_numbers.replace('0', '62')
    #                         if phone_numbers[0:3] == '+62':
    #                             phone_numbers = phone_numbers.replace('+', '')
    #                             phone_numbers = phone_numbers.replace('-', '')
    #                             phone_numbers = phone_numbers.replace(' ', '')
    #                     json_data = {
    #                         "code": rec.ref,
    #                         "fullName": rec.name,
    #                         "phoneNumber": phone_numbers
    #                     }
    #                     response = requests.put(base_url+'/'+str(rec.id), data=json.dumps(json_data), headers=headers)
    #                     res = response.json()
    #                     if 'error' in res:
    #                         if type(res['error']) != str:
    #                             if 'phoneNumber' in res['error']:
    #                                 raise UserError(('[Integration APPS] message : '+res['error']['phoneNumber']))
    #                             elif 'code' in res['error']:
    #                                 raise UserError(('[Integration APPS] message : '+res['error']['code']))
    #                             elif 'odooId' in res['error']:
    #                                 raise UserError(('[Integration APPS] message : '+res['error']['odooId']))
    #                             else:
    #                                 raise UserError((json.dumps(res)))
    #                         else:    
    #                             raise UserError(('[Integration APPS] message : '+res['error']))
    #                     else:
    #                         logs = {
    #                             'name': 'API Update Peternak',
    #                             'base_url': base_url,
    #                             'method': 'PUT',
    #                             'data': json_data,
    #                             'response': res,
    #                             'is_posted': True
    #                         }
    #                         self.env['external.api.log'].create(logs)
    #     return result
    
    # def unlink(self):
    #     is_api = self.env.context.get('api_action')
    #     if not is_api:
    #         for rec in self:
    #             if rec.is_peternak:
    #                 base_url = 'https://app-be-dev.broilerx.com/v1/farmers/odoo'
    #                 api_apps = self.env['external.api.key'].search([('code', '=', 'api_apps_user')])
    #                 if not api_apps:
    #                     raise UserError(("Contact admin for settings external api key api_apps_user"))
    #                 api_apps.generate_token()
    #                 headers = {
    #                     "Content-Type": "application/json", 
    #                     "Accept": "application/json", 
    #                     "Catch-Control": "no-cache",
    #                     'Authorization':"Bearer "+api_apps.token,
    #                     'User-Agent': 'ODOO_DEV'
    #                 }
    #                 json_data = {}
    #                 response = requests.delete(base_url+'/'+str(rec.id), data=json.dumps(json_data), headers=headers)
    #                 res = response.json()
    #                 if 'error' in res:
    #                     if type(res['error']) != str:
    #                         raise UserError(('[Integration APPS] message : '+ 'Mohon pastikan bahwa Anda telah memasukkan informasi akun dengan benar'))
    #                     else:    
    #                         raise UserError(('[Integration APPS] message : '+res['error']))
    #                 else:
    #                     logs = {
    #                         'name': 'API Delete Peternak',
    #                         'base_url': base_url,
    #                         'method': 'DEL',
    #                         'data': json_data,
    #                         'response': res,
    #                         'is_posted': True
    #                     }
    #                     self.env['external.api.log'].create(logs)
    #     res = super(InheritResPartnerRHPP, self).unlink()
    #     return res
