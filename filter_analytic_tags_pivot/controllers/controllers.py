# -*- coding: utf-8 -*-
# from odoo import http


# class FilterAnalyticTagsPivot(http.Controller):
#     @http.route('/filter_analytic_tags_pivot/filter_analytic_tags_pivot', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/filter_analytic_tags_pivot/filter_analytic_tags_pivot/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('filter_analytic_tags_pivot.listing', {
#             'root': '/filter_analytic_tags_pivot/filter_analytic_tags_pivot',
#             'objects': http.request.env['filter_analytic_tags_pivot.filter_analytic_tags_pivot'].search([]),
#         })

#     @http.route('/filter_analytic_tags_pivot/filter_analytic_tags_pivot/objects/<model("filter_analytic_tags_pivot.filter_analytic_tags_pivot"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('filter_analytic_tags_pivot.object', {
#             'object': obj
#         })
