# See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner Credit Time Limit',
    'version': '15.0.0.1',
    'price': 70.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'author': 'Caliber Softwares',
    'website': 'calibersoftware.odoo.com/',    
    'support': 'calibersware@gmail.com',
    'category': 'Sale',
    'summary': """This module allow you to set Customer credit time limit., Credit limit, Not allow in specific time limit exceed, Check time and not allow to create Order""",
    'description': """
        Credit Limit, Odoo credit limit,Credit limit by period, period wise credit limit,
        Credit time limit during new order raise system will check customer credit time limit.
        for example Customer: Anand Baksi have credit time limit is 45 days
        Anand Baksi not fully paid last 50 days and recently raise new order so system will raise warning
        'Can not confirm Sale Order, Total mature due days 50 as on today(01-08-2020) Check Partner Accounts or Period Credit Limits !' so we informed to customer for that due records.
        customer credit limit
        customer create credit limit on period
        Customer Credit time limit
        Partner credit limit period time month, year, days
    """,
    'depends': [
        'sale_management',
    ],
    'data': [
        'views/partner_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
