# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    split_method = fields.Selection([('by_ratio', 'By Ratio'), ('by_quantity', 'By Quantity')], string='Split Method', compute='_compute_split_method', store=True)

    @api.depends('product_id')
    def _compute_split_method(self):
        for rec in self:
            if rec.product_id:
                category = self.env['product.category'].search(['|', '|', ('name', 'ilike', 'LIVE BIRD'), ('name', 'ilike', 'POULTRY'), ('name', 'ilike', 'IOT')])
                subcategory = self.env['product.category'].search([('id', 'child_of', category.ids)])
                if rec.product_id.categ_id.id in category.ids or rec.product_id.categ_id.id in subcategory.ids:
                    rec.split_method = 'by_ratio'
                else:
                    rec.split_method = 'by_quantity'
            else:
                rec.split_method = False


class MrpBomByProduct(models.Model):
    _inherit = 'mrp.bom.byproduct'

    ratio = fields.Float(string='Ratio')
    is_fix_cost = fields.Boolean(string='Is Fix Cost')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(comodel_name="res.currency", related="company_id.currency_id", string="Company Currency", readonly=True)
    fix_cost = fields.Monetary(string='Fix Cost', currency_field="company_currency_id")


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    is_special_bom = fields.Boolean(string="Special BOM")