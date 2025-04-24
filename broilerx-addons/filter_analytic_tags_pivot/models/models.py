# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritAccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'
#     _description = 'filter_analytic_tags_pivot.filter_analytic_tags_pivot'
    analytic_tags = fields.Char(string='Analytic Tags', readonly=True)

    _depends = {
        'account.move': [
            'name', 'state', 'move_type', 'partner_id', 'invoice_user_id', 'fiscal_position_id',
            'invoice_date', 'invoice_date_due', 'invoice_payment_term_id', 'partner_bank_id',
        ],
        'account.move.line': [
            'quantity', 'price_subtotal', 'amount_residual', 'balance', 'amount_currency',
            'move_id', 'product_id', 'product_uom_id', 'account_id', 'analytic_account_id',
            'journal_id', 'company_id', 'currency_id', 'partner_id','analytic_tags',
        ],
        'product.product': ['product_tmpl_id'],
        'product.template': ['categ_id'],
        'uom.uom': ['category_id', 'factor', 'name', 'uom_type'],
        'res.currency.rate': ['currency_id', 'name'],
        'res.partner': ['country_id'],
    }

    @property
    def _table_query(self):
        return '%s %s %s' % (self._select(), self._from(), self._where())

    @api.model
    def _select(self):
        return '''
                SELECT
                    line.id,
                    line.move_id,
                    line.product_id,
                    line.account_id,
                    line.analytic_account_id,
                    line.analytic_tags,
                    line.journal_id,
                    line.company_id,
                    line.company_currency_id,
                    line.partner_id AS commercial_partner_id,
                    move.state,
                    move.move_type,
                    move.partner_id,
                    move.invoice_user_id,
                    move.fiscal_position_id,
                    move.payment_state,
                    move.invoice_date,
                    move.invoice_date_due,
                    uom_template.id                                             AS product_uom_id,
                    template.categ_id                                           AS product_categ_id,
                    line.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
                                                                                AS quantity,
                    -line.balance * currency_table.rate                         AS price_subtotal,
                    -COALESCE(
                       -- Average line price
                       (line.balance / NULLIF(line.quantity, 0.0)) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
                       -- convert to template uom
                       * (NULLIF(COALESCE(uom_line.factor, 1), 0.0) / NULLIF(COALESCE(uom_template.factor, 1), 0.0)),
                       0.0) * currency_table.rate                               AS price_average,
                    COALESCE(partner.country_id, commercial_partner.country_id) AS country_id
            '''

    @api.model
    def _from(self):
        return '''
                FROM account_move_line line
                    LEFT JOIN res_partner partner ON partner.id = line.partner_id
                    LEFT JOIN product_product product ON product.id = line.product_id
                    LEFT JOIN account_account account ON account.id = line.account_id
                    LEFT JOIN account_account_type user_type ON user_type.id = account.user_type_id
                    LEFT JOIN product_template template ON template.id = product.product_tmpl_id
                    LEFT JOIN uom_uom uom_line ON uom_line.id = line.product_uom_id
                    LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
                    INNER JOIN account_move move ON move.id = line.move_id
                    LEFT JOIN res_partner commercial_partner ON commercial_partner.id = move.commercial_partner_id
                    JOIN {currency_table} ON currency_table.company_id = line.company_id
            '''.format(
            currency_table=self.env['res.currency']._get_query_currency_table(
                {'multi_company': True, 'date': {'date_to': fields.Date.today()}}),
        )

    @api.model
    def _where(self):
        return '''
                WHERE move.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                    AND line.account_id IS NOT NULL
                    AND NOT line.exclude_from_invoice_tab
            '''

class InheritAccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'Account Move Line For Report'

    analytic_tags = fields.Char()

    def cron_check_analytic_tags(self):
        all_update_account_move_line = self.env['account.move.line'].search([])
        print(all_update_account_move_line)
        if all_update_account_move_line:
            arr_data = ''
            for data_update_move_line in all_update_account_move_line:
                if len(data_update_move_line.analytic_tag_ids.ids) > 1:
                    for data_analytic_tags in data_update_move_line.analytic_tag_ids:
                        arr_data = str(data_analytic_tags.name) + ',' + str(arr_data)
                elif len(data_update_move_line.analytic_tag_ids.ids) == 1:
                    arr_data = str(data_update_move_line.analytic_tag_ids.name)


                print(arr_data)
                data_update_move_line.write({
                    'analytic_tags': arr_data,
                })

class InheritAccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        if self.invoice_line_ids.analytic_tag_ids:
            arr_data = ''
            for invoice_line_ids in self.invoice_line_ids:
                if len(invoice_line_ids.analytic_tag_ids.ids) > 1:
                    for data_analytic_tags in invoice_line_ids.analytic_tag_ids:
                        arr_data = str(data_analytic_tags.name) + ',' + str(arr_data)
                elif len(invoice_line_ids.analytic_tag_ids.ids) == 1:
                    arr_data = str(invoice_line_ids.analytic_tag_ids.name)


                print(arr_data)
                invoice_line_ids.write({
                    'analytic_tags': arr_data,
                })
        else:
            self.invoice_line_ids.write({
                'analytic_tags': None,
            })

        res = super(InheritAccountMove,self).action_post()
        return res

    def write(self, vals):
        if self.invoice_line_ids.analytic_tag_ids:
            arr_data = ''
            for invoice_line_ids in self.invoice_line_ids:
                if len(invoice_line_ids.analytic_tag_ids.ids) > 1:
                    for data_analytic_tags in invoice_line_ids.analytic_tag_ids:
                        arr_data = str(data_analytic_tags.name) + ',' + str(arr_data)
                elif len(invoice_line_ids.analytic_tag_ids.ids) == 1:
                    arr_data = str(invoice_line_ids.analytic_tag_ids.name)


                print(arr_data)
                invoice_line_ids.write({
                    'analytic_tags':arr_data,
                })
        else:
            self.invoice_line_ids.write({
                'analytic_tags': None,
            })

        res = super(InheritAccountMove, self).write(vals)
        return res
