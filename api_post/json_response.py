import logging
import json
import datetime
from odoo.tools import date_utils
from odoo.http import Response, JsonRequest

class JsonRequestPatch(JsonRequest):

    def _json_response(self, result=None, error=None):
        path = self.httprequest.path
        if 'api_broilerx' in path:
            response = {}
            default_code = 200
            if error is not None:
                response = error
                this_default_code = 500
            if result is not None:
                response = result
                if 'code' in response:
                    this_default_code = response['code']
                    try:
                        del response['code']
                    except KeyError:
                        pass

            mime = 'application/json'
            body = json.dumps(response, default=date_utils.json_default)

            return Response(
                body, status=this_default_code,
                headers=[('Content-Type', mime), ('Content-Length', len(body))]
            )
        else:
            response = {
                'jsonrpc': '2.0',
                'id': self.jsonrequest.get('id')
                }
            default_code = 200
            if error is not None:
                response['error'] = error
            if result is not None:
                response['result'] = result

            mime = 'application/json'
            body = json.dumps(response, default=date_utils.json_default)

            return Response(
                body, status=error and error.pop('http_status', default_code ) or default_code,
                headers=[('Content-Type', mime), ('Content-Length', len(body))]
            )
        
        
JsonRequest._json_response = JsonRequestPatch._json_response
