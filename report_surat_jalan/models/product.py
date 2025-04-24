from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    def __getUOM(self):
        for rec in self:
            if rec.secondary_uom_as_ref and rec.product_id.sh_secondary_uom:
                rec.product_uom_id = rec.product_id.sh_secondary_uom.id
            else:
                rec.product_uom_id = rec.product_id.uom_id.id

    product_uom_id = fields.Many2one('uom.uom', compute=__getUOM, related="", readonly=False)
    secondary_uom_as_ref = fields.Boolean(string='2nd UOM as Ref',default=False,)
    product_uom_name = fields.Char(related="product_uom_id.name", readonly=True)

    @api.onchange("secondary_uom_as_ref")
    def _onchange_secondary_uom_as_ref(self):
        for rec in self:
            if rec.secondary_uom_as_ref and rec.product_id.sh_secondary_uom:
                rec.product_uom_id = rec.product_id.sh_secondary_uom.id
            else:
                rec.product_uom_id = rec.product_id.uom_id.id


