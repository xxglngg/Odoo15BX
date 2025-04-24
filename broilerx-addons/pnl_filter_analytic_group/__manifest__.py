# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PnL Filter by Analytic Group',
    'summary': 'PnL Filter by Analytic Group',
    'description': """
PnL Filter by Analytic Group
    """,
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['base', 'account_reports'],
    'assets': {
        'web.assets_backend': [
            'pnl_filter_analytic_group/static/src/js/account_reports_mod.js'
        ]},
    'auto_install': False,
    'data': [
    ],
    'license': '',
}
