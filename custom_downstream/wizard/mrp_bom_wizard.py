from odoo import models, fields, api, _


class MrpBomWizard(models.TransientModel):
    _name = 'mrp.bom.wizard'

    bom_id = fields.Many2one(comodel_name='mrp.bom', string='Bill of Material')
    bom_ids = fields.Many2many(comodel_name='product.product', string='Raw Material')

    def button_add_raw_material(self):
        line_vals = []
        for rec in self:
            for bom in rec.bom_ids.filtered(lambda x: x not in rec.bom_id.bom_line_ids.mapped('product_id')):
                line_vals.append((0, 0, {
                    'product_id': bom.id,
                    'product_uom_id': bom.uom_id.id,
                }))
            rec.bom_id.bom_line_ids = line_vals

class MrpBomWizardByProduct(models.TransientModel):
    _name = 'mrp.bom.byproduct.wizard'

    bom_id = fields.Many2one(comodel_name='mrp.bom', string='Bill of Material')
    bom_ids = fields.Many2many(comodel_name='product.product', string='Product Result line')

    def button_add_product_result(self):
        line_vals = []
        for rec in self:
            for bom in rec.bom_ids.filtered(lambda x: x not in rec.bom_id.bom_line_ids.mapped('product_id')):
                line_vals.append((0, 0, {
                    'product_id': bom.id,
                    'product_uom_id': bom.uom_id.id,
                }))
            rec.bom_id.byproduct_ids = line_vals
