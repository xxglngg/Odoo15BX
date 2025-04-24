# -*- coding: utf-8 -*-
import werkzeug.wrappers

from odoo import http
from odoo.http import request
from werkzeug.wrappers import Request, Response
import json
from uuid import uuid4
import urllib.parse
import sys

class ApiPost(http.Controller):

    @http.route('/api_post_bx_15/json/peternak', method=["POST"], type='json', auth='user',csrf=True)
    def post_data_json_peternak(self,**kwargs):
        data_arr = []
        list = {}
        rand_token = uuid4()
        peternak = http.request.env['res.partner.category'].sudo().search([('name', 'in', kwargs['variable_filter'])])

        if len(peternak.ids) == 0 :
            list['ERROR'] = 'Data Peternak tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(list)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return data

        else:
            data_peternak = http.request.env['res.partner'].sudo().search([('category_id', 'in', peternak.ids)])
            for data in data_peternak:
                list = {}
                list['id'] = data.id
                list['create_date'] = str(data.create_date)
                list['write_date'] = str(data.write_date)
                list['nama'] = data.name
                list['email'] = data.email
                list['no_hp'] = data.phone
                list['id_peternak'] = data.ref
                list['address'] = str(data.street) + '-' + str(data.city) + '-' + str(data.state_id.name) + '-' + str(
                    data.country_id.name)

                data_arr.append(list)
            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            data_api_config = http.request.env['api.config'].sudo().search([('id','=',kwargs['id'])])

            base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            url = base_url+"/api_post_bx_15/json/peternak"
            data_api_config.write({

                'value':data_value,
                'url':url,
                'token':rand_token,

            })
            return data_value

    @http.route('/api_post_bx_15/json/customer', method=["POST"], type='json', auth='user', csrf=True)
    def post_data_json_customer(self, **kwargs):
        data_arr = []
        list = {}
        rand_token = uuid4()
        customer = http.request.env['res.partner.category'].sudo().search([('name','in', kwargs['variable_filter'])])

        if len(customer.ids) == 0 :
            list['ERROR'] = 'Data Bakul tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(list)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return data

        else:
            data_bakul = http.request.env['res.partner'].sudo().search([('category_id', 'in', customer.ids)])
            for data in data_bakul:
                list = {}
                list['id'] = data.id
                list['create_date'] = str(data.create_date)
                list['write_date'] = str(data.write_date)
                list['nama'] = data.name
                list['email'] = data.email
                list['no_hp'] = data.phone
                list['address'] = str(data.street) + '-' + str(data.city) + '-' + str(data.state_id.name) + '-' + str(
                    data.country_id.name)
                list['vat'] = data.vat


                data_arr.append(list)
            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            data_api_config = http.request.env['api.config'].sudo().search([('id', '=', kwargs['id'])])

            url = sys.argv[1]
            base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            url = base_url+"/api_post_bx_15/json/customer"
            data_api_config.write({

                'value': data_value,
                'url': url,
                'token': rand_token,

            })
            return data_value

    @http.route('/api_post_bx_15/json/pakan_pre_starter', method=["POST"], type='json', auth='user', csrf=True)
    def post_data_json_pakan_pre_starter(self, **kwargs):
        data_arr = []
        list = {}
        rand_token = uuid4()
        prestarter = http.request.env['product.category'].sudo().search([('name', 'in', kwargs['variable_filter'])])

        if len(prestarter.ids) == 0 :
            list['ERROR'] = 'Data Product Pre-Starter tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(list)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return data

        else:
            data_prestarter = http.request.env['product.template'].sudo().search([('categ_id', 'in', prestarter.ids)])
            if len(data_prestarter.seller_ids) > 0:
                for data in data_prestarter.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search([('id', '=', data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name) + '-' + str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list = {}
                list['id'] = data_prestarter.id
                list['create_date'] = str(data_prestarter.create_date)
                list['write_date'] = str(data_prestarter.write_date)
                list['nama'] = data_prestarter.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = data_prestarter.name +'-'
                list['product_uom'] = data_prestarter.uom_id.name
                data_arr.append(list)
            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            data_api_config = http.request.env['api.config'].sudo().search([('id', '=', kwargs['id'])])

            url = sys.argv[1]
            base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            url = base_url + "/api_post_bx_15/json/pakan_pre_starter"
            data_api_config.write({

                'value': data_value,
                'url': url,
                'token': rand_token,

            })
            return data_value

    @http.route('/api_post_bx_15/json/pakan_starter', method=["POST"], type='json', auth='user', csrf=True)
    def post_data_json_pakan_starter(self, **kwargs):
        data_arr = []
        list = {}
        rand_token = uuid4()
        prestarter = http.request.env['product.category'].sudo().search([('name','in', kwargs['variable_filter'])])

        if len(prestarter.ids) == 0 :
            list['ERROR'] = 'Data Product Starter tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(list)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return data

        else:
            data_starter = http.request.env['product.template'].sudo().search([('categ_id', 'in', prestarter.ids)])
            if len(data_starter.seller_ids) > 0:
                for data in data_starter.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search([('id', '=', data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name) + '-' + str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list = {}
                list['id'] = data_starter.id
                list['create_date'] = str(data_starter.create_date)
                list['write_date'] = str(data_starter.write_date)
                list['nama'] = data_starter.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = data_starter.name + '-'
                list['product_uom'] = data_starter.uom_id.name
                data_arr.append(list)
            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            data_api_config = http.request.env['api.config'].sudo().search([('id', '=', kwargs['id'])])

            url = sys.argv[1]
            base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            url = base_url + "/api_post_bx_15/json/pakan_starter"
            data_api_config.write({

                'value': data_value,
                'url': url,
                'token': rand_token,

            })
            return data_value

    @http.route('/api_post_bx_15/json/pakan_finisher', method=["POST"], type='json', auth='user', csrf=True)
    def post_data_json_pakan_finisher(self, **kwargs):
        data_arr = []
        list = {}
        rand_token = uuid4()
        finisher = http.request.env['product.category'].sudo().search([('name','in',kwargs['variable_filter'])])

        if len(finisher.ids) == 0 :
            list['ERROR'] = 'Data Product Finisher tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(list)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return data

        else:
            data_finisher= http.request.env['product.template'].sudo().search([('categ_id', 'in', finisher.ids)])
            if len(data_finisher.seller_ids) > 0:
                for data in data_finisher.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search([('id', '=', data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name) + '-' + str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list['id'] = data_finisher.id
                list['create_date'] = str(data_finisher.create_date)
                list['write_date'] = str(data_finisher.write_date)
                list = {}
                list['nama'] = data_finisher.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = data_finisher.name + '-'
                list['product_uom'] = data_finisher.uom_id.name
                data_arr.append(list)
            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            data_api_config = http.request.env['api.config'].sudo().search([('id', '=', kwargs['id'])])

            url = sys.argv[1]
            base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            url = base_url + "/api_post_bx_15/json/pakan_finisher"
            data_api_config.write({

                'value': data_value,
                'url': url,
                'token': rand_token,

            })
            return data_value

    @http.route('/api_post_bx_15/json/doc', method=["POST"], type='json', auth='user', csrf=True)
    def post_data_json_doc(self, **kwargs):
        data_arr = []
        list = {}
        rand_token = uuid4()
        doc = http.request.env['product.category'].sudo().search([('name','in', kwargs['variable_filter'])])

        if len(doc.ids) == 0 :
            list['ERROR'] = 'Data Product DOC tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(list)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return data

        else:
            data_doc = http.request.env['product.template'].sudo().search([('categ_id', 'in', doc.ids)])
            if len(data_doc.seller_ids) > 0:
                for data in data_doc.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search(
                        [('id', '=', data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name) + '-' + str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list = {}
                list['id'] = data_doc.id
                list['create_date'] = str(data_doc.create_date)
                list['write_date'] = str(data_doc.write_date)
                list['nama'] = data_doc.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = data_doc.name + '-'
                list['product_uom'] = data_doc.uom_id.name
                data_arr.append(list)
            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            data_api_config = http.request.env['api.config'].sudo().search([('id', '=', kwargs['id'])])

            url = sys.argv[1]
            base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            url = base_url + "/api_post_bx_15/json/doc"
            data_api_config.write({

                'value': data_value,
                'url': url,
                'token': rand_token,

            })
            return data_value

    @http.route('/api_post_bx_15/json/analytic_account', method=["POST"], type='json', auth='user', csrf=True)
    def post_data_json_analytic_account(self, **kwargs):
        data_arr = []
        list = {}
        rand_token = uuid4()
        account = http.request.env['account.analytic.account'].sudo().search([])

        if len(account.ids) == 0 :
            list['ERROR'] = 'Data Account Analytic tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(list)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return data

        else:


            for data in account:

                list = {}
                list['id'] = data.id
                list['create_date'] = str(data.create_date)
                list['write_date'] = str(data.write_date)
                list['nama'] = data.name
                list['customer'] = data.partner_id.name
                list['reference'] = str(data.code)
                list['group'] = str(data.group_id.name)
                list['company'] = str(data.company_id.name)
                list['state'] = str(data.state)
                data_arr.append(list)

            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            data_api_config = http.request.env['api.config'].sudo().search([('id', '=', kwargs['id'])])

            url = sys.argv[1]
            base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            url = base_url + "/api_post_bx_15/json/analytic_account"
            data_api_config.write({

                'value': data_value,
                'url': url,
                'token': rand_token,

            })
            return data_value

    @http.route('/api_post_bx_15/json/ovk', method=["POST"], type='json', auth='user', csrf=True)
    def post_data_json_ovk(self, **kwargs):
        data_arr = []
        list = {}
        rand_token = uuid4()
        ovk = http.request.env['product.category'].sudo().search([('name', 'in', kwargs['variable_filter'])])

        if len(ovk.ids) == 0 :
            list['ERROR'] = 'Data Product Obat, Vaksin & Kimia tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(list)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return data

        else:
            data_ovk = http.request.env['product.template'].sudo().search([('categ_id', 'in', ovk.ids)])
            if len(data_ovk.seller_ids) > 0:
                for data in data_ovk.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search(
                        [('id', '=', data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name) + '-' + str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list = {}
                list['id'] = data_ovk.id
                list['create_date'] = str(data_ovk.create_date)
                list['write_date'] = str(data_ovk.write_date)
                list['nama'] = data_ovk.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = data_ovk.name + '-'
                list['product_uom'] = data_ovk.uom_id.name
                data_arr.append(list)
            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            data_api_config = http.request.env['api.config'].sudo().search([('id', '=', kwargs['id'])])

            url = sys.argv[1]
            base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            url = base_url + "/api_post_bx_15/json/ovk"
            data_api_config.write({

                'value': data_value,
                'url': url,
                'token': rand_token,

            })
            return data_value

            #JSON
            # =======================================================================
            #
            # == == == == == == == == == == == == == == == == == == == == == == == ==
            # ========= HTTP ==================

    @http.route('/api_post_bx_15/http/peternak', method=["POST"], type='http', auth='user',csrf=True)
    def post_data_http_peternak(self, **kwargs):
        data_arr = []
        list = {}
        variable = http.request.env['parameters.api.post'].sudo().search([('api_selection','=','peternak')])
        if len(variable.ids) == 0:
            list['ERROR'] = 'Parameters Category Peternak tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )
        check_name = [i.strip() for i in variable.name.split('+')]
        peternak = http.request.env['res.partner.category'].sudo().search([('name', 'in', check_name)])

        if len(peternak.ids) == 0 :
            list['ERROR'] = 'Data peternak tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        else:
            data_peternak =  http.request.env['res.partner'].sudo().search([('category_id', 'in', peternak.ids)])
            for data in data_peternak:
                list = {}
                list['id'] = data.id
                list['create_date'] = str(data.create_date)
                list['write_date'] = str(data.write_date)
                list['nama'] = data.name
                list['email'] =data.email
                list['no_hp'] = data.phone
                list['id_peternak'] = data.ref
                list['address'] = str(data.street) +'-'+str(data.city)+'-'+str(data.state_id.name) +'-'+str(data.country_id.name)
                data_arr.append(list)
            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data_value,
            )

    @http.route('/api_post_bx_15/http/customer', method=["POST"], type='http', auth='user', csrf=True)
    def post_data_http_customer(self, **kwargs):
        data_arr = []
        list = {}
        variable = http.request.env['parameters.api.post'].sudo().search([('api_selection', '=', 'customer')])
        if len(variable.ids) == 0:
            list['ERROR'] = 'Parameters Category Bakul Livebird tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        check_name = [i.strip() for i in variable.name.split('+')]
        customer = http.request.env['res.partner.category'].sudo().search([('name', 'in', check_name)])

        if len(customer.ids) == 0 :
            list['ERROR'] = 'Data Bakul tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        else:
            data_bakul = http.request.env['res.partner'].sudo().search([('category_id', 'in', customer.ids)])
            for data in data_bakul:
                list = {}
                list['id'] = data.id
                list['create_date'] = str(data.create_date)
                list['write_date'] = str(data.write_date)
                list['nama'] = data.name
                list['email'] = data.email
                list['no_hp'] = data.phone
                list['address'] = str(data.street) + '-' + str(data.city) + '-' + str(data.state_id.name) + '-' + str(
                    data.country_id.name)
                list['vat'] = data.vat
                data_arr.append(list)
            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data_value,
            )

    @http.route('/api_post_bx_15/http/pakan_pre_starter', method=["POST"], type='http', auth='user', csrf=True)
    def post_data_http_pakan_prestarter(self, **kwargs):
        data_arr = []
        list = {}
        variable = http.request.env['parameters.api.post'].sudo().search([('api_selection', '=', 'pakan pre-starter')])
        if len(variable.ids) == 0:
            list['ERROR'] = 'Parameters Category Pakan Starter tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        check_name = [i.strip() for i in variable.name.split('+')]
        prestarter = http.request.env['product.category'].sudo().search([('name', 'in', check_name)])

        if len(prestarter.ids) == 0 :
            list['ERROR'] = 'Data Category Product Pre Starter tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        else:
            data_prestarter = http.request.env['product.template'].sudo().search([('categ_id', 'in', prestarter.ids)])
            if len(data_prestarter.seller_ids) > 0:
                for data in data_prestarter.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search([('id','=',data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name)+'-'+str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list = {}
                list['id'] = data_prestarter.id
                list['create_date'] = str(data_prestarter.create_date)
                list['write_date'] = str(data_prestarter.write_date)
                list['nama'] = data_prestarter.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = str(data_prestarter.name) + '-'
                list['product_uom'] = data_prestarter.uom_id.name

                data_arr.append(list)

            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data_value,
            )

    @http.route('/api_post_bx_15/http/pakan_starter', method=["POST"], type='http', auth='user', csrf=True)
    def post_data_http_pakan_starter(self, **kwargs):
        data_arr = []
        list = {}
        variable = http.request.env['parameters.api.post'].sudo().search([('api_selection', '=', 'pakan starter')])
        if len(variable.ids) == 0:
            list['ERROR'] = 'Parameters Category Pakan Starter tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        check_name = [i.strip() for i in variable.name.split('+')]
        starter = http.request.env['product.category'].sudo().search([('name', 'in', check_name)])

        if len(starter.ids) == 0 :
            list['ERROR'] = 'Data Category Product Starter tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        else:
            data_starter = http.request.env['product.template'].sudo().search([('categ_id', 'in', starter.ids)])
            if len(data_starter.seller_ids) > 0:
                for data in data_starter.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search([('id', '=', data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name) + '-' + str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list = {}
                list['id'] = data_starter.id
                list['create_date'] = str(data_starter.create_date)
                list['write_date'] = str(data_starter.write_date)
                list['nama'] = data_starter.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = str(data_starter.name) + '-'
                list['product_uom'] = data_starter.uom_id.name

                data_arr.append(list)

            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data_value,
            )

    @http.route('/api_post_bx_15/http/pakan_finisher', method=["POST"], type='http', auth='user', csrf=True)
    def post_data_http_pakan_finisher(self, **kwargs):
        data_arr = []
        list = {}
        variable = http.request.env['parameters.api.post'].sudo().search([('api_selection', '=', 'pakan finisher')])
        if len(variable.ids) == 0:
            list['ERROR'] = 'Parameters Category Pakan Finisher tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        check_name = [i.strip() for i in variable.name.split('+')]
        starter = http.request.env['product.category'].sudo().search([('name', 'in', check_name)])

        if len(starter.ids) == 0 :
            list['ERROR'] = 'Data Category Product Finisher tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        else:
            data_starter = http.request.env['product.template'].sudo().search([('categ_id', 'in', starter.ids)])
            if len(data_starter.seller_ids) > 0:
                for data in data_starter.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search([('id', '=', data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name) + '-' + str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list = {}
                list['id'] = data_starter.id
                list['create_date'] = str(data_starter.create_date)
                list['write_date'] = str(data_starter.write_date)
                list['nama'] = data_starter.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = str(data_starter.name) + '-'
                list['product_uom'] = data_starter.uom_id.name

                data_arr.append(list)

            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data_value,
            )

    @http.route('/api_post_bx_15/http/doc', method=["POST"], type='http', auth='user', csrf=True)
    def post_data_http_doc(self, **kwargs):
        data_arr = []
        list = {}
        variable = http.request.env['parameters.api.post'].sudo().search([('api_selection', '=', 'doc')])
        if len(variable.ids) == 0:
            list['ERROR'] = 'Parameters Category DOC tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )
        check_name = [i.strip() for i in variable.name.split('+')]
        doc = http.request.env['product.category'].sudo().search([('name', 'in', check_name)])

        if len(doc.ids) == 0 :
            list['ERROR'] = 'Data Category Product DOC tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        else:
            data_doc = http.request.env['product.template'].sudo().search([('categ_id', 'in', doc.ids)])
            if len(data_doc.seller_ids) > 0:
                for data in data_doc.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search([('id', '=', data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name) + '-' + str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list = {}
                list['id'] = data_doc.id
                list['create_date'] = str(data_doc.create_date)
                list['write_date'] = str(data_doc.write_date)
                list['nama'] = data_doc.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = str(data_doc.name) + '-'
                list['product_uom'] = data_doc.uom_id.name

                data_arr.append(list)

            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data_value,
            )
    @http.route('/api_post_bx_15/http/ovk', method=["POST"], type='http', auth='user', csrf=True)
    def post_data_http_ovk(self, **kwargs):
        data_arr = []
        list = {}
        variable = http.request.env['parameters.api.post'].sudo().search([('api_selection', '=', 'ovk')])
        if len(variable.ids) == 0:
            list['ERROR'] = 'Parameters Category Product Obat, Vaksin & Kimia tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )
        check_name = [i.strip() for i in variable.name.split('+')]
        ovk = http.request.env['product.category'].sudo().search([('name', 'in', check_name)])

        if len(ovk.ids) == 0 :
            list['ERROR'] = 'Data Category Product Obat, Vaksin & Kimia tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        else:
            data_ovk = http.request.env['product.template'].sudo().search([('categ_id', 'in', ovk.ids)])
            if len(data_ovk.seller_ids) > 0:
                for data in data_ovk.seller_ids:
                    product_name = http.request.env['product.template'].sudo().search([('id', '=', data.product_tmpl_id.id)])
                    list = {}
                    list['id'] = data.id
                    list['create_date'] = str(data.create_date)
                    list['write_date'] = str(data.write_date)
                    list['nama'] = product_name.name
                    list['perusahaan'] = data.display_name
                    list['nama_product_dan_perusahaan'] = str(product_name.name) + '-' + str(data.display_name)
                    list['product_uom'] = product_name.uom_id.name
                    data_arr.append(list)
            else:
                list = {}
                list['id'] = data_ovk.id
                list['create_date'] = str(data_ovk.create_date)
                list['write_date'] = str(data_ovk.write_date)
                list['nama'] = data_ovk.name
                list['perusahaan'] = '-'
                list['nama_product_dan_perusahaan'] = str(data_ovk.name) + '-'
                list['product_uom'] = data_ovk.uom_id.name

                data_arr.append(list)

            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data_value,
            )

    @http.route('/api_post_bx_15/http/analytic_account', method=["POST"], type='http', auth='user', csrf=True)
    def post_data_http_analytic_account(self, **kwargs):
        data_arr = []
        list = {}

        account = http.request.env['account.analytic.account'].sudo().search([])

        if len(account.ids) == 0 :
            list['ERROR'] = 'Data Account Analytic tidak ditemukan'

            data_arr.append(list)
            data = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data,
            )

        else:

            for data in account:

                list = {}
                list['id'] = data.id
                list['create_date'] = str(data.create_date)
                list['write_date'] = str(data.write_date)
                list['nama'] = data.name
                list['customer'] = data.partner_id.name
                list['reference'] = str(data.code)
                list['group'] = str(data.group_id.name)
                list['company'] = str(data.company_id.name)
                list['state'] = str(data.state)
                data_arr.append(list)


            data_value = json.dumps(data_arr)
            headers = [('Content-Type', 'application/json'),
                       ('Cache-Control', 'no-store')]
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json',
                headers=headers,
                response=data_value,
            )
#