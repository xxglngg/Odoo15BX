from itertools import groupby

from num2words import num2words
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('amount_total')
    def _amount_to_text(self):
        for record in self:
            record.amount_text = ''
            if record.amount_total:
                value = round(record.amount_total)
                result = num2words(value, lang="id")
                if record.currency_id.name == 'IDR':
                    amount_txt = str(result.capitalize()).upper() + ' RUPIAH'
                    # txt = amount_txt.replace("KOMA NOL", "")
                    record.amount_text = amount_txt
                else:
                    record.amount_text = record.currency_id.name + ' ' + str(result.capitalize())

    amount_text = fields.Char(string="Terbilang", compute=_amount_to_text, store=False)

    purchase_user_id = fields.Many2one(comodel_name="res.users", string="Purchasing", required=False, )
    manager_user_id = fields.Many2one(comodel_name="res.users", string="Manager Unit", required=False, )
    finance_user_id = fields.Many2one(comodel_name="res.users", string="GM Finance & Accounting", required=False, )

    delivery_company_id = fields.Many2one(comodel_name="res.company", string="Delivery", required=False, default=lambda self: self.env.user.company_id.id)
    da_street = fields.Char(related="delivery_company_id.street")
    da_street2 = fields.Char(related="delivery_company_id.street2")
    da_city = fields.Char(related="delivery_company_id.city")
    da_state_id = fields.Many2one(related="delivery_company_id.state_id")
    da_zip = fields.Char(related="delivery_company_id.zip")

    cp = fields.Char(string="Contact Person", required=False, )
    cp_phone = fields.Char(string="Phone", required=False, )
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', compute="_get_analytic_account")

    @api.depends('order_id.analytic_account_id')
    def _get_analytic_account(self):
        for rec in self:
            rec.analytic_account_id = rec.order_id.analytic_account_id
    
    # def _prepare_account_move_line(self, move=False):
    #     res = super(PurchaseOrderLine,self)._prepare_account_move_line(move)
    #     picking_ids = self.env['stock.picking'].search([('purchase_id', '=', self.order_id.ids)])
    #     for total in picking_ids.move_ids_without_package:
    #         print(total, "ID")
    #         res.update({
    #             'total_karung': total.total_karung,
    #             'potong_karung': total.potong_karung,
    #             'profit_weight' : total.profit_weight,
    #             'gross_weight' : total.gross_weight,
    #             'susut' : total.susut,
    #             'total_berat' : total.total_berat})
    #         return res