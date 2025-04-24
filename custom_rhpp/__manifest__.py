# -*- coding: utf-8 -*-
{
    'name': "custom_rhpp",

    'summary': "Config and setting module rhpp",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','web','analytic','account','contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/restrict_groups.xml',
        'data/sequence_number.xml',
        'views/analytic_rhpp_views.xml',

        'views/res_partner_inherit.xml',
        'views/contract_rhpp.xml',
        'views/pricelist_ayam.xml',
        'views/pricelist_sapronak.xml',
        'views/populasi_kandang_views.xml',
        'views/account_analytic_group_views.xml',
        'views/account_analytic_line_views.xml',
        'views/product_supplierinfo_views.xml',

        'views/bonus_jenis_kandang_views.xml',
        'views/bonus_ip_views.xml',
        'views/bonus_pasar_views.xml',
        'views/bonus_capaian_fcr_views.xml',
        'views/bonus_daya_hidup_views.xml',
        'views/unit_rhpp_views.xml',
        'views/pph_pasal_21_views.xml',
        'views/standar_fcr_views.xml',
        'views/account_analytic_account_views.xml',
        'views/account_move_line_views.xml',
        'views/klausul_kontrak_views.xml',
        'report/report_print_rhpp.xml',
        'report/report_print_kontrak_peternak.xml',
        'report/report_print_perjanjian_mitra_peternak.xml',
        'views/reports.xml',
        'views/template_contract_rhpp.xml',
        'views/nama_jabatan_views.xml',
        
        'wizard/analytic_rhpp_journal_wizard.xml',
        'wizard/popup_tabungan_rhpp_wizard_views.xml'
    ],
    'assets': {
    'web.assets_backend': [
        'custom_rhpp/static/src/css/rhpp_html.css',
	],
    }
}
