# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        if self.purchase_id:
            self.origin = self.purchase_id.name
    
    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        if self.sale_id:
            self.origin = self.sale_id.name
    
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
        check_company=False, readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        check_company=False, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

    location_domain = fields.Char(
       compute="_compute_location_domain",
       readonly=True,
       store=False,)
    
    ### override field purchase_id make store=True ###
    purchase_id = fields.Many2one('purchase.order', related='move_lines.purchase_line_id.order_id', string="Purchase Orders", readonly=False, store=True)

    berat_karung = fields.Float(string="Berat Karung", required=True)
    # netto_brutto = fields.Selection([
    #     ('netto','Hitung by Netto'),
    #     ('brutto','Hitung by Brutto')], string="Hitung Netto/Brutto", required=True)

    upload_sj_ttb = fields.Binary(string="Upload SJ/TTB")
    file_sj_ttb = fields.Char(string="File SJ/TTB")

    def action_view_upload_sj_ttb(self):
        if self.file_sj_ttb.endswith('.png') or self.file_sj_ttb.endswith('.jpg') or self.file_sj_ttb.endswith('.jpeg'):
            id = self.id

            context = {
                'default_id': id,
                'default_upload_sj_ttb': self.upload_sj_ttb,
            }

            compose_form = self.env.ref(
                'custom_stock.wizard_view_image_sj_ttb'
            )
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': context,
                'nodestroy': True,
                'target': 'new',
                'res_id':id,
            }
        
        if self.file_sj_ttb.endswith('.pdf'):
            id = self.id

            context = {
                'default_id': id,
                'default_upload_sj_ttb': self.upload_sj_ttb,
            }

            compose_form = self.env.ref(
                'custom_stock.wizard_view_pdf_sj_ttb'
            )

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': context,
                'nodestroy': True,
                'target': 'new',
                'res_id':id,
            }

    @api.depends('picking_type_id')
    def _compute_location_domain(self):
        for rec in self:
            domain = []
            lot_ids = []
            quant_domain = []
            if rec.picking_type_id and rec.picking_type_id.multi_location:
                # print("quant_domain")
                domain = [('usage', 'in', ['view'])]
            rec.location_domain = json.dumps(domain)
    
    def open_wizard(self):
        # if context is None:
        context = {}
        # if not ids:
        #     return False
        # if not isinstance(ids, list):
        #     ids = [ids]
        wizard_ids = []
        wizard_exist = self.env['picking.line.wizard'].search([('picking_id','=',self.id)])
        
        if wizard_exist:
            wizard_ids = wizard_exist.ids
        else:
            company_product_rel_ids = self.env['company.product.rel'].search([('company_ids','in',self.company_id.ids)])
            allowed_product_categ_ids = company_product_rel_ids.mapped('product_categ_ids')
            # print(company_product_rel_ids, allowed_product_categ_ids)
            if allowed_product_categ_ids:
                product_template_ids = self.env['product.template'].search([('categ_id','in',allowed_product_categ_ids.ids),])
                if product_template_ids:
                    products = self.env['product.product'].search([('active','=',True),('product_tmpl_id','in',product_template_ids.ids)])
                else:
                    products = self.env['product.product'].search([('active','=',True),])
            else:
                products = self.env['product.product'].search([('active','=',True),])
            internal_location_ids = self.env['stock.location'].search([('usage','in',['internal','transit'])])
            ids = products
            print("ids",ids)
            vals = {}
            # for product_id in ids:
            print("ids",products, internal_location_ids.ids)
            quant_ids = self.env['stock.quant'].search([('product_id','=',products.ids),('location_id','in',internal_location_ids.ids)])
            # quant_ids = self.env['stock.quant'].search([('product_id','=',products.ids)])
            # quant_ids = self.env['stock.quant'].search([],slimit=100)
            print(quant_ids)
            for quant in quant_ids:
            #     vals = {'picking_id':self.id, 
            #             'product_id': product_id, 
            #             'location_id':quant.location_id.id,
            #             'lot_id':quant.lot_id.id if quant.lot_id else False,
            #             }
                vals = {
                        'picking_id':self.id, 
                        'product_id': quant.product_id.id, 
                        'product_categ_id': quant.product_id.product_tmpl_id.categ_id.id,
                        'id_inventory': quant.id_inventory,
                        'location_id': quant.location_id.id,
                        'lot_id': quant.lot_id.id,
                        'quant_qty': quant.quantity,
                        }
                if vals:
                    wizard_id = self.env['picking.line.wizard'].create(vals)
                    wizard_ids.append(wizard_id.id)
                else:
                    return {}
        # print(len(wizard_ids))
        return {
            'name': 'Line Wizard',
            'view_mode': 'tree',
            'res_model': 'picking.line.wizard',
            'res_id': wizard_ids,
            'type': 'ir.actions.act_window',
            "search_view_id": [self.env.ref('custom_stock.view_picking_line_wizard_search').id, 'search'],
            'target': 'new',
            'domain': [('picking_id','=', self.id)],
            'context': context,
        }