# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request, content_disposition, route
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar


class additional_field_pivot_stock(models.TransientModel):
    _name = 'report.pivot.stock'
    _description = "Module Report Pivot Stock"

    saldo_awal = fields.Many2one('report.pivot.stock.saldo.awal')
    saldo_akhir = fields.Many2one('report.pivot.stock.saldo.akhir')
    saldo_in = fields.Many2one('report.pivot.stock.saldo.in')
    saldo_out = fields.Many2one('report.pivot.stock.saldo.out')
    saldo_adjustment = fields.Many2one('report.pivot.stock.saldo.adjustment')

    qty = fields.Float()
    harga_satuan = fields.Float()
    nilai = fields.Float()
    saldo = fields.Char()

    product_tmpl_id = fields.Many2one('product.template')
    location = fields.Many2one('stock.location')
    notes_date = fields.Datetime()

    date_range = fields.Datetime(store=False, search='_search_date')

    def _search_date(self, operator, value):
        self._cr.execute("""
                    DELETE FROM report_pivot_stock
                """)
        print(self)
        print(operator)
        print(value)
        nilai_awal = 0
        nilai_akhir = 0
        nilai_in = 0
        nilai_out = 0
        nilai_adjustment = 0

        harga_satuan_awal = 0
        harga_satuan_akhir = 0
        harga_satuan_in = 0
        harga_satuan_out = 0
        harga_satuan_adjustment = 0

        saldo_in = 0
        saldo_out = 0
        saldo_awal = 0
        saldo_akhir = 0
        saldo_adjustment = 0

        pivot_stock_move_line = []
        date = self.validate(value)
        date_filter = date.strftime('%Y-%m-%d')
        # Mencari product yang ada di stock move line di tanggal tsb
        first_date = date.replace(day=1).strftime('%Y-%m-%d')
        last_date = date.replace(day = calendar.monthrange(date.year, date.month)[1])

        product = self.env['stock.move.line'].sudo().search([('date','<=',date_filter),('state','=','done')])

        list_product = []
        list_product.append(product.product_id.product_tmpl_id.ids)
        list_product_cleansing = [i for n, i in enumerate(list_product[0]) if i not in list_product[0][:n]]
        print(list_product_cleansing)

        if list_product_cleansing:
            for data_product in list_product_cleansing:
                tanggal_stock_awal = (date - relativedelta(months=1)).strftime('%Y-%m-%d')

                stock_flow_awal = self.env['stock.move.line'].sudo().search([('product_id.product_tmpl_id', '=', data_product),('date', '<=', tanggal_stock_awal),('state','=','done')], order="id asc")
                stock_flow_akhir = self.env['stock.move.line'].sudo().search([('product_id.product_tmpl_id', '=', data_product), ('date', '<=', date_filter),('state','=','done')],order="id asc")
                stcok_flow_in_out =  self.env['stock.move.line'].sudo().search([('product_id.product_tmpl_id', '=', data_product), ('date', '>=', first_date),('date', '<=', last_date),('state','=','done')],order="id asc")

                # SALDO AWAL
                if stock_flow_awal:
                    for stock_flow_saldo_awal in stock_flow_awal:
                        print(stock_flow_saldo_awal)
                        if stock_flow_saldo_awal.picking_code == 'incoming':
                            saldo_awal = saldo_awal + stock_flow_saldo_awal.qty_done

                        if stock_flow_saldo_awal.picking_code == 'outgoing':
                            saldo_awal = saldo_awal - stock_flow_saldo_awal.qty_done

                        nilai_awal = nilai_awal + (stock_flow_saldo_awal.move_id.price_unit * saldo_awal)
                        if nilai_awal > 0:
                            harga_satuan_awal = harga_satuan_awal + (nilai_awal/saldo_awal)

                create_pivot_line_saldo_awal = self.env['report.pivot.stock.saldo.awal'].create({
                    'product_tmpl_id': data_product,
                    'qty': saldo_awal,
                    'nilai': nilai_awal,
                    'harga_satuan': harga_satuan_awal,
                })
                print(create_pivot_line_saldo_awal)

                create_pivot_line = self.env['report.pivot.stock'].create({
                    'product_tmpl_id': data_product,
                    'saldo_awal': create_pivot_line_saldo_awal.id,
                    'notes_date': date_filter,
                    'qty':saldo_awal,
                    'harga_satuan':harga_satuan_awal,
                    'nilai':nilai_awal,
                    'saldo':'a. Saldo Awal'
                })
                pivot_stock_move_line.append(create_pivot_line.id)

                # SALDO ADJUSTEMNT
                if stock_flow_awal:
                    for stock_flow_saldo_adjustment in stock_flow_awal:
                        if 'Update' in stock_flow_saldo_adjustment.reference:
                            saldo_adjustment = saldo_adjustment + stock_flow_saldo_adjustment.qty_done

                        nilai_adjustment = nilai_adjustment + (stock_flow_saldo_adjustment.move_id.price_unit * saldo_adjustment)
                        if nilai_adjustment > 0:
                            harga_satuan_adjustment = harga_satuan_adjustment + (nilai_adjustment / saldo_adjustment)

                create_pivot_line_saldo_adjustment = self.env['report.pivot.stock.saldo.adjustment'].create({
                    'product_tmpl_id': data_product,
                    'qty': saldo_adjustment,
                    'nilai': nilai_adjustment,
                    'harga_satuan': harga_satuan_adjustment,
                })

                create_pivot_line = self.env['report.pivot.stock'].create({
                    'product_tmpl_id': data_product,
                    'saldo_adjustment': create_pivot_line_saldo_adjustment.id,
                    'notes_date': date_filter,
                    'qty': saldo_adjustment,
                    'harga_satuan': harga_satuan_adjustment,
                    'nilai': nilai_adjustment,
                    'saldo': 'd. Saldo Adjustment'
                })
                pivot_stock_move_line.append(create_pivot_line.id)

                #SALDO AKHIR
                if stock_flow_akhir:
                    for stock_flow_saldo_akhir in stock_flow_akhir:
                        if stock_flow_saldo_akhir.picking_code == 'incoming':
                            saldo_akhir = saldo_akhir + stock_flow_saldo_akhir.qty_done

                        if stock_flow_saldo_akhir.picking_code == 'outgoing':
                            saldo_akhir = saldo_akhir - stock_flow_saldo_akhir.qty_done

                        nilai_akhir = nilai_akhir + (stock_flow_saldo_akhir.move_id.price_unit * saldo_akhir)
                        if nilai_akhir > 0:
                            harga_satuan_akhir = harga_satuan_akhir + (nilai_akhir / saldo_akhir)

                create_pivot_line_saldo_akhir = self.env['report.pivot.stock.saldo.akhir'].create({
                    'product_tmpl_id': data_product,
                    'qty': saldo_akhir,
                    'nilai': nilai_akhir,
                    'harga_satuan': harga_satuan_akhir,
                })

                create_pivot_line = self.env['report.pivot.stock'].create({
                    'product_tmpl_id': data_product,
                    'saldo_akhir': create_pivot_line_saldo_akhir.id,
                    'notes_date': date_filter,
                    'qty': saldo_akhir,
                    'harga_satuan': harga_satuan_akhir,
                    'nilai': nilai_akhir,
                    'saldo': 'e. Saldo Akhir'
                })
                pivot_stock_move_line.append(create_pivot_line.id)

                # SALDO IN OUT
                if stcok_flow_in_out:
                    for stock_flow_saldo_in_out in stcok_flow_in_out:
                        if stock_flow_saldo_in_out.picking_code == 'incoming':
                            saldo_in = saldo_in + stock_flow_saldo_in_out.qty_done
                            nilai_in = nilai_in + (stock_flow_saldo_in_out.move_id.price_unit * saldo_in)
                            harga_satuan_in = harga_satuan_in + (nilai_in / saldo_in)


                        if stock_flow_saldo_in_out.picking_code == 'outgoing':
                            saldo_out = saldo_out + stock_flow_saldo_in_out.qty_done
                            nilai_out = nilai_out + stock_flow_saldo_in_out.move_id.price_unit
                            harga_satuan_out = harga_satuan_out + (nilai_out/saldo_out)

                create_pivot_line_saldo_in = self.env['report.pivot.stock.saldo.in'].create({
                    'product_tmpl_id': data_product,
                    'qty': saldo_in,
                    'nilai': nilai_in,
                    'harga_satuan': harga_satuan_in,
                })

                create_pivot_line = self.env['report.pivot.stock'].create({
                    'product_tmpl_id': data_product,
                    'saldo_in': create_pivot_line_saldo_in.id,
                    'notes_date': date_filter,
                    'qty': saldo_in,
                    'harga_satuan': harga_satuan_in,
                    'nilai': nilai_in,
                    'saldo': 'b. Saldo In'
                })
                pivot_stock_move_line.append(create_pivot_line.id)

                create_pivot_line_saldo_out = self.env['report.pivot.stock.saldo.out'].create({
                    'product_tmpl_id': data_product,
                    'qty': saldo_out,
                    'nilai': nilai_out,
                    'harga_satuan': harga_satuan_out,
                })

                create_pivot_line = self.env['report.pivot.stock'].create({
                    'product_tmpl_id': data_product,
                    'saldo_out': create_pivot_line_saldo_out.id,
                    'notes_date': date_filter,
                    'qty': saldo_out,
                    'harga_satuan': harga_satuan_out,
                    'nilai': nilai_out,
                    'saldo': 'c. Saldo Out'
                })

                pivot_stock_move_line.append(create_pivot_line.id)



        print(pivot_stock_move_line)

        # condition = [('id','in',pivot_stock_move_line)]
        condition = [('notes_date', '=', value)]
        print(condition)
        query = self.env['report.pivot.stock']._search(condition)
        print(query)
        return [('id', 'in', query)]

    def validate(self, value):
        try:
            date = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return date
        except:
            date = datetime.strptime(value, '%Y-%m-%d')
            return date

class additional_field_pivot_stock_saldo_awal(models.TransientModel):
    _name = "report.pivot.stock.saldo.awal"
    _description = "Pivot Stock For Saldo Awal WMU"

    name = fields.Char('Saldo Awal', default='Saldo Awal')
    product_tmpl_id = fields.Many2one('product.template')
    qty = fields.Float()
    nilai = fields.Float()
    harga_satuan = fields.Float()


class additional_field_pivot_stock_saldo_akhir(models.TransientModel):
    _name = "report.pivot.stock.saldo.akhir"
    _description = "Pivot Stock For Saldo Akhir WMU"

    name = fields.Char('Saldo Akhir', default='Saldo Akhir')
    product_tmpl_id = fields.Many2one('product.template')
    qty = fields.Float()
    nilai = fields.Float()
    harga_satuan = fields.Float()


class additional_field_pivot_stock_saldo_in(models.TransientModel):
    _name = "report.pivot.stock.saldo.in"
    _description = "Pivot Stock For Saldo In WMU"

    name = fields.Char('Saldo In', default="Saldo In")
    product_tmpl_id = fields.Many2one('product.template')
    qty = fields.Float()
    nilai = fields.Float()
    harga_satuan = fields.Float()


class additional_field_pivot_stock_saldo_out(models.TransientModel):
    _name = "report.pivot.stock.saldo.out"
    _description = "Pivot Stock For Saldo Out WMU"

    name = fields.Char('Saldo Out', default="Saldo Out")
    product_tmpl_id = fields.Many2one('product.template')
    qty = fields.Float()
    nilai = fields.Float()
    harga_satuan = fields.Float()


class additional_field_pivot_stock_saldo_adjustment(models.TransientModel):
    _name = "report.pivot.stock.saldo.adjustment"
    _description = "Pivot Stock For Saldo Adjustment WMU"

    name = fields.Char('Saldo Adjustment', default="Saldo Adjustment")
    product_tmpl_id = fields.Many2one('product.template')
    qty = fields.Float()
    nilai = fields.Float()
    harga_satuan = fields.Float()