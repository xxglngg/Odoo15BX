from odoo import models


class DeliveryOrderXlsx(models.AbstractModel):
    _name = 'report.custom_accounting.report_database_rhpp_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Accounting Xlsx Report"

    def generate_xlsx_report(self, workbook, data, account):
        sheet = workbook.add_worksheet('Database RHPP')
        bold = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'dd/mm/yy'})
        price_style = workbook.add_format({'num_format': '#,##0.00'})
        align_center = workbook.add_format({'align': 'center'})
        align_center_b = workbook.add_format({'align': 'center', 'bold': True})
        row = 0
        col = 0
        sheet.set_column('A:A', 50)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 30)
        sheet.set_column('G:G', 30)
        sheet.set_column('H:H', 30)
        sheet.set_column('I:I', 30)
        sheet.set_column('J:J', 30)
        sheet.set_column('K:K', 30)
        sheet.set_column('L:L', 30)
        sheet.set_column('M:M', 30)
        sheet.set_column('N:N', 20)
        sheet.write(row, col, 'Analytic Account/Analytic Account', bold)
        sheet.write(row, col+1, 'Move', bold)
        sheet.write(row, col+2, 'Partner', bold)
        sheet.write(row, col+3, 'Invoice Date', bold)
        sheet.write(row, col+4, 'Due Date', bold)
        sheet.write(row, col+5, 'Product Category', bold)
        sheet.write(row, col+6, 'Product', bold)
        sheet.write(row, col+7, 'Move/Invoice lines/Note', bold)
        sheet.write(row, col+8, 'Product Quantity', bold)
        sheet.write(row, col+9, 'Product/Unit of Measure', bold)
        sheet.write(row, col+10, 'Average Price', bold)
        sheet.write(row, col+11, 'Untaxed Total', bold)
        sheet.write(row, col+12, 'Revenue/Expense Account', bold)
        sheet.write(row, col+13, 'Move/Tax', bold)
        for obj in account:
            row += 1
            sheet.write(row, col, obj.analytic_account_id.name)
            sheet.write(row, col+1, obj.move_id.name)
            sheet.write(row, col+2, obj.partner_id.name)
            sheet.write(row, col+3, obj.invoice_date, date_format)
            sheet.write(row, col+4, obj.invoice_date_due, date_format)
            sheet.write(row, col+5, obj.product_categ_id.name)
            sheet.write(row, col+6, obj.product_id.name)
            for move in obj.move_id.invoice_line_ids:
                line = move.filtered(lambda r : r.product_id.id == obj.product_id.id)
                if line.note:
                    sheet.write(row, col+7, line.note)
                if line.note == ' ':
                    sheet.write(row, col+7, ' ')
            sheet.write(row, col+8, obj.quantity, price_style)
            sheet.write(row, col+9, obj.product_uom_id.name)
            sheet.write(row, col+10, obj.price_average, price_style)
            sheet.write(row, col+11, obj.price_subtotal, price_style)
            sheet.write(row, col+12, obj.account_id.name)
            sheet.write(row, col+13, obj.move_id.amount_tax_signed, price_style)