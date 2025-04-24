# -*- coding: utf-8 -*-
# from odoo import http


# class InformationManyToManySalesOrder(http.Controller):
#     @http.route('/information_many_to_many_sales_order/information_many_to_many_sales_order', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/information_many_to_many_sales_order/information_many_to_many_sales_order/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('information_many_to_many_sales_order.listing', {
#             'root': '/information_many_to_many_sales_order/information_many_to_many_sales_order',
#             'objects': http.request.env['information_many_to_many_sales_order.information_many_to_many_sales_order'].search([]),
#         })

#     @http.route('/information_many_to_many_sales_order/information_many_to_many_sales_order/objects/<model("information_many_to_many_sales_order.information_many_to_many_sales_order"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('information_many_to_many_sales_order.object', {
#             'object': obj
#         })
