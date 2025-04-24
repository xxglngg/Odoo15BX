# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockManifest(models.Model):
    _name = 'stock.manifest'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def name_get(self):
        res = []
        for manifest in self:
            if manifest.driver and manifest.nopol:
                res.append((manifest.id, '%s [%s]' % (manifest.driver, manifest.nopol)))
        return res

    tanggal = fields.Date(string='Date', required=True)
    nopol = fields.Char(string='Nopol', required=True)
    driver = fields.Char(string='Driver', required=True)
    note = fields.Text(string='Note')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    stock_picking_ids = fields.Many2many(comodel_name='stock.picking', relation='stock_manifest_to_stock_picking_rel',
                                         copy=False, string='Pickings')
    stock_manifest_line_ids = fields.One2many(comodel_name='stock.manifest.line', inverse_name='manifest_id',
                                              copy=False, string='Manifest Lines')

    @api.onchange('stock_picking_ids')
    def onchange_stock_picking_ids(self):
        for rec in self:
            rec.stock_manifest_line_ids = False
            vals_stock_picking = []
            for line in rec.stock_picking_ids:
                for move_line in line.move_line_ids_without_package:
                    vals_stock_picking.append((0, 0, {
                        'sequence': line.sequence,
                        'picking_id': line._origin.id,
                        'partner_id': line.partner_id.id,
                        'address': line.address,
                        'mobile': line.mobile,
                        'sku': move_line.product_id.default_code,
                        'product_id': move_line.product_id.id,
                        'product_qty': move_line.qty_done,
                        'product_uom_id': move_line.product_uom_id.id,
                    }))
            rec.stock_manifest_line_ids = vals_stock_picking


class StockManifestLine(models.Model):
    _name = 'stock.manifest.line'
    _order = 'sequence asc'
    _rec_name = 'product_id'

    manifest_id = fields.Many2one(comodel_name='stock.manifest', string='Manifest')
    sequence = fields.Integer(string='Delivery Order')
    picking_id = fields.Many2one(comodel_name='stock.picking', string='Picking')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer')
    address = fields.Text(string='Address')
    mobile = fields.Char(string='Phone Number')
    sku = fields.Char(string='SKU', related='product_id.default_code')
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    product_qty = fields.Float(string='Qty')
    product_uom_id = fields.Many2one(comodel_name='uom.uom', related='product_id.uom_id', string='UOM')
