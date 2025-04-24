# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields , api


class ShStockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def __getSecondQty(self):
        for rec in self:
            if rec.sh_sec_qty:
                str_value = str(rec.sh_sec_qty)
            else:
                str_value = ""
            rec.sh_sec_qty_computed = str_value

    sh_sec_qty = fields.Float("Secondary Qty", digits='Product Unit of Measure')
    sh_sec_uom = fields.Many2one("uom.uom", 'Secondary UOM', related="move_id.sh_sec_uom")
    sh_is_secondary_unit = fields.Boolean("Related Sec Unit", related="move_id.product_id.sh_is_secondary_unit")

    ### 220922 add by tio computed field for sh_sec_qty ##
    sh_sec_qty_computed = fields.Char(string='Secondary Qty', compute=__getSecondQty)

    @api.onchange('qty_done')
    def onchange_product_uom_done_qty_sh_move_line(self):
        ## 220922 add by tio not compute when uom Kg uom 2 Pcs ##
        if self.product_uom.name == 'Kg' and self.sh_sec_uom.name == 'Pcs':
            return {}
        else:
            if self and self.sh_is_secondary_unit and self.sh_sec_uom:
                self.sh_sec_qty = self.product_uom_id._compute_quantity(
                    self.qty_done, self.sh_sec_uom
                )

    @api.onchange('sh_sec_qty')
    def onchange_product_sec_done_qty_sh_move_line(self):
        ## 220922 add by tio not compute when uom Kg uom 2 Pcs ##
        if self.product_uom.name == 'Kg' and self.sh_sec_uom.name == 'Pcs':
            #### recalculate sh_sec_done_qty ###
            self.move_id.recalculate_total_sh_sec_done_qty(self._origin.id, self.sh_sec_qty)
            return {}
        else:
            if self and self.sh_is_secondary_unit and self.sh_sec_uom:
                self.qty_done = self.sh_sec_uom._compute_quantity(
                    self.sh_sec_qty, self.product_uom_id
                )

    def _get_aggregated_product_quantities(self, **kwargs):
        """ Returns a dictionary of products (key = id+name+description+uom) and corresponding values of interest.

        Allows aggregation of data across separate move lines for the same product. This is expected to be useful
        in things such as delivery reports. Dict key is made as a combination of values we expect to want to group
        the products by (i.e. so data is not lost). This function purposely ignores lots/SNs because these are
        expected to already be properly grouped by line.

        returns: dictionary {product_id+name+description+uom: {product, name, description, qty_done, product_uom}, ...}
        """
        aggregated_move_lines = {}
        for move_line in self:
            name = move_line.product_id.display_name
            description = move_line.move_id.description_picking
            if description == name or description == move_line.product_id.name:
                description = False
            uom = move_line.product_uom_id
            line_key = str(move_line.product_id.id) + "_" + name + (description or "") + "uom " + str(uom.id)

            if line_key not in aggregated_move_lines:
                aggregated_move_lines[line_key] = {'name': name,
                                                   'description': description,
                                                   'qty_done': move_line.qty_done,
                                                   'product_uom': uom.name,
                                                   'product': move_line.product_id,
                                                   'sh_sec_qty':move_line.move_id.sh_sec_done_qty,
                                                   'sh_sec_uom':move_line.move_id.sh_sec_uom.name,
                                                   }
            else:
                aggregated_move_lines[line_key]['qty_done'] += move_line.qty_done
        return aggregated_move_lines
