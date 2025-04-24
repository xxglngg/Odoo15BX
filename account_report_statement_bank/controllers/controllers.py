# -*- coding: utf-8 -*-
# from odoo import http


# class AccountReportStatementBank(http.Controller):
#     @http.route('/account_report_statement_bank/account_report_statement_bank', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_report_statement_bank/account_report_statement_bank/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_report_statement_bank.listing', {
#             'root': '/account_report_statement_bank/account_report_statement_bank',
#             'objects': http.request.env['account_report_statement_bank.account_report_statement_bank'].search([]),
#         })

#     @http.route('/account_report_statement_bank/account_report_statement_bank/objects/<model("account_report_statement_bank.account_report_statement_bank"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_report_statement_bank.object', {
#             'object': obj
#         })
