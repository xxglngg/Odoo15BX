from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _get_bag_qty(self):
        for rec in self:
            rec.bag_qty = 0
            # if rec.move_line_ids:
            qty = 0
            for line in rec.move_line_ids:
                qty += line.bag_qty
            rec.bag_qty = qty

    # def __get_bag_qty(self):
    #     for rec in self:
    #         rec.bag_qty = 0
    #         qty = 0
    #         if rec.product_id.pcs_per_bag_ratio: 
    #             if rec.sh_sec_qty and rec.sh_sec_uom.name == 'Pcs':
    #                 qty = rec.sh_sec_qty/rec.product_id.pcs_per_bag_ratio
    #             else:
    #                 qty = rec.quantity_done/rec.product_id.pcs_per_bag_ratio
    #         rec.bag_qty = qty

    bag_qty = fields.Float(string="Total Bag", compute=_get_bag_qty)
    total_karung = fields.Integer(string="Total Karung")
    potong_karung = fields.Float(string="Total Potong Karung", compute="_depends_potong_karung")
    profit_weight = fields.Float(string="Total Netto", compute="_depends_profit_weight")
    is_profit_weight = fields.Boolean(string="Is Netto", default=False)
    gross_weight = fields.Float(string="Total Brutto", compute="_depends_gross_weight")
    is_gross_weight = fields.Boolean(string="Is Brutto", default=False)
    susut = fields.Float(string="Susut")
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
            rec.profit_weight = rec.quantity_done
            if rec.quantity_done:
                rec.profit_weight = rec.quantity_done - rec.potong_karung
    
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
            rec.gross_weight = rec.quantity_done
            if rec.quantity_done:
                rec.gross_weight = rec.quantity_done + rec.potong_karung
    
    # @api.depends('is_gross_weight')
    # def _depends_is_gross_weight(self):
    #     for rec in self:
    #         if rec.picking_id.netto_brutto == 'brutto':
    #             rec.is_gross_weight = True
    #         else:
    #             rec.is_gross_weight = False
    
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