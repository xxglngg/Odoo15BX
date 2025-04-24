# -*- coding: utf-8 -*-
# from odoo import http


# class PivotInventoryStockReport(http.Controller):
#     @http.route('/pivot_inventory_stock_report/pivot_inventory_stock_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pivot_inventory_stock_report/pivot_inventory_stock_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pivot_inventory_stock_report.listing', {
#             'root': '/pivot_inventory_stock_report/pivot_inventory_stock_report',
#             'objects': http.request.env['pivot_inventory_stock_report.pivot_inventory_stock_report'].search([]),
#         })

#     @http.route('/pivot_inventory_stock_report/pivot_inventory_stock_report/objects/<model("pivot_inventory_stock_report.pivot_inventory_stock_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pivot_inventory_stock_report.object', {
#             'object': obj
#         })
