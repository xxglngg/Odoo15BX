# See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_time_limit(self):
        self.ensure_one()
        partner = self.partner_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
            [('partner_id', '=', partner.id),
             ('account_id.user_type_id.name', 'in', ['Receivable', 'Payable']),
             ('full_reconcile_id', '=', False)]
        )
        today_dt = datetime.strftime(datetime.now().date(), DF)
        today = datetime.now().date()
        diff = 0
        for line in movelines:
            ### custom if date maturity null use invoice date ###
            date_maturity = line.date_maturity or line.date
            diff = today - date_maturity
            if diff.days > partner.credit_time_limit:
                if not partner.over_credit_time_limit:
                    msg = 'Can not confirm Sale Order, Total mature due days ' \
                            '%s as on %s !\nCheck Partner Accounts or Credit Time ' \
                            'Limits ! (ref: %s)' % (diff.days, today_dt, line.move_id.name)
                    raise UserError(_('Over Customer Credit Time Limit !\n' + msg))
        # invoice_list = []
        # for line in movelines:
        #     ### custom if date maturity null use invoice date ###
        #     date_maturity = line.date_maturity or line.date
        #     diff = today - date_maturity
        #     if diff.days > partner.credit_time_limit:
        #         if not partner.over_credit_time_limit:
        #             if line.move_id.name not in invoice_list:
        #                 invoice_list.append(line.move_id.name)

        # if invoice_list:
        #     note = ', '.join(data for data in invoice_list)
        #     msg = 'Can not confirm Sale Order, Total mature due days ' \
        #             '%s as on %s !\nCheck Partner Accounts or Credit Time ' \
        #             'Limits ! (%s)' % (diff.days, today_dt, note)
        #     raise UserError(_('Over Customer Credit Time Limit !\n' + msg))
        return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.check_time_limit()
        return res
