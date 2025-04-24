# -*- coding: utf-8 -*-
# from odoo import http


# class AdditionalFieldReport(http.Controller):
#     @http.route('/additional_field_report/additional_field_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/additional_field_report/additional_field_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('additional_field_report.listing', {
#             'root': '/additional_field_report/additional_field_report',
#             'objects': http.request.env['additional_field_report.additional_field_report'].search([]),
#         })

#     @http.route('/additional_field_report/additional_field_report/objects/<model("additional_field_report.additional_field_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('additional_field_report.object', {
#             'object': obj
#         })
