from odoo import models, fields, api
from odoo.exceptions import UserError

class InheritStockMove0223(models.Model):
    _inherit = 'stock.move'
    _description = 'Inherit Model Stock move'

    packaging_qty_line = fields.Float(
        string='Packaging QTY',
        readonly='False',
        help='Packaging Quantity, counted by Demand/Packaging value',
        compute= '_compute_packaging_qty_line',
        store=True
    )
    kilograms = fields.Float(string="Kg", compute= '_compute_kg_pcs_abw')
    pieces = fields.Float(string="Pcs", compute= '_compute_kg_pcs_abw')
    abw = fields.Float(string="ABW", compute='_compute_kg_pcs_abw')
    neto = fields.Float(string="Neto", compute='_compute_kg_pcs_abw')
    
    def _compute_kg_pcs_abw(self):
        for amove in self:
            if amove.product_uom.name == 'Kg':
                amove.kilograms = amove.quantity_done
            elif amove.sh_sec_uom.name == 'Kg':
                amove.kilograms = amove.sh_sec_done_qty_computed
            else :
                amove.kilograms = False
            if amove.product_uom.name == 'Pcs':
                amove.pieces = amove.quantity_done
            elif amove.sh_sec_uom.name == 'Pcs':
                amove.pieces = amove.sh_sec_done_qty_computed
            else :
                amove.pieces = False
            if amove.pieces == False or amove.kilograms == False:
                amove.abw = False
            else:
                amove.abw = amove.kilograms/amove.pieces
            if amove.kilograms:
                tmp_kg = amove.kilograms
            else:
                tmp_kg = 0 
            if amove.potong_karung:
                tmp_pk = amove.potong_karung
            else:
                tmp_pk = 0
            if amove.susut:
                tmp_susut = amove.susut
            else:
                tmp_susut = 0
            
            tmp_neto = tmp_kg - tmp_pk - tmp_susut
            if tmp_neto < 0.0:
                tmp_neto = 0.0
            amove.neto = tmp_neto
            
    @api.depends('product_packaging_id', 'quantity_done', 'sh_sec_done_qty', 'product_packaging_id.qty')
    def _compute_packaging_qty_line(self):
        for move in self:
            # raise UserError(str(self)+str(type(self)))
            if move.product_packaging_id and move.quantity_done and move.product_packaging_id.qty and not move.product_packaging_id.secondary_uom_as_ref:
                move.packaging_qty_line = float(move.quantity_done)/float(move.product_packaging_id.qty)
            elif move.product_packaging_id and move.sh_sec_done_qty and move.product_packaging_id.qty and move.product_packaging_id.secondary_uom_as_ref:
                move.packaging_qty_line = float(move.sh_sec_done_qty)/float(move.product_packaging_id.qty)
            else:
                move.packaging_qty_line = False

    @api.onchange("packaging_qty_line")
    def _onchange_packaging_qty_line(self):
        for move in self:
            if move.packaging_qty_line != 0 and move.product_packaging_id and move.product_packaging_id.qty:
                if not move.product_packaging_id.secondary_uom_as_ref:
                    move.quantity_done = float(move.packaging_qty_line)*float(move.product_packaging_id.qty)
                elif move.product_packaging_id.secondary_uom_as_ref:
                    move.sh_sec_done_qty = float(move.packaging_qty_line)*float(move.product_packaging_id.qty)
