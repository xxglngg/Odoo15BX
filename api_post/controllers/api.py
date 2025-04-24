import werkzeug.wrappers
import json
from xmlrpc import client
from odoo import http, models, fields, _, exceptions, tools
from odoo.http import request
from werkzeug.wrappers import PlainRequest
import logging
from odoo.exceptions import AccessDenied
import jwt
from odoo.tools.config import config
import functools
from datetime import datetime

secret_key = config.options.get('jwt_secret_key', 'br01lerx')
_logger = logging.getLogger(__name__)

# def validate_token(func):
#     """."""

#     @functools.wraps(func)
#     def wrap(self, *args, **kwargs):
#         headers = request.httprequest.headers
#         api_key = headers.get("odoo_api_key")
#         if api_key:
#             request.uid = 1
#             auth_api_key = request.env["res.api.key"]._retrieve_api_key(
#                 api_key
#             )
#             if auth_api_key:
#                 try:
#                     check = jwt.decode(auth_api_key.key, secret_key, algorithms=['HS256'])   
#                 except jwt.exceptions.ExpiredSignatureError:
#                     return {'code': 401, 'message': "Token is expired", 'data': []}
#                 except jwt.exceptions.DecodeError:
#                     return {'code': 401, 'message': "Token signature is invalid", 'data': []}
#                 request._env = None
#                 request.uid = auth_api_key.user_id.id
#                 request.auth_api_key = api_key
#                 request.auth_api_key_id = auth_api_key.id
#                 return func(self, *args, **kwargs)
#             return {'code': 401, 'message': "access denied", 'data': []}
#         return {'code': 401, 'message': "access denied", 'data': []}
#     return wrap

def validate_webhook_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        vals = request.jsonrequest.get('event_id','')
        headers = request.httprequest.headers
        api_key = headers.get("odoo_api_key")
        if api_key:
            request.uid = 1
            auth_api_key = request.env["webhook.api.token"].search(
                [('token','=', api_key)]
            )
            if auth_api_key:
                return func(self, *args, **kwargs)
            return {'code': 401, 'status': 'unauthorize', 'message': "access denied", 'data':{ 'event_id': uuid, 'error' : 'Access denied'}}
        return {'code': 401, 'status': 'unauthorize', 'message': "access denied", 'data':{ 'event_id': uuid, 'error' : 'Access denied'}}
    return wrap

class Api(http.Controller):
    def check_keys(self, keys, vals):
        result = False
        for rec in keys:
            if rec in vals:
                result = True
            else:
                result = False
                break
        return result
    
    def check_keys_multiple(self, keys, vals):
        result = True
        for rec in keys:
            for val in vals:
                if rec in val:
                    result = True
                else:
                    result = False
                    return
        return result
    
    # @http.route(['/api_broilerx/getToken'], auth="none", type='json', methods=['POST'], csrf=False)
    # def user_authenticate(self, **values):
    #     try:
    #         db_name = tools.config['dbfilter']
    #     except:
    #         return {'code': 403, 'message': '`dbfilter` not found in your odoo configuration file.'}
    #     username = request.jsonrequest.get('username','0')
    #     password = request.jsonrequest.get('password','0')
    #     data = {}
    #     testLogin = False
    #     try:
    #         testLogin = request.session.authenticate(db_name, username, password)
    #     except:
    #         data = {'code':403, 'message': 'Forbidden Access','data':False}
    #     if testLogin != False:
    #         getToken = request.env['res.api.key']._retrieve_api_by_username(username)
    #         data = {'code':200, 'message': 'Client API','data':{'token': getToken}}
    #     else:
    #         data = {'code':403, 'message': 'Forbidden Access','data':False}
    #     return data
    
    # @validate_token
    # @http.route('/api_broilerx/delToken', auth="none", type="json", methods=['PUT'], csrf=False)
    # def user_unauthenticate(self, **kw):
    #     res = request.env['res.api.key']._del_token_key(request.uid)
    #     if res:
    #         data = {'code': 200, 'message': 'Success', 'data': []}
    #     else:
    #         data = {'code': 400, 'message': 'Failed', 'data': []}
    #     return data

    ## ODOO API ENDPOINT WEBHOOK
    @http.route(['/api_broilerx/create/token'], auth="none", type='json', methods=['POST'], csrf=False)
    def user_authenticate(self, **values):
        token = request.jsonrequest.get('token','')
        if token != '':
            request.uid = 1
            res = request.env['webhook.api.token'].create({'token': token})
            if res:
                data = {'code':200, 'status': 'success','message': 'Success create token','data':{'token': token}}
            else:
                data = {'code':403, 'status': 'failed','message': 'Forbidden Access','data':{}}
        else:
            data = {'code':401, 'status': 'failed','message': 'Failed body token','data':{}}
        return data
    
    @validate_webhook_token
    @http.route('/api_broilerx/webhook', auth="none", type="json", methods=['POST'], csrf=False)
    def api_webhook(self, **kw):
        data = []
        vals = request.jsonrequest
        keys = ('event_id', 'event_type', 'model', 'model_id')
        if self.check_keys(keys, vals):
            return {
                    'code':200, 
                    'status': 'success',
                    'message': 'Success data',
                    'data': vals
            }
            # if vals['model'] == 'farmers':
            #     external_api = request.env['external.api.key'].search([('code', '=', 'api_apps_user')])
            #     external_api.generate_token()
            #     headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache",'Authorization':"Bearer "+external_api.token,'User-Agent': 'ODOO_Dev'}
            #     json_data = {}
            #     response = requests.get(external_api.endpoint_url+'/'+vals['model']+'/'+vals['model_id'], data=json.dumps(json_data), headers=headers)
            #     data_apps = response.json()
            #     data = self.api_farmers(data_apps, vals['event_type'], vals['event_id'])
            # elif vals['model'] == 'houses':
            #     external_api = request.env['external.api.key'].search([('code', '=', 'api_apps_user')])
            #     external_api.generate_token()
            #     headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache",'Authorization':"Bearer "+external_api.token,'User-Agent': 'ODOO_Dev'}
            #     json_data = {}
            #     response = requests.get(external_api.endpoint_url+'/'+vals['model']+'/'+vals['model_id'], data=json.dumps(json_data), headers=headers)
            #     data_apps = response.json()
            #     data = self.api_kandang(data_apps, vals['event_type'], vals['event_id'])
            # elif vals['model'] == 'rearingPeriods':
            #     external_api = request.env['external.api.key'].search([('code', '=', 'api_apps_user')])
            #     external_api.generate_token()
            #     headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache",'Authorization':"Bearer "+external_api.token,'User-Agent': 'ODOO_Dev'}
            #     json_data = {}
            #     response = requests.get(external_api.endpoint_url+'/'+vals['model']+'/'+vals['model_id'], data=json.dumps(json_data), headers=headers)
            #     data_apps = response.json()
            #     data = self.api_periode(data_apps, vals['event_type'], vals['event_id'])
            # else:
            #     data = {
            #         'code':400, 
            #         'status': 'failed',
            #         'message': 'Failed body model',
            #         'data': { 'event_id': uuid, 'error' : 'Failed body model'}
            #     }
        else:
            data = {
                'code': 400, 
                'status': 'failed',
                'message': 'Failed Body Format', 
                'data': { 'event_id': uuid, 'error' : 'Failed Body Format'}
            } 
        return data

    def api_farmers(self, vals, method, uuid):
        data = []
        keys = ('kode_peternak', 'nama', 'nik', 'telepon', 'kode_unit','nomer_rekening','nama_rekening', 'nama_bank', 'npwp')
        if self.check_keys(keys, vals):
            if method == 'CREATE':
                farmers = request.env['res.partner'].search([('ref', '=', vals['kode_peternak'])])
                if not farmers:
                    farmers_mobile = request.env['res.partner'].search([('phone', '=', vals['telepon'])])
                    if farmers_mobile:
                        return {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed Duplicate telepon Farmers', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Duplicate telepon Farmers'}
                        }
                    unit_id = request.env['unit.rhpp'].search([('short_code', '=', vals['kode_unit'])])
                    if not unit_id:
                        return {
                            'code': 400,
                            'status': 'failed', 'message': 'Failed Unit Not Found', 
                            'data': { 'event_id': uuid,'error' :'Failed Unit Not Found'}
                        }
                    category = request.env['res.partner.category'].search([('name', '=', 'peternak')])
                    bank = request.env['res.bank'].search([('name','=', vals['nama_bank'])])
                    if not bank:
                        return {
                            'code': 400,
                            'status': 'failed', 'message': 'Failed Bank Not Found', 
                            'data': { 'event_id': uuid,'error' :'Failed Bank Not Found'}
                        }
                    data_farmers = {
                        'name': vals['nama'],
                        'phone': vals['telepon'],
                        'ref': vals['kode_peternak'],
                        'nik': vals['nik'],
                        'unit_rhpp': unit_id.id,
                        'vat': vals['npwp'],
                        'active': True, 
                        'category_id': [(4, category.id)],
                        'bank_ids': [
                                (0, 0, {
                                        'acc_holder_name': vals['nama_rekening'],
                                        'acc_number': vals['nomer_rekening'],
                                        'bank_id': bank.id
                                    }
                                ),
                        ]
                    }
                    res = request.env['res.partner'].create(data_farmers)     
                    if res:
                        data = {
                            'code': 201, 
                            'status': 'success',
                            'message': 'Data successfully received'
                        }
                    else:
                        data = {
                            'code': 400, 
                            'status': 'failed', 
                            'message': 'Failed Create Farmers', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Create Farmers'}
                        }
                else:
                    data = {
                        'code': 400, 
                        'status': 'failed',
                        'message': 'Failed Duplicate Kode Peternak', 
                        'data': { 'event_id': uuid, 'error' : 'Failed Duplicate Kode Peternak'}
                    }
            elif method == 'UPDATE':
                farmers = request.env['res.partner'].search([('ref', '=', vals['kode_peternak'])])
                if farmers:
                    farmers_mobile = request.env['res.partner'].search([('mobile', '=', vals['telepon'])])
                    if farmers_mobile:
                        if farmers_mobile.id != vals['id']:
                            return {
                                'code': 400,
                                'status': 'failed', 
                                'message': 'Failed Duplicate telepon Farmers', 
                                'data': { 'event_id': uuid, 'error' : 'Failed Duplicate telepon Farmers'}
                            }
                    unit_id = request.env['unit.rhpp'].search([('short_code', '=', vals['kode_unit'])])
                    if not unit_id:
                        return {
                            'code': 400,
                            'status': 'failed', 
                            'message': 'Failed Unit Not Found', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Unit Not Found'}
                        }
                    bank = request.env['res.bank'].search([('name','=', vals['nama_bank'])])
                    if not bank:
                        return {
                            'code': 400,
                            'status': 'failed', 'message': 'Failed Bank Not Found', 
                            'data': { 'event_id': uuid,'error' :'Failed Bank Not Found'}
                        }
                    data_farmers = {
                        'name': vals['nama'],
                        'phone': vals['telepon'],
                        'nik': vals['nik'],
                        'unit_rhpp': unit_id.id,
                        'vat': vals['npwp'],
                    }
                    if farmers.bank_ids:
                        data_farmers['bank_ids'] = [
                                (1, farmers.bank_ids[0].id, {
                                        'acc_holder_name': vals['nama_rekening'],
                                        'acc_number': vals['nomer_rekening'],
                                        'bank_id': bank.id
                                    }
                                ),
                        ]
                    else:
                        data_farmers['bank_ids'] = [
                                (0, 0, {
                                        'acc_holder_name': vals['nama_rekening'],
                                        'acc_number': vals['nomer_rekening'],
                                        'bank_id': bank.id
                                    }
                                ),
                        ]
                    res = farmers.write(data_farmers)     
                    if res:
                        data = {
                            'code': 200, 
                            'status': 'success',
                            'message': 'Data successfully updated'
                        }
                    else:
                        data = {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed Update Farmers', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Update Farmers'}
                        }
                else:
                    data = {
                        'code': 400, 
                        'status': 'failed',
                        'message': 'Failed Farmers Not Exists', 
                        'data': { 'event_id': uuid, 'error' : 'Failed Farmers Not Exists'}
                    }
            elif method == 'DELETE':
                farmers = request.env['res.partner'].search([('ref', '=', vals['kode_peternak'])])
                if farmers:
                    data_farmers = {
                        'active': False
                    }
                    res = farmers.write(data_farmers)     
                    if res:
                        data = {
                            'code': 200, 
                            'status': 'success',
                            'message': 'Data successfully deleted'
                        }
                    else:
                        data = {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed deleted Farmers', 
                            'data': { 'event_id': uuid, 'error' : 'Failed deleted Farmers'}
                        }
                else:
                    data = {
                        'code': 400, 
                        'status': 'failed',
                        'message': 'Failed Farmers Not Exists', 
                        'data': { 'event_id': uuid, 'error' : 'Failed Farmers Not Exists'}
                    }
            else:
                data = {
                    'code': 400, 
                    'status': 'failed',
                    'message': 'Failed Check Method', 
                    'data': { 'event_id': uuid, 'error' : 'Failed Check Method'}
                }
        else:
            data = {
                'code': 400, 
                'status': 'failed',
                'message': 'Failed Body Farmers', 
                'data': { 'event_id': uuid, 'error' : 'Failed Body Farmers'}
            }    
        return data
    
    def api_kandang(self, vals, method, uuid):
        data = []
        keys = ('kode_kandang', 'kode_peternak', 'no_kandang', 'jenis_kandang', 'alamat_kandang', 'kode_unit')
        if self.check_keys(keys, vals):
            if method == 'CREATE':
                kandang = request.env['populasi.kandang'].search([])
                if kandang:
                    kandang = [x for x in kandang if x.kode_kandang == vals['kode_kandang']]
                    if kandang:
                        kandang = kandang[0]
                if not kandang:
                    jenis_kandang = ''
                    if vals['jenis_kandang'] == 'Close House':
                        jenis_kandang = 'close'
                    elif vals['jenis_kandang'] == 'Semi Close House':
                        jenis_kandang = 'semi'
                    elif vals['jenis_kandang'] == 'Open House':
                        jenis_kandang = 'open'
                    else:
                        return {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Check jenis kandang Clouse House, Semi Close House, and Open House', 
                            'data': { 'event_id': uuid, 'error' : 'Check jenis kandang Clouse House, Semi Close House, and Open House'}
                        }
                    peternak = request.env['res.partner'].search([('ref', '=', vals['kode_peternak'])])
                    if not peternak:
                        return {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed peternak not found', 
                            'data': { 'event_id': uuid, 'error' : 'Failed peternak not found'}
                        }
                    unit_id = request.env['unit.rhpp'].search([('short_code', '=', vals['kode_unit'])])
                    if not unit_id:
                        return {
                            'code': 400,
                            'status': 'failed', 
                            'message': 'Failed Unit Not Found', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Unit Not Found'}
                        }
                    category = request.env['res.partner.category'].search([('name', '=', 'peternak')])
                    data_farmers = {
                        'name': peternak.name+' '+vals['no_kandang'],
                        'kode_kandang': vals['kode_kandang'],
                        'nomor_kandang': vals['no_kandang'],
                        'peternak': peternak.id,
                        'jenis_kandang': jenis_kandang,
                        'alamat_kandang': vals['alamat_kandang'],
                        'unit_kandang': unit_id.id,
                        'populasi': 0,
                        'active': True
                    }
                    res = request.env['populasi.kandang'].create(data_farmers)     
                    if res:
                        data = {
                            'code': 201, 
                            'status': 'success',
                            'message': 'Data successfully received'
                        }
                    else:
                        data = {
                            'code': 400, 
                            'status': 'failed', 
                            'message': 'Failed Create Kandang', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Create Kandang'}
                        }
                else:
                    data = {
                        'code': 400, 
                        'status': 'failed',
                        'message': 'Failed Duplicate Kode Kandang', 
                        'data': { 'event_id': uuid, 'error' : 'Failed Duplicate Kode Kandang'}
                    }
            elif method == 'UPDATE':
                kandang = request.env['populasi.kandang'].search([])
                if kandang:
                    kandang = [x for x in kandang if x.kode_kandang == vals['kode_kandang']]
                    if kandang:
                        kandang = kandang[0]
                if kandang:
                    jenis_kandang = ''
                    if vals['jenis_kandang'] == 'Close House':
                        jenis_kandang = 'close'
                    elif vals['jenis_kandang'] == 'Semi Close House':
                        jenis_kandang = 'semi'
                    elif vals['jenis_kandang'] == 'Open House':
                        jenis_kandang = 'open'
                    else:
                        return {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Check jenis kandang Clouse House, Semi Close House, and Open House', 
                            'data': { 'event_id': uuid, 'error' : 'Check jenis kandang Clouse House, Semi Close House, and Open House'}
                        }
                    peternak = request.env['res.partner'].search([('ref', '=', vals['kode_peternak'])])
                    if not peternak:
                        return {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed peternak not found', 
                            'data': { 'event_id': uuid, 'error' : 'Failed peternak not found'}
                        }
                    unit_id = request.env['unit.rhpp'].search([('short_code', '=', vals['kode_unit'])])
                    if not unit_id:
                        return {
                            'code': 400,
                            'status': 'failed', 
                            'message': 'Failed Unit Not Found', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Unit Not Found'}
                        }
                    data_farmers = {
                        'name': peternak.name+' '+vals['no_kandang'],
                        'nomor_kandang': vals['no_kandang'],
                        'peternak': peternak.id,
                        'jenis_kandang': jenis_kandang,
                        'alamat_kandang': vals['alamat_kandang'],
                        'unit_kandang': unit_id.id
                    }
                    res = kandang.write(data_farmers)     
                    if res:
                        data = {
                            'code': 200, 
                            'status': 'success',
                            'message': 'Data successfully updated'
                        }
                    else:
                        data = {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed Update Kandang', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Update Kandang'}
                        }
                else:
                    data = {
                        'code': 400, 
                        'status': 'failed',
                        'message': 'Failed Kandang Not Exists', 
                        'data': { 'event_id': uuid, 'error' : 'Failed Kandang Not Exists'}
                    }
            elif method == 'DELETE':
                kandang = request.env['populasi.kandang'].search([])
                if kandang:
                    kandang = [x for x in kandang if x.kode_kandang == vals['kode_kandang']]
                    if kandang:
                        kandang = kandang[0]
                if kandang:
                    data_kandang = {
                        'active': False
                    }
                    res = kandang.write(data_kandang)     
                    if res:
                        data = {
                            'code': 200, 
                            'status': 'success',
                            'message': 'Data successfully deleted'
                        }
                    else:
                        data = {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed Delete Kandang', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Delete Kandang'}
                        }
                else:
                    data = {
                        'code': 400, 
                        'status': 'failed',
                        'message': 'Failed Kandang Not Exists', 
                        'data': { 'event_id': uuid, 'error' : 'Failed Kandang Not Exists'}
                    }
            else:
                data = {
                    'code': 400, 
                    'status': 'failed',
                    'message': 'Failed Check Method', 
                    'data': { 'event_id': uuid, 'error' : 'Failed Check Method'}
                }
        else:
            data = {
                'code': 400, 
                'status': 'failed',
                'message': 'Failed Body Farmers', 
                'data': { 'event_id': uuid, 'error' : 'Failed Body Farmers'}
            }    
        return data
    
    def api_periode(self, vals, method, uuid):
        data = []
        keys = ('kode_periode', 'kode_kandang', 'no_periode', 'populasi', 'tanggal_doc_in','ppl')
        if self.check_keys(keys, vals):
            if method == 'CREATE':
                periode = request.env['form.kontrak.peternak'].search([('name', '=', vals['kode_periode'])])
                if not periode:
                    kandang = request.env['populasi.kandang'].search([])
                    if kandang:
                        kandang = [x for x in kandang if x.kode_kandang == vals['kode_kandang']]
                        if kandang:
                            kandang = kandang[0]
                        else:
                            return {
                                'code': 400, 
                                'status': 'failed',
                                'message': 'Failed kandang not found', 
                                'data': { 'event_id': uuid, 'error' : 'Failed kandang not found'}
                            }
                    else:
                        return {
                                'code': 400, 
                                'status': 'failed',
                                'message': 'Failed kandang not found', 
                                'data': { 'event_id': uuid, 'error' : 'Failed kandang not found'}
                        }
                    
                    try:
                        tgl_doc_in = datetime.strptime(vals['tanggal_doc_in'], "%d %B %Y")
                        tgl_doc_in = tgl_doc_in.strftime("%Y-%m-%d")
                    except:
                        data = {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed check format date', 
                            'data': { 'event_id': uuid, 'error' : 'Failed check format date'}
                        }
                    data_periode = {
                        'name': vals['kode_periode'],
                        'populasi_kandang': kandang.id,
                        'contract_periode': vals['no_periode'],
                        'contract_ppl': vals['ppl'],
                        'contact_doc_in': tgl_doc_in,
                        'populasi': vals['populasi']
                    }
                    res = request.env['form.kontrak.peternak'].create(data_periode)     
                    if res:
                        data = {
                            'code': 201, 
                            'status': 'success',
                            'message': 'Data successfully received'
                        }
                    else:
                        data = {
                            'code': 400, 
                            'status': 'failed', 
                            'message': 'Failed Create Periode', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Create Periode'}
                        }
                else:
                    data = {
                        'code': 400, 
                        'status': 'failed',
                        'message': 'Failed Duplicate Kode Periode', 
                        'data': { 'event_id': uuid, 'error' : 'Failed Duplicate Kode Periode'}
                    }
            elif method == 'UPDATE':
                periode = request.env['form.kontrak.peternak'].search([('name', '=', vals['kode_periode'])])
                if periode:
                    kandang = request.env['populasi.kandang'].search([])
                    if kandang:
                        kandang = [x for x in kandang if x.kode_kandang == vals['kode_kandang']]
                        if kandang:
                            kandang = kandang[0]
                        else:
                            return {
                                'code': 400, 
                                'status': 'failed',
                                'message': 'Failed kandang not found', 
                                'data': { 'event_id': uuid, 'error' : 'Failed kandang not found'}
                            }
                    else:
                        return {
                                'code': 400, 
                                'status': 'failed',
                                'message': 'Failed kandang not found', 
                                'data': { 'event_id': uuid, 'error' : 'Failed kandang not found'}
                        }
                    try:
                        tgl_doc_in = datetime.strptime(vals['tanggal_doc_in'], "%d %B %Y")
                        tgl_doc_in = tgl_doc_in.strftime("%Y-%m-%d")
                    except:
                        data = {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed check format date', 
                            'data': { 'event_id': uuid, 'error' : 'Failed check format date'}
                        }
                    data_periode = {
                        'populasi_kandang': kandang.id,
                        'contract_periode': vals['no_periode'],
                        'contract_ppl': vals['ppl'],
                        'contact_doc_in': tgl_doc_in,
                        'populasi': vals['populasi']
                    }
                    res = periode.write(data_periode)     
                    if res:
                        data = {
                            'code': 200, 
                            'status': 'success',
                            'message': 'Data successfully updated'
                        }
                    else:
                        data = {
                            'code': 400, 
                            'status': 'failed',
                            'message': 'Failed Update Periode', 
                            'data': { 'event_id': uuid, 'error' : 'Failed Update Period'}
                        }
                else:
                    data = {
                        'code': 400, 
                        'status': 'failed',
                        'message': 'Failed Farmers Not Exists', 
                        'data': { 'event_id': uuid, 'error' : 'Failed Period Not Exists'}
                    }
            elif method == 'DELETE':
                periode = request.env['form.kontrak.peternak'].search([('name', '=', vals['kode_periode'])])
                if periode:
                    if periode.state == 'new':
                        res = periode.unlink()     
                        if res:
                            data = {
                                'code': 200, 
                                'status': 'success',
                                'message': 'Data successfully deleted'
                            }
                        else:
                            data = {
                                'code': 400, 
                                'status': 'failed',
                                'message': 'Failed deleted Periode', 
                                'data': { 'event_id': uuid, 'error' : 'Failed deleted Periode'}
                            }
                    else:
                        data = {
                                'code': 400, 
                                'status': 'failed',
                                'message': 'Failed deleted periode running', 
                                'data': { 'event_id': uuid, 'error' : 'Failed deleted periode running'}
                            }
                else:
                    data = {
                        'code': 400, 
                        'status': 'failed',
                        'message': 'Failed Farmers Not Exists', 
                        'data': { 'event_id': uuid, 'error' : 'Failed Periode Not Exists'}
                    }
            else:
                data = {
                    'code': 400, 
                    'status': 'failed',
                    'message': 'Failed Check Method', 
                    'data': { 'event_id': uuid, 'error' : 'Failed Check Method'}
                }
        else:
            data = {
                'code': 400, 
                'status': 'failed',
                'message': 'Failed Body Farmers', 
                'data': { 'event_id': uuid, 'error' : 'Failed Body Periode'}
            }    
        return data