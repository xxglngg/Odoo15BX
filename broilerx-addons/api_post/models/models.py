# # -*- coding: utf-8 -*-
#
from odoo import models, fields, api
import json
import requests
from uuid import uuid4
# import json
# import requests
from odoo.exceptions import UserError
from urllib.parse import urlparse



# class APICustomer(models.Model):
# 	_inherit = 'module.name'
# 	_description = 'Module Description’'
# 	name =  fields.Char(string=)
# 	age =  fields.Char(string=”Age”)
#
# @api.model
# 	def create(self, vals):
# data = {
# “Name” : vals.get(‘name’),
# “Age” : vals.get(‘age’’),
# }
# url = ""http://example.com"
# response = requests.post(url, data=json.dumps(data))
# return super(ModuleName, self).create(vals)
#
API_SELECTION = [
    ('peternak', 'Data Peternak'),
    ('customer', 'Data Bakul Livebird'),
    ('pakan pre-starter', 'Data Master Pakan Pre Starter'),
    ('pakan starter', 'Data Master Pakan Starter'),
    ('pakan finisher', 'Data Master Pakan Finisher'),
    ('doc', 'Data Pakan DOC'),
    ('ovk', 'Data Pakan OVK'),
    ('analytic_account', 'Data Account Analytic'),
]

METHOD_SELECTION = [
    ('post', 'POST'),
    ('get', 'GET'),
    ('put', 'PUT'),
    ('delete', 'DELETE'),
]

STATUS_RESPONSE_SELECTION = [
    ('sukses', 'Sukses'),
    ('gagal', 'Gagal'),
]


class api_post(models.Model):
    _name = 'api.config'
    _description = 'Setup and Config for API POST'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    value = fields.Char()
    url = fields.Char()
    token = fields.Char()
    api_selection = fields.Selection(API_SELECTION, String='API untuk :', required=True, track_visibility='always')
    description = fields.Char()


    def button_check_api_request_http(self):
        rand_token = uuid4()
        # data = 0

        # self.env['']
        if self.api_selection == 'peternak':
            check_variable = self.env['parameters.api.post'].search([('api_selection','=','peternak')])
            if len(check_variable.ids) == 0:
                raise UserError("Mohon diisi variable parameters pada menu settings")
            check_name = [i.strip() for i in check_variable.name.split('+')]
            peternak = self.env['res.partner.category'].search([('name','in',check_name)])
            if len(peternak.ids) == 0:
                raise UserError("Please check category partner with tag name == 'peternak' - periksa text tulisan")

            data = {}
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # parsed_url = urllib.parse.urlparse(url)
            url = base_url+"/api_post_bx_15/http/peternak"
            response = requests.post(url, data=data)
            self.write({
                'value':response.text,
                'url':url,
                'token':rand_token,
            })

        if self.api_selection == 'customer':
            check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'customer')])
            if len(check_variable.ids) ==0 :
                raise UserError("Mohon diisi variable parameters pada menu settings")
            check_name = [i.strip() for i in check_variable.name.split('+')]
            customer = self.env['res.partner.category'].search([('name','in',check_name)])
            if len(customer.ids) == 0:
                raise UserError("Please check category partner with tag name == 'bakul livebird' - periksa text tulisan")

            data = {}
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # parsed_url = urllib.parse.urlparse(url)
            url =base_url+"/api_post_bx_15/http/customer"
            response = requests.post(url, data=data)
            self.write({
                'value':response.text,
                'url':url,
                'token':rand_token,
            })

        if self.api_selection == 'pakan pre-starter':
            check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'pakan pre-starter')])
            if len(check_variable.ids) == 0:
                raise UserError("Mohon diisi variable parameters pada menu settings")
            check_name = [i.strip() for i in check_variable.name.split('+')]
            starter = self.env['product.category'].search([('name','in',check_name)])
            if len(starter.ids) == 0:
                raise UserError("Check category dengan nama == 'Pre Starter' - periksa text tulisan")

            data = {}
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # parsed_url = urllib.parse.urlparse(url)
            url = base_url+"/api_post_bx_15/http/pakan_pre_starter"
            response = requests.post(url, data=data)
            self.write({
                'value':response.text,
                'url':url,
                'token':rand_token,
            })

        if self.api_selection == 'pakan starter':
            check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'pakan starter')])
            if len(check_variable.ids) == 0:
                raise UserError("Mohon diisi variable parameters pada menu settings")
            check_name = [i.strip() for i in check_variable.name.split('+')]
            starter = self.env['product.category'].search([('name','in',check_name)])
            if len(starter.ids) == 0:
                raise UserError("Check category dengan nama == 'Starter' - periksa text tulisan")

            data = {}
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # parsed_url = urllib.parse.urlparse(url)
            url = base_url+"/api_post_bx_15/http/pakan_starter"
            response = requests.post(url, data=data)
            self.write({
                'value':response.text,
                'url':url,
                'token':rand_token,
            })

        if self.api_selection == 'pakan finisher':
            check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'pakan finisher')])
            if len(check_variable.ids) == 0:
                raise UserError("Mohon diisi variable parameters pada menu settings")
            check_name = [i.strip() for i in check_variable.name.split('+')]
            starter = self.env['product.category'].search([('name','in',check_name)])
            if len(starter.ids) == 0:
                raise UserError("Check category dengan nama == 'Finisher' - periksa text tulisan")

            data = {}
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # parsed_url = urllib.parse.urlparse(url)
            url = base_url+"/api_post_bx_15/http/pakan_finisher"
            response = requests.post(url, data=data)
            self.write({
                'value':response.text,
                'url':url,
                'token':rand_token,
            })

        if self.api_selection == 'doc':
            check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'doc')])
            if len(check_variable.ids) == 0:
                raise UserError("Mohon diisi variable parameters pada menu settings")
            check_name = [i.strip() for i in check_variable.name.split('+')]
            starter = self.env['product.category'].search([('name','in',check_name)])
            if len(starter.ids) == 0:
                raise UserError("Check category dengan nama == 'DOC' - periksa text tulisan")

            data = {}
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # parsed_url = urllib.parse.urlparse(url)
            url = base_url+"/api_post_bx_15/http/doc"
            response = requests.post(url, data=data)
            self.write({
                'value':response.text,
                'url':url,
                'token':rand_token,
            })

        if self.api_selection == 'ovk':
            check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'ovk')])
            if len(check_variable.ids) == 0:
                raise UserError("Mohon diisi variable parameters pada menu settings")
            check_name = [i.strip() for i in check_variable.name.split('+')]
            starter = self.env['product.category'].search([('name','in',check_name)])
            if len(starter.ids) == 0:
                raise UserError("Check category dengan nama == 'Obat, Vaksin & Kimia' - periksa text tulisan")

            data = {}
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # parsed_url = urllib.parse.urlparse(url)
            url = base_url+"/api_post_bx_15/http/ovk"
            response = requests.post(url, data=data)
            self.write({
                'value':response.text,
                'url':url,
                'token':rand_token,
            })

        if self.api_selection == 'analytic_account':

            account_analytic = self.env['account.analytic.account'].search([])
            if account_analytic is False:
                raise UserError("Please check data Analytic Account in Report or Contact Administrator")

            data = {}
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # parsed_url = urllib.parse.urlparse(url)
            url = base_url+"/api_post_bx_15/http/analytic_account"
            response = requests.post(url, data=data)
            self.write({
                'value':response.text,
                'url':url,
                'token':rand_token,
            })


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('api.post') or ('New')
        return super(api_post, self).create(values)

    @api.model
    def check_id_data(self, args):

        print(self)
        print(args)
        checkarray_amp = []
        checkarray_crash = []

        data = []
        list = {}

        check_amp_model_id_array = []
        check_crash_model_id_array = []
        if len(args['array_amp']) > 0:
            for res_arr1 in args['array_amp']:
                if (res_arr1.find("model=") != -1):
                    check = res_arr1.split("model=")
                    checkarray_amp.append(check)
                if (res_arr1.find("#id=") != -1):
                    check_id = res_arr1.split("=")
                    checkarray_amp.append(check_id)

                if (res_arr1.find("id=") != -1):
                    check_id = res_arr1.split("=")
                    checkarray_amp.append(check_id)

            print(checkarray_amp)
            if len(checkarray_amp) > 0:
                i = 0

                for amp in checkarray_amp:

                    # for data_amp in amp:
                    if amp[1] == "api.config" :
                        list['model'] = amp[1]
                        check_amp_model_id_array.append(amp[1])

                    if amp[0] == 'id':
                        i = i +1
                        list['id'] = amp[1]
                        check_amp_model_id_array.append(amp[1])


                    i = i + 1

                check_amp_model_id_array = set(check_amp_model_id_array)
                if len(check_amp_model_id_array) == 2:
                    check_api = self.env['api.config'].search([('id', '=', list['id'])])
                    if check_api.api_selection == 'peternak':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'peternak')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['res.partner.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            peternak = self.env['res.partner'].sudo().search([('category_id', 'in', check_category.ids)])
                            if peternak:
                                list['result'] = "true"
                                list['api'] = 'peternak'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'customer':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'customer')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['res.partner.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            bakul = self.env['res.partner'].sudo().search([('category_id', 'in', check_category.ids)])
                            if bakul:
                                list['result'] = "true"
                                list['api'] = 'customer'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'pakan pre-starter':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'pakan pre-starter')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            pre_starter = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if pre_starter:
                                list['result'] = "true"
                                list['api'] = 'pakan pre-starter'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'pakan starter':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'pakan starter')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            starter = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if starter:
                                list['result'] = "true"
                                list['api'] = 'pakan starter'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'pakan finisher':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'pakan finisher')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            finisher = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if finisher:
                                list['result'] = "true"
                                list['api'] = 'pakan finisher'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'doc':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'doc')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            doc = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if doc:
                                list['result'] = "true"
                                list['api'] = 'doc'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'ovk':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'ovk')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name','in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            ovk = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if ovk:
                                list['result'] = "true"
                                list['api'] = 'ovk'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'analytic_account':
                        account_analytic = self.env['account.analytic.account'].search([])
                        if len(account_analytic.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)

                            list['result'] = "true"
                            list['api'] = 'analytic_account'
                            list['variable_filter'] = ''
                            data.append(list)
                            return data

        else:
            list['result'] = "false"
            data.append(list)
            return data

        if len(args['array_crash']) > 0:
            for res_arr2 in args['array_crash']:
                crash_amp = res_arr2.split("&")
                for data_crash_amp in crash_amp:
                    if (data_crash_amp.find("model=") != -1):
                        check = data_crash_amp.split("model=")
                        checkarray_crash.append(check)

                    if (data_crash_amp.find("id=") != -1):
                        check_id = data_crash_amp.split("=")
                        checkarray_crash.append(check_id)

            if len(checkarray_crash) > 0:
                i = 0
                for crash in checkarray_crash:

                    # for data_crash in crash:
                    if crash[1] == "api.config":
                        list['model'] = crash[1]
                        check_crash_model_id_array.append(crash[1])
                    if crash[0] == 'id':
                        i = i + 1
                        list['id'] = crash[1]
                        check_crash_model_id_array.append(crash[1])


                    i = i + 1
                check_crash_model_id_array = set(check_crash_model_id_array)
                if len(check_crash_model_id_array) == 2:
                    check_api = self.env['api.config'].search([('id', '=', list['id'])])
                    if check_api.api_selection == 'peternak':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'peternak')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['res.partner.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            peternak = self.env['res.partner'].sudo().search([('category_id', 'in', check_category.ids)])
                            if peternak:
                                list['result'] = "true"
                                list['api'] = 'peternak'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'customer':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'customer')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['res.partner.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            bakul = self.env['res.partner'].sudo().search([('category_id', 'in', check_category.ids)])
                            if bakul:
                                list['result'] = "true"
                                list['api'] = 'customer'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'pakan pre-starter':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'pakan pre-starter')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            pre_starter = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if pre_starter:
                                list['result'] = "true"
                                list['api'] = 'pakan pre-starter'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'pakan starter':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'pakan starter')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            starter = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if starter:
                                list['result'] = "true"
                                list['api'] = 'pakan starter'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data
                    if check_api.api_selection == 'pakan finisher':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'pakan finisher')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            finisher = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if finisher:
                                list['result'] = "true"
                                list['api'] = 'pakan finisher'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'doc':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'doc')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            doc = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if doc:
                                list['result'] = "true"
                                list['api'] = 'doc'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'ovk':
                        check_variable = self.env['parameters.api.post'].search([('api_selection', '=', 'ovk')])
                        if len(check_variable.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        check_name = [i.strip() for i in check_variable.name.split('+')]
                        check_category = self.env['product.category'].search([('name', 'in',check_name)])
                        if len(check_category.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)
                            ovk = self.env['product.template'].sudo().search([('categ_id', 'in', check_category.ids)])
                            if ovk:
                                list['result'] = "true"
                                list['api'] = 'ovk'
                                list['variable_filter'] = check_name
                                data.append(list)
                                return data

                    if check_api.api_selection == 'analytic_account':
                        account_analytic = self.env['account.analytic.account'].search([])
                        if len(account_analytic.ids) == 0:
                            list['result'] = "false"
                            data.append(list)
                            return data
                        else:
                            print(self)

                            list['result'] = "true"
                            list['api'] = 'analytic_account'
                            list['variable_filter'] = ''
                            data.append(list)
                            return data
        else:
            list['result'] = "false"
            data.append(list)
            return data

        list['result'] = "false"
        data.append(list)
        return data

class api_get(models.Model):
    _name = 'api.config.get'
    _description = 'Setup and Config for API GET'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    value = fields.Char()
    url = fields.Char()
    token = fields.Char()
    description = fields.Char()
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    phone_number = fields.Char()
    query_param = fields.Char()
    database = fields.Char(required=True)

    # @api.model
    def get_api_performa_produksi(self):
        print(self)
        # get_data_controller = controllers.controller.ApiGet.get_apps_from_api(self)
        auth_login = 'https://app-be-dev.broilerx.com/v1/auth/login'
        base_url = 'https://app-be-dev.broilerx.com/v1/'
        # params = 'rearingPeriods?itemPerPage=&currentPage=0&descending=false'
        params = self.query_param
        # common = xmlrpc.client.ServerProxy(auth_login).start()
        # common.version()
        # uid = common.authenticate(self.database, self.username, self.password, {})
        # r = requests.get(base_url + params)
        # print("Status Code: {} [OK]".format(r.status_code))
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache"}

        json_data = {'username': self.username, 'password':self.password}

        response = requests.post(auth_login, data=json.dumps(json_data), headers=headers)
        print(response)
        token = response.json()

        print(token)
        headers2 = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache",'Authorization':"Bearer "+token['accessToken'],'User-Agent': 'ODOO_Dev'}

        json_data2 = {}

        response2 = requests.get(self.url, data=json.dumps(json_data2), headers=headers2)
        print(response2)
        data_apps = response2.json()

        self.write({
            'token':"Bearer "+token['accessToken'],
            'value':data_apps['contents']
        })

        print(data_apps)

class parameters_api_post(models.Model):
    _name = 'parameters.api.post'
    _description = 'Variable Parameters API POST'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    api_selection = fields.Selection(API_SELECTION, String='API untuk :', required=True, track_visibility='always')


class api_hit(models.Model):
    _name = 'api.config.hit'
    _description = 'Setup and Config for API HIT (POST, GET, PUT, DELETE)'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    value = fields.Char()
    url = fields.Char(required=True)
    method = fields.Selection(METHOD_SELECTION, String='Method:', required=True, track_visibility='always')
    api_selection = fields.Selection(API_SELECTION, String='API untuk :', required=True, track_visibility='always')
    token = fields.Char()
    status = fields.Selection(STATUS_RESPONSE_SELECTION, String='status :', track_visibility='always')
    description = fields.Text()
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    phone_number = fields.Char()
    query_param = fields.Char()
    database = fields.Char(required=True)
    variable_json_data = fields.Text(required=True)

    def check_response_connection(self):
        print(self)
        print(self)
        # get_data_controller = controllers.controller.ApiGet.get_apps_from_api(self)
        auth_login = 'https://app-be-dev.broilerx.com/v1/auth/login'
        base_url = 'https://app-be-dev.broilerx.com/v1/'
        # params = 'rearingPeriods?itemPerPage=&currentPage=0&descending=false'
        params = self.query_param
        # common = xmlrpc.client.ServerProxy(auth_login).start()
        # common.version()
        # uid = common.authenticate(self.database, self.username, self.password, {})
        # r = requests.get(base_url + params)
        # print("Status Code: {} [OK]".format(r.status_code))
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache"}

        json_data = {'username': self.username, 'password': self.password}

        response = requests.post(auth_login, data=json.dumps(json_data), headers=headers)
        print(response)
        token = response.json()
        if 'accessToken' not in token:
            self.write({
                'token': '-',
                'value': token['error'],
                'status': 'gagal',
            })
            raise UserError(("API response connection Gagal, check Username dan Password"))

        print(token)
        headers2 = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache",
                    'Authorization': "Bearer " + token['accessToken'], 'User-Agent': 'ODOO_Dev'}

        json_data2 ={}

        for dt in (self.variable_json_data.split("+")):
            value = dt.split(":")
            json_data2[value[0]] = value[1]

        try:
            if self.method == 'get':
                response2 = requests.get(self.url, data=json.dumps(json_data2), headers=headers2)
                print(response2)
                data_apps = response2.json()
                if 'contents' in data_apps:
                    self.write({
                        'token': "Bearer " + token['accessToken'],
                        'value': data_apps['contents'],
                        'status':'sukses',
                    })
                else:
                    self.write({
                        'token': "Bearer " + token['accessToken'],
                        'value': data_apps['error'],
                        'status': 'gagal',
                    })

                print(data_apps)
            if self.method == 'post':
                response2 = requests.post(self.url, data=json.dumps(json_data2), headers=headers2)
                print(response2)
                data_apps = response2.json()

                if 'contents' in data_apps:
                    self.write({
                        'token': "Bearer " + token['accessToken'],
                        'value': data_apps['contents'],
                        'status': 'sukses',
                    })
                else:
                    self.write({
                        'token': "Bearer " + token['accessToken'],
                        'value': data_apps['error'],
                        'status': 'gagal',
                    })

                print(data_apps)
            if self.method == 'put':
                response2 = requests.put(self.url, data=json.dumps(json_data2), headers=headers2)
                print(response2)
                data_apps = response2.json()

                if 'contents' in data_apps:
                    self.write({
                        'token': "Bearer " + token['accessToken'],
                        'value': data_apps['contents'],
                        'status': 'sukses',
                    })
                else:
                    self.write({
                        'token': "Bearer " + token['accessToken'],
                        'value': data_apps['error'],
                        'status': 'gagal',
                    })

                print(data_apps)
            if self.method == 'delete':
                response2 = requests.delete(self.url, data=json.dumps(json_data2), headers=headers2)
                print(response2)
                data_apps = response2.json()

                if 'contents' in data_apps:
                    self.write({
                        'token': "Bearer " + token['accessToken'],
                        'value': data_apps['contents'],
                        'status': 'sukses',
                    })
                else:
                    self.write({
                        'token': "Bearer " + token['accessToken'],
                        'value': data_apps['error'],
                        'status': 'gagal',
                    })

                print(data_apps)

        except Exception as e:
            self.write({
                'token': "Bearer " + token['accessToken'],
                'value': '-',
                'status': 'gagal',
            })
            raise UserError(("API response connection Gagal, check description untuk parsing json"))