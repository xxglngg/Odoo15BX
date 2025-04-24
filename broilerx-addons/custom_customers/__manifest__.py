# -*- coding: utf-8 -*-
{
    'name': "Custom Customers",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Erpana",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['web','base','contacts', 'custom_rhpp'],

    'license': 'LGPL-3',

    'data': [
        'security/ir.model.access.csv',
        'data/res_partner_category.xml',
        'data/res_partner_code_sequence.xml',
        'views/res_partner_inherit.xml',
        'views/res_partner_segmentasi_views.xml',
        'views/contact_salesman_views.xml'
    ],
}
