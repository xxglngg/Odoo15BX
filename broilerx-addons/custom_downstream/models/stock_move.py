# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(comodel_name="res.currency", related="company_id.currency_id",
                                          string="Company Currency", readonly=True)
    material_cost = fields.Float(string='Material Cost')
    material_cost_by_quantity = fields.Float(string='Material Cost by Qty')
    subtotal_material = fields.Monetary(string='Subtotal Material', currency_field="company_currency_id", compute='compute_subtotal_material', store=True)
    is_fix_cost = fields.Boolean(string='Is Fix Cost')
    fix_cost_price = fields.Monetary(string='Fix Cost Price', currency_field="company_currency_id")
    ratio = fields.Float(string='Ratio')
    cost = fields.Monetary(string='Cost', currency_field="company_currency_id", compute='compute_cost', store=True)
    landed_cost = fields.Monetary(string='Landed Cost', currency_field="company_currency_id",store=True)
    # cost = fields.Float(string='Cost', compute='compute_cost', store=True)
    cost_share = fields.Float(
        "Cost Share (%)", digits=(5, 10),  # decimal = 10 is important for rounding calculations!!
        help="The percentage of the final production cost for this by-product. The total of all by-products' cost share must be smaller or equal to 100.",
        compute='compute_cost_share', store=True)
    production_state = fields.Selection(related="production_id.state")
    raw_material_production_state = fields.Selection(related="raw_material_production_id.state")
    show_lots_text = fields.Boolean(compute='_compute_show_lots_text', store=True)
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

    @api.depends('production_id')
    def _compute_show_lots_text(self):
        for move in self:
            if move.production_id.picking_type_id.use_create_components_lots:
                move.show_lots_text = True
            else:
                move.show_lots_text = False


    @api.depends('cost')
    def compute_cost_share(self):
        for rec in self:
            if rec.production_id and rec.production_id.material_cost:
                rec.cost_share = rec.cost / rec.production_id.material_cost * 100

    @api.depends('quantity_done', 'material_cost')
    def compute_subtotal_material(self):
        for rec in self:
            if rec.quantity_done and rec.material_cost:
                rec.subtotal_material = rec.quantity_done * rec.material_cost
            else:
                rec.subtotal_material = 0

            if rec.raw_material_production_id and rec.raw_material_production_id.state != 'draft':
                rec.raw_material_production_id.compute_material_cost()

            if rec.production_id and rec.production_id.state != 'draft':
                rec.production_id.compute_fix_cost()
                rec.production_id.compute_by_quantity()

    @api.depends('quantity_done', 'is_fix_cost', 'fix_cost_price')
    def compute_cost(self):
        for rec in self:
            if rec.is_fix_cost:
                rec.cost = rec.quantity_done * rec.fix_cost_price

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super(StockMove, self)._prepare_move_line_vals(quantity, reserved_quant)
        self.ensure_one()
        res.update({"qty_at_farm_kg": self.purchase_line_id.product_qty,
                    "qty_at_farm_ekor": self.purchase_line_id.product_qty_secondary})
        return res

    @api.onchange('material_cost','product_id','quantity_done')
    def onchange_quantity_done(self):
        if self.product_id and self.quantity_done:
            if self.product_id.categ_id.property_cost_method == 'average':
                self.material_cost = self.product_id.standard_price
                self.subtotal_material = self.quantity_done * self.material_cost
            else:
                self.subtotal_material = self.quantity_done * self.material_cost

    def action_show_details(self):
        """ Open the produce wizard in order to register tracked components for
        subcontracted product. Otherwise use standard behavior.
        """
        self.ensure_one()
        action = super(StockMove, self).action_show_details()
        if self.production_id and self.show_lots_text:
            action['context'].update({
                'show_lots_m2o': False,
                'show_lots_text': True,
            })
        return action


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    operation_type_code = fields.Selection(related='picking_type_id.code', string='Operation Type Code')
    qty_done_secondary = fields.Float(string='Done Secondary')
    qty_at_farm_ekor = fields.Integer(string='Qty At Farm (Ekor)')
    qty_at_farm_kg = fields.Float(string='Qty At Farm (Kg)')
    qty_deplesi_ekor = fields.Integer(string='Deplesi (Ekor)')
    qty_deplesi_kg = fields.Float(string='Deplesi (Kg)')
    weight_loss = fields.Float(string='Weight Loss', compute='_compute_weight_loss', store=True)

    def write(self, vals):
        res = super(StockMoveLine, self).write(vals)
        if vals.get('qty_at_farm_kg'):
            self.move_id.purchase_line_id.product_qty = vals.get('qty_at_farm_kg')
            if self.qty_done:
                self.move_id.price_unit = self.move_id.purchase_line_id.product_qty * self.move_id.purchase_line_id.price_unit / self.qty_done
        if self.move_id.raw_material_production_id:
            for rec in self:
                if rec.lot_id and rec.product_id.categ_id.property_cost_method == 'fifo':
                    rec.move_id.material_cost = rec.lot_id.unit_price
                else:
                    rec.move_id.material_cost = rec.product_id.standard_price
        for rec in self:
            if rec.qty_done:
                if rec.qty_done_secondary:
                    rec.move_id.quantity_done_secondary = rec.qty_done_secondary
        return res

    @api.depends('qty_at_farm_kg', 'qty_deplesi_kg', 'qty_done')
    def _compute_weight_loss(self):
        for rec in self:
            rec.weight_loss = rec.qty_at_farm_kg - rec.qty_deplesi_kg - rec.qty_done

    @api.model
    def create(self, vals):
        res = super(StockMoveLine, self).create(vals)
        # values = []
        # production_lot_obj = self.env["stock.production.lot"]
        # default_dict = res._prepare_auto_lot_values()
        # default_dict.update({"name": res.move_id.picking_id.name})
        # values.append(default_dict)
        # lot = production_lot_obj.create(values)

        if res.product_id.tracking == "lot" and res.product_id.auto_create_lot and res.picking_type_id.auto_create_lot:
            # res.lot_name = lot.name
            res.lot_name = res.move_id.picking_id.name
        if res.lot_id and res.product_id.categ_id.property_cost_method == 'fifo':
            res.move_id.material_cost = res.lot_id.unit_price
        else:
            res.move_id.material_cost = res.product_id.standard_price
        return res
