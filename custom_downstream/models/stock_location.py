from odoo import fields, models, api
from odoo.tools.float_utils import float_compare


class Location(models.Model):
    _inherit = "stock.location"

    def _check_can_be_used(self, product, quantity=0, package=None, location_qty=0):
        """Check if product/package can be stored in the location. Quantity
        should in the default uom of product, it's only used when no package is
        specified."""
        self.ensure_one()
        if self.storage_category_id:
            # check if enough space
            if package and package.package_type_id:
                # check weight
                package_smls = self.env['stock.move.line'].search([('result_package_id', '=', package.id)])
                if self.storage_category_id.max_weight < self.forecast_weight + sum(package_smls.mapped(lambda sml: sml.product_qty * sml.product_id.weight)):
                    return False
                # check if enough space
                package_capacity = self.storage_category_id.package_capacity_ids.filtered(lambda pc: pc.package_type_id == package.package_type_id)
                if package_capacity and location_qty >= package_capacity.quantity:
                    return False
            else:
                # check weight
                if self.storage_category_id.max_weight < self.forecast_weight + product.weight * quantity:
                    return False
                product_capacity = self.storage_category_id.product_capacity_ids.filtered(lambda pc: pc.product_id == product)
                # To handle new line without quantity in order to avoid suggesting a location already full
                if product_capacity and location_qty >= product_capacity.quantity:
                    return False
                if product_capacity and quantity + location_qty > product_capacity.quantity:
                    return False
            positive_quant = self.quant_ids.filtered(lambda q: float_compare(q.quantity, 0, precision_rounding=q.product_id.uom_id.rounding) > 0)
            # check if only allow new product when empty
            if self.storage_category_id.allow_new_product == "empty" and positive_quant:
                return False
            # check if only allow same product
            if self.storage_category_id.allow_new_product == "same" and positive_quant and positive_quant.product_id != product:
                return False
            if self.storage_category_id.allow_new_product == "two_products" and positive_quant and len(positive_quant) >= 2:
                if product not in positive_quant.product_id:
                    return False
        return True
