{
    'name': "Custom Report Aging Payable/Receivable",

    'summary': """
        Custom Account Report Aging Payable/Receivable :
        - Aging Payable Custom Report
        - Aging Receivable Custom Report
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "erpana_tio",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_reports'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/account_financial_report_data.xml',
        'data/aged_period_data.xml',
        'views/account_aged_period_views.xml',
        'views/report_financial.xml',
    ],
    # only loaded in demonstration modes
}
# -*- coding: utf-8 -*-
