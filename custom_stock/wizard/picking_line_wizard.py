# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from io import BytesIO
import xlrd
import base64
import datetime
import json

logger = logging.getLogger(__file__)


class PickingLineWizard(models.TransientModel):
    _name = 'picking.line.wizard'

    picking_id = fields.Many2one('stock.picking', string='Picking ID')
    product_id = fields.Many2one(comodel_name='product.product', string='Product ID',)
    product_tmpl_id = fields.Many2one(comodel_name='product.template', related="product_id.product_tmpl_id")
    product_categ_id = fields.Many2one(comodel_name='product.category')
    product_qty = fields.Float('Quantity')
    uom_id = fields.Many2one('uom.uom', related="product_id.uom_id")
    quant_qty = fields.Float("Stock Qty")
    qty_available = fields.Float(related="product_id.qty_available")
    standard_price = fields.Float(related="product_id.standard_price")
    lst_price = fields.Float(related="product_id.lst_price")
    location_id = fields.Many2one('stock.location', string='Location')
    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial Number')
    id_inventory = fields.Char(string="ID Inventory",)

    location_domain = fields.Char(
       compute="_compute_location_domain",
       readonly=True,
       store=False,)
    
    lot_domain = fields.Char(
       compute="_compute_lot_domain",
       readonly=True,
       store=False,)

    @api.depends('product_id','lot_id')
    def _compute_location_domain(self):
        for rec in self:
            domain = []
            location_ids = []
            if rec.product_id:
                if rec.lot_id:
                    quant_ids = self.env['stock.quant'].search([('product_id','=',rec.product_id.id),('lot_id','=',rec.lot_id.id)])
                else:
                    quant_ids = self.env['stock.quant'].search([('product_id','=',rec.product_id.id)])
                for quant in quant_ids:
                    if quant.location_id.id not in location_ids:
                        location_ids.append(quant.location_id.id)
                domain = [('id', 'in', location_ids)]
            else:
                domain = [('usage', 'in', ['internal', 'transit'])]
            rec.location_domain = json.dumps(domain)
    
    @api.depends('product_id','location_id')
    def _compute_lot_domain(self):
        for rec in self:
            domain = []
            lot_ids = []
            quant_domain = []
            if rec.product_id:
                if rec.location_id:
                    quant_ids = self.env['stock.quant'].search([('product_id','=',rec.product_id.id),('location_id','=',rec.location_id.id)])
                else:
                    quant_ids = self.env['stock.quant'].search([('product_id','=',rec.product_id.id)])
                for quant in quant_ids:
                    if quant.lot_id.id not in lot_ids:
                        lot_ids.append(quant.lot_id.id)
                domain = [('id', 'in', lot_ids)]
            else:
                domain = []
            rec.lot_domain = json.dumps(domain)


    # @api.model
    # def default_get(self, fields):
    #     res = super(PickingLineWizard, self).default_get(fields)
    #     if 'request_id' in fields and not res.get('request_id') and self._context.get('active_model') == 'product.creation.request' and self._context.get('active_id'):
    #         res['request_id'] = self._context['active_id']
    #     return res

    def action_add_product(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['picking.line.wizard'].browse(selected_ids)
        print("selected_records", selected_records)
        move_obj = self.env['stock.move']
        detail_lines = []
        product_selected = []
        move_ids = []
        for data in selected_records:
            if data.product_qty:
                move_line_vals = {
                    'picking_id': data.picking_id.id,
                    'product_id': data.product_id.id,
                    # 'name': data.product_id.name,
                    # 'product_qty':data.product_qty,
                    'product_uom_qty':data.product_qty,
                    'qty_done':data.product_qty,
                    'product_uom_id':data.product_id.uom_id.id,
                    'location_id':data.location_id.id,
                    'location_dest_id':data.picking_id.location_dest_id.id,
                    'lot_id':data.lot_id.id if data.lot_id else False,
                    'id_inventory':data.id_inventory if data.id_inventory else '',
                }
                detail_lines.append(move_line_vals)

                if data.product_id.id not in product_selected:
                    product_selected.append(data.product_id.id)
                    move_vals = {
                        'picking_id': data.picking_id.id,
                        'product_id': data.product_id.id,
                        'name': data.product_id.name,
                        # 'product_qty':data.product_qty,
                        # 'product_uom_qty':data.product_qty,
                        'product_uom':data.product_id.uom_id.id,
                        'location_id':data.location_id.id,
                        'location_dest_id':data.picking_id.location_dest_id.id,
                    }
                    move_ids.append(move_vals)

        if detail_lines and move_ids:
            for move in move_ids:
                move_line = []
                qty = 0
                for line in detail_lines:
                    if move['product_id'] == line['product_id']:
                        qty += line['qty_done']
                        move_line.append([0,0,line])
                move['move_line_ids'] = move_line
                move['product_uom_qty'] = qty
                print("move#######################", move)
                move_id = move_obj.create(move)
        return True