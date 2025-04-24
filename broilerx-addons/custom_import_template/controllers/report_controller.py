from odoo import http
from odoo.http import content_disposition, request
from datetime import date
from io import BytesIO
import xlsxwriter
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import quote_sheetname
import os


class ReportController(http.Controller):
    @http.route('/xls_report/template_report_purchase',
                type='http', auth='user')
    def get_xlsx_template_report_purchase(self, data=None):
        """ function to generate xls report """
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('{}'.format('Template Import PO') + '.xlsx'))
            ]
        )
        fp = BytesIO()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path.replace('controllers','static/src/template/Template Import PO.xlsx')
        wb = openpyxl.load_workbook(dir_path)
        ws_analytic = wb['Analytic Account']
        ws_analytic.delete_cols(2,999999999)
        account_analytics = request.env['account.analytic.account'].search([('state', '=', 'unlocked'),('active', '=', True)])
        for col_num, data in enumerate(account_analytics):
            ws_analytic['A'+str(2 + col_num)] = data.name
            
        ws_product = wb['Produk']
        ws_product.delete_cols(2,999999999)
        products = request.env['product.product'].search([('company_id', 'in', (False, request.env.company.id)),('active', '=', True),('categ_id.name', 'in', ['Obat, Vaksin & Kimia','DOC FS','Starter','Pre Starter','Finisher','Live Bird'])])
        for col_num, data in enumerate(products):
            ws_product['A'+str(2 + col_num)] = data.name

        ws_vendor = wb['Vendor']
        ws_vendor.delete_cols(2,999999999)
        partners = request.env['res.partner'].search([('category_id.name', '=', 'Vendor'),('active', '=', True)])
        for col_num, data in enumerate(partners):
            ws_vendor['A'+str(2 + col_num)] = data.name

        ws_tax_purchase = wb['Tax']
        ws_tax_purchase.delete_cols(2,999999999)
        tax_purchase = request.env['account.tax'].search([('type_tax_use', '=', 'purchase'),('active', '=', True)])
        for col_num, data in enumerate(tax_purchase):
            ws_tax_purchase['A'+str(2 + col_num)] = data.name
        
        ws_template = wb['Template']
        data_vendor = DataValidation(type="list",formula1="Vendor!$A$2:$A$999999", allow_blank=True)
        ws_template.add_data_validation(data_vendor)
        data_vendor.add("A2")
        
        data_analytic = DataValidation(type="list",formula1="'Analytic Account'!$A$2:$A$999999")
        ws_template.add_data_validation(data_analytic)
        data_analytic.add("C2")
        
        data_produk = DataValidation(type="list",formula1="Produk!$A$2:$A$999999")
        ws_template.add_data_validation(data_produk)
        data_produk.add("F2")

        data_tax_purchase = DataValidation(type="list",formula1="Tax!$A$2:$A$999999")
        ws_template.add_data_validation(data_tax_purchase)
        data_tax_purchase.add("I2")
        
        wb.save(fp)
        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
        return response
    
    @http.route('/xls_report/template_report_sale',
                type='http', auth='user')
    def get_xlsx_template_report_sale(self, data=None):
        """ function to generate xls report """
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('{}'.format('Template Import SO') + '.xlsx'))
            ]
        )
        fp = BytesIO()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path.replace('controllers','static/src/template/Template Import SO.xlsx')
        wb = openpyxl.load_workbook(dir_path)

        ws_peternak = wb['Data Peternak']
        ws_peternak.delete_cols(2,999999999)
        peternak = request.env['res.partner'].search([('active', '=', True),('is_peternak', '=', True)])
        for col_num, data in enumerate(peternak):
            ws_peternak['A'+str(2 + col_num)] = data.name

        ws_product = wb['Produk']
        ws_product.delete_cols(2,999999999)
        products = request.env['product.product'].search([('company_id', 'in', (False, request.env.company.id)),('active', '=', True),('categ_id.name', 'in', ['Obat, Vaksin & Kimia','DOC FS','Starter','Pre Starter','Finisher','Live Bird'])])
        for col_num, data in enumerate(products):
            ws_product['A'+str(2 + col_num)] = data.name

        ws_payment_term = wb['Payment Terms']
        ws_payment_term.delete_cols(2,999999999)
        payment_term = request.env['account.payment.term'].search([('active', '=', True)])
        for col_num, data in enumerate(payment_term):
            ws_payment_term['A'+str(2 + col_num)] = data.name
        
        ws_tax_sale = wb['Tax']
        ws_tax_sale.delete_cols(2,999999999)
        tax_sale = request.env['account.tax'].search([('type_tax_use', '=', 'sale'),('active', '=', True)])
        for col_num, data in enumerate(tax_sale):
            ws_tax_sale['A'+str(2 + col_num)] = data.name
        
        ws_template = wb['Template']
        data_peternak = DataValidation(type="list",formula1="'Data Peternak'!$A$2:$A$999999", allow_blank=True)
        ws_template.add_data_validation(data_peternak)
        data_peternak.add("A2")

        data_produk = DataValidation(type="list",formula1="Produk!$A$2:$A$999999")
        ws_template.add_data_validation(data_produk)
        data_produk.add("E2")
        
        data_payment_terms = DataValidation(type="list",formula1="'Payment Terms'!$A$2:$A$999999")
        ws_template.add_data_validation(data_payment_terms)
        data_payment_terms.add("D2")

        data_tax_sale = DataValidation(type="list",formula1="Tax!$A$2:$A$999999")
        ws_template.add_data_validation(data_tax_sale)
        data_tax_sale.add("I2")
        
        wb.save(fp)
        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
        return response