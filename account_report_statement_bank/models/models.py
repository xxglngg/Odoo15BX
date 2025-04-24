# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritAccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'
    _description = 'Inherit Account Bank Statement'

    user_applicant= fields.Many2one('res.users')
    user_fin_director = fields.Many2one('res.users')
    user_director = fields.Many2one('res.users')
    total_partner = fields.Integer(compute="_get_data_partner")
    data_partner_ids = fields.Many2many('res.partner',compute="_get_data_partner")

    def _get_data_partner(self):
        # test = self.env['account.bank.statement'].search([('id','=',10017)])
        print(self)
        check_various = []
        check_partner = []
        for data_statement in self:
            for line_ids in data_statement.line_ids:
                print(line_ids)
                if line_ids.partner_id:
                    check_partner.append(line_ids.partner_id.id)
                else:
                    check_various.append(0)

            total = len(check_partner) + len(check_various)
            if total == len(data_statement.line_ids.ids):
                all_partner = check_partner + check_various
                data = list(dict.fromkeys(all_partner))
                total_data = len(data)
                data_statement.total_partner = total_data
                data_statement.data_partner_ids = data

    def button_print_voucher(self):
        return self.env.ref('account_report_statement_bank.action_report_account_statement_new').report_action(self)