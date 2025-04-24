from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def _get_has_create_vendor(self):
        return self.env.user.has_group('custom_restrict_fields.hide_vendor_create_user')
     
    def _get_has_create_customer(self):
        return self.env.user.has_group('custom_restrict_fields.hide_customer_create_user')
    
    has_group_create_vendor = fields.Boolean(default=_get_has_create_vendor)
    has_group_create_customer = fields.Boolean(default=_get_has_create_customer)
