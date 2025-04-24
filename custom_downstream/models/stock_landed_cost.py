from odoo import fields, models, api


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'


    mrp_production_ids = fields.Many2many(
        'mrp.production', string='Manufacturing order',
        copy=False, states={'done': [('readonly', True)]}, groups='stock.group_stock_manager,'
                                                                  'custom_downstream.group_broilerx_downstream')

    def button_validate(self):
        validate = super(StockLandedCost, self).button_validate()
        if validate:
            for cost in self:
                valuation_layers = self.env['stock.valuation.layer'].search([('stock_landed_cost_id', '=', cost.id)])
                for valuation_layer in valuation_layers:
                    linked_layer = valuation_layer.stock_valuation_layer_id
                    if linked_layer.lot_id:
                        valuation_layer.lot_id = linked_layer.lot_id
                        valuation_layer.lot_id.inventory_value += valuation_layer.value
                        valuation_layer.lot_id.unit_price = valuation_layer.lot_id.inventory_value / valuation_layer.lot_id.product_qty
        return validate
