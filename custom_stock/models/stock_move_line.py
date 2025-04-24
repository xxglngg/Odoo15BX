# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
import json


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # @api.model
    # def __getDomainLot(self):
    #     domain = []
    #     list_id = []
    #     lot_ids = []
    #     quant_domain = []
    #     print (self.product_id, self.location_id)
    #     if self.product_id:
    #         quant_domain = [
    #             ('product_id', '=', self.product_id.id),
    #             ('lot_id', '!=', False),
    #             ('location_id.usage', '=', 'internal')
    #         ]
        
    #     if self.location_id:
    #         quant_domain = expression.AND([quant_domain, [
    #             '|',
    #             ('location_id', '=', self.location_id.id),
    #             ('location_id', 'child_of', self.location_id.id)
    #         ]])
        
    #         quant_ids = self.env['stock.quant'].search(quant_domain)
    #         print("sdfsdf", quant_ids)
    #         lot_ids = [data.lot_id.id for data in quant_ids]
        
    #     print(quant_domain, "sdfsdf")
    #     print(lot_ids)

    #     domain = [('id', 'in', lot_ids)]
    #     return domain

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     domain = {}
    #     default_domain_lot = self.__getDomainLot()
    #     domain['lot_id'] = default_domain_lot
    #     return {'domain': domain,}
    
    # lot_id = fields.Many2one(
    #     'stock.production.lot', 'Lot/Serial Number',
    #     domain=__getDomainLot, check_company=True)

    lot_id_domain = fields.Char(
       compute="_compute_lot_id_domain",
       readonly=True,
       store=False,)
    id_inventory = fields.Char(string="ID Inventory",)
    total_karung = fields.Integer(string="Total Karung", related='move_id.total_karung')
    potong_karung = fields.Float(string="Total Potong Karung", compute="_depends_potong_karung")
    profit_weight = fields.Float(string="Total Netto", compute="_depends_profit_weight")
    is_profit_weight = fields.Boolean(string="Is Netto", default=False)
    gross_weight = fields.Float(string="Total Brutto", compute="_depends_gross_weight")
    is_gross_weight = fields.Boolean(string="Is Brutto", default=False)
    susut = fields.Float(string="Susut", related='move_id.susut')
    total_berat = fields.Float(string="Total Berat")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', compute="_get_analytic_account")

    def _get_analytic_account(self):
        for rec in self:
            po_obj = rec.picking_id.purchase_id
            so_obj = rec.picking_id.sale_id
            if po_obj:
                rec.analytic_account_id = po_obj.analytic_account_id.id
            elif so_obj:
                rec.analytic_account_id = so_obj.analytic_account_id.id
            else:
                rec.analytic_account_id = None

    @api.depends('potong_karung')
    def _depends_potong_karung(self):
        total = 0
        for rec in self:
            total = rec.total_karung * rec.picking_id.berat_karung
            rec.potong_karung = total
    
    @api.depends('profit_weight')
    def _depends_profit_weight(self):
        for rec in self:
            rec.profit_weight = rec.qty_done
            if rec.qty_done:
                rec.profit_weight = rec.qty_done - rec.potong_karung
    
    # @api.depends('is_profit_weight')
    # def _depends_is_profit_weight(self):
    #     for rec in self:
    #         if rec.picking_id.netto_brutto == 'netto':
    #             rec.is_profit_weight = True
    #         else:
    #             rec.is_profit_weight = False
    
    @api.depends('gross_weight')
    def _depends_gross_weight(self):
        for rec in self:
            rec.gross_weight = rec.qty_done
            if rec.qty_done:
                rec.gross_weight = rec.qty_done + rec.potong_karung
    
    @api.depends('is_gross_weight')
    def _depends_is_gross_weight(self):
        for rec in self:
            if rec.picking_id.netto_brutto == 'brutto':
                rec.is_gross_weight = True
            else:
                rec.is_gross_weight = False
    
    # @api.depends('total_berat')
    # def _depends_total_berat(self):
    #     for rec in self:
    #         total = 0
    #         rec.total_berat = 0
    #         if rec.picking_id:
    #             if rec.picking_id.netto_brutto == 'netto':
    #                 total = rec.profit_weight - rec.susut
    #             rec.total_berat = total
    #             if rec.picking_id.netto_brutto == 'brutto':
    #                 total = rec.gross_weight - rec.potong_karung - rec.susut
    #             rec.total_berat = total


    @api.depends('product_id', 'location_id')
    def _compute_lot_id_domain(self):
        for rec in self:
            domain = []
            lot_ids = []
            quant_domain = []
            if rec.product_id:
                quant_domain = [
                    ('product_id', '=', rec.product_id.id),
                    ('lot_id', '!=', False),
                    ('location_id.usage', '=', 'internal')
                ]
            if rec.location_id:
                quant_domain = expression.AND([quant_domain, [
                    '|',
                    ('location_id', '=', rec.location_id.id),
                    ('location_id', 'child_of', rec.location_id.id)
                ]])
            
                quant_ids = self.env['stock.quant'].search(quant_domain)
                lot_ids = [data.lot_id.id for data in quant_ids]
            
            # print("quant_domain", quant_domain, lot_ids)
            domain = [('id', 'in', lot_ids)]
            rec.lot_id_domain = json.dumps(domain)

    