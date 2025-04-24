from odoo import api, models


class StockPicking(models.Model):
    """Extends stock picking to apply domain restrictions based on user's
    assigned warehouses."""
    _inherit = 'stock.picking'

    @api.onchange('location_id', 'location_dest_id')
    def _onchange_location_id(self):
        """Domain for location_id and location_dest_id."""
        return {
            'domain': {'location_id': [
                ('warehouse_id', 'in', self.env.user.allowed_warehouse_ids.ids)],
                'location_dest_id': [
                    ('warehouse_id', 'in', self.env.user.allowed_warehouse_ids.ids)]}}
