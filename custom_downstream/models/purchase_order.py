# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def _check_uom_kg(self):
        for purchase in self:
            count_eror = 0
            for line in purchase.order_line:
                if line.product_id.product_type_stream == 'downstream' and line.product_uom.id != 12 and line.product_uom_secondary.id != 12:
                    count_eror +=1
                if line.product_id.product_type_stream == 'downstream' and line.product_uom_secondary.id == 12 and line.product_qty_secondary == 0:
                    count_eror +=1
            # raise ValidationError(_("Ada product yang uom nya tidak kg" ))
            if count_eror > 0:
                raise ValidationError(_("Ada product yang uom nya tidak kg" ))


    def button_approve(self):
        self._check_uom_kg()
        res = super(PurchaseOrder, self).button_approve()
        return res