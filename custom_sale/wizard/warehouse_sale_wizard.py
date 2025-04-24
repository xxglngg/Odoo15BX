# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class WarehouseSaleWizard(models.TransientModel):
    _name = 'warehouse.sale.wizard'
    _description = 'Wizard Sale Warehouse'

    message = fields.Text(string="Message")

    def button_confirm(self):
        active_id = self.env.context.get('active_id')
        sale = self.env['sale.order'].browse(active_id)
        if sale:
            sale.with_context(skip_procurement=True).action_confirm()
