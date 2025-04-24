from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    kilograms = fields.Float(string="Kg", compute= '_compute_kg_pcs_abw_pckg')
    pieces = fields.Float(string="Pcs", compute= '_compute_kg_pcs_abw_pckg')
    pckg_qty = fields.Float(string="Packaging Quantity", compute= '_compute_kg_pcs_abw_pckg')

    def _compute_kg_pcs_abw_pckg(self):
        for amove in self:
            if amove.product_uom_id.name == 'Kg':
                amove.kilograms = amove.qty_done
            elif amove.sh_sec_uom.name == 'Kg':
                amove.kilograms = amove.sh_sec_qty
            else :
                amove.kilograms = False
            if amove.product_uom_id.name == 'Pcs':
                amove.pieces = amove.qty_done
            elif amove.sh_sec_uom.name == 'Pcs':
                amove.pieces = amove.sh_sec_qty
            else :
                amove.pieces = False
            if amove.kilograms and amove.move_id.packaging_qty_line and amove.move_id.kilograms:
                amove.pckg_qty = amove.move_id.packaging_qty_line / amove.move_id.kilograms * amove.kilograms
            else:
                amove.pckg_qty = False
