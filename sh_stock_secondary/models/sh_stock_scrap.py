# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class ShStockScrap(models.Model):
    _inherit = 'stock.scrap'

    def __getSecondQty(self):
        for rec in self:
            if rec.sh_sec_qty:
                str_value = str(rec.sh_sec_qty)
            else:
                str_value = ""
            rec.sh_sec_qty_computed = str_value

    sh_sec_qty = fields.Float(
        "Secondary Qty",
        digits='Product Unit of Measure'
    )
    sh_sec_uom = fields.Many2one("uom.uom", 'Secondary UOM')
    sh_is_secondary_unit = fields.Boolean(
        'Related sec. unit',
        related='product_id.sh_is_secondary_unit'
    )
    category_id = fields.Many2one(
        "uom.category",
        "UOM Category",
        related="product_uom_id.category_id"
    )

    ### 220922 add by tio computed field for sh_sec_qty ##
    sh_sec_qty_computed = fields.Char(string='Secondary Qty', compute=__getSecondQty)

    @api.model
    def create(self, vals):
        res = super(ShStockScrap, self).create(vals)
        res.sh_sec_qty = res.product_uom_id._compute_quantity(
            res.scrap_qty, res.product_id.sh_secondary_uom
        )
        res.sh_sec_uom = res.product_id.sh_secondary_uom.id
        return res

    @api.onchange('scrap_qty', 'product_uom_id')
    def onchange_product_uom_qty_sh(self):
        ## 220922 add by tio not compute when uom Kg uom 2 Pcs ##
        if self.product_uom.name == 'Kg' and self.sh_sec_uom.name == 'Pcs':
            return {}
        else:
            if self and self.sh_is_secondary_unit and self.sh_sec_uom:
                self.sh_sec_qty = self.product_uom_id._compute_quantity(
                    self.scrap_qty, self.sh_sec_uom
                )

    @api.onchange('sh_sec_qty', 'sh_sec_uom')
    def onchange_sh_sec_qty_sh(self):
        ## 220922 add by tio not compute when uom Kg uom 2 Pcs ##
        if self.product_uom.name == 'Kg' and self.sh_sec_uom.name == 'Pcs':
            return {}
        else:
            if self and self.sh_is_secondary_unit and self.product_uom_id:
                self.scrap_qty = self.sh_sec_uom._compute_quantity(
                    self.sh_sec_qty, self.product_uom_id
                )

    @api.onchange('product_id')
    def onchange_secondary_uom(self):
        if self:
            for rec in self:
                if rec.product_id.sh_is_secondary_unit and rec.product_id.uom_id:
                    rec.sh_sec_uom = rec.product_id.sh_secondary_uom.id
                else:
                    rec.sh_sec_uom = False
