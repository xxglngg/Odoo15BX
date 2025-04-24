from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_company_pis = fields.Boolean('Is Company PIS', compute="_compute_is_company_pis")

    def _compute_is_company_pis(self):
        for rec in self:
            rec.is_company_pis = False
            if rec.company_id.name == 'PT Pangan Integrasi Sejahtera':
                rec.is_company_pis = True
