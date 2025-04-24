from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import ast


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _query_get(self, domain=None):
        self.check_access_rights('read')

        context = dict(self._context or {})
        domain = domain or []
        if not isinstance(domain, (list, tuple)):
            domain = ast.literal_eval(domain)

        date_field = 'date'
        if context.get('aged_balance'):
            date_field = 'date_maturity'
        if context.get('date_to'):
            domain += [(date_field, '<=', context['date_to'])]
        if context.get('date_from'):
            if not context.get('strict_range'):
                domain += ['|', (date_field, '>=', context['date_from']), ('account_id.user_type_id.include_initial_balance', '=', True)]
            elif context.get('initial_bal'):
                domain += [(date_field, '<', context['date_from'])]
            else:
                domain += [(date_field, '>=', context['date_from'])]

        if context.get('journal_ids'):
            domain += [('journal_id', 'in', context['journal_ids'])]

        state = context.get('state')
        if state and state.lower() != 'all':
            domain += [('parent_state', '=', state)]

        if context.get('company_id'):
            domain += [('company_id', '=', context['company_id'])]
        elif context.get('allowed_company_ids'):
            domain += [('company_id', 'in', self.env.companies.ids)]
        else:
            domain += [('company_id', '=', self.env.company.id)]

        if context.get('reconcile_date'):
            domain += ['|', ('reconciled', '=', False), '|', ('matched_debit_ids.max_date', '>', context['reconcile_date']), ('matched_credit_ids.max_date', '>', context['reconcile_date'])]

        if context.get('account_tag_ids'):
            domain += [('account_id.tag_ids', 'in', context['account_tag_ids'].ids)]

        if context.get('account_ids'):
            domain += [('account_id', 'in', context['account_ids'].ids)]

        if context.get('analytic_tag_ids'):
            try:
                domain += [('analytic_tag_ids', 'in', context['analytic_tag_ids'].ids)]
            except:
                analytic_tags = context['analytic_tag_ids'].replace('account.analytic.tag(','')
                analytic_tags = analytic_tags.replace(')','')
                analytic_tags = [int(id) for id in analytic_tags.split(',') if id != '']
                domain += [('analytic_tag_ids', 'in', analytic_tags)]
                
        if context.get('analytic_account_ids'):
            domain += [('analytic_account_id', 'in', context['analytic_account_ids'].ids)]

        if context.get('partner_ids'):
            try:
                domain += [('partner_id', 'in', context['partner_ids'])]
            except:
                partner_ids = context['partner_ids'].replace('res.partner(','')
                partner_ids = partner_ids.replace(')','')
                partner_ids = [int(id) for id in partner_ids.split(',') if id != '']
                domain += [('partner_id', 'in', partner_ids)]

        if context.get('partner_categories'):
            try:
                domain += [('partner_id.category_id', 'in', context['partner_categories'])]
            except:
                partner_categories = context['partner_categories'].replace('res.partner.category(','')
                partner_categories = partner_categories.replace(')','')
                partner_categories = [int(id) for id in partner_categories.split(',') if id != '']
                domain += [('partner_id.category_id', 'in', partner_categories)]

        where_clause = ""
        where_clause_params = []
        tables = ''
        if domain:
            domain.append(('display_type', 'not in', ('line_section', 'line_note')))
            domain.append(('parent_state', '!=', 'cancel'))

            query = self._where_calc(domain)

            # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
            self._apply_ir_rules(query)

            tables, where_clause, where_clause_params = query.get_sql()
        return tables, where_clause, where_clause_params
    
    @api.depends('product_id', 'account_id', 'partner_id', 'date', 'move_id')
    def _compute_analytic_account_id(self):
        for record in self:
            if record.move_id.analytic_account_assist:
                record.analytic_account_id = record.move_id.analytic_account_id
            else:
                if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
                    rec = self.env['account.analytic.default'].account_get(
                        product_id=record.product_id.id,
                        partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
                        account_id=record.account_id.id,
                        user_id=record.env.uid,
                        date=record.date,
                        company_id=record.move_id.company_id.id
                    )
                    if rec:
                        record.analytic_account_id = rec.analytic_id
