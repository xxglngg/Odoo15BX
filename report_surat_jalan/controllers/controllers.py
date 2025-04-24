# -*- coding: utf-8 -*-
# from odoo import http


# class ReportSuratJalan(http.Controller):
#     @http.route('/report_surat_jalan/report_surat_jalan', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_surat_jalan/report_surat_jalan/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_surat_jalan.listing', {
#             'root': '/report_surat_jalan/report_surat_jalan',
#             'objects': http.request.env['report_surat_jalan.report_surat_jalan'].search([]),
#         })

#     @http.route('/report_surat_jalan/report_surat_jalan/objects/<model("report_surat_jalan.report_surat_jalan"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_surat_jalan.object', {
#             'object': obj
#         })
