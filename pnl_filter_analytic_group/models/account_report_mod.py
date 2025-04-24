from odoo import models, api, fields, _


class ReportAccountFinancialReport(models.AbstractModel):
    _inherit = 'account.financial.html.report'

    def _get_options(self, previous_options=None):
        options = super(ReportAccountFinancialReport, self)._get_options(previous_options)
        options['analytic_groups'] = []
        if not previous_options:
            return options
        
        if previous_options.get('analytic_groups'):
            options['analytic_groups'] = previous_options['analytic_groups']
        
        return options
    
    @api.model
    def _get_options_domain(self, options):
        domain = super(ReportAccountFinancialReport, self)._get_options_domain(options)
        if options.get('analytic_groups'):
            add_analytics = self.env['account.analytic.account'].search([('group_id', 'in', options.get('analytic_groups'))])
            for d in domain:
                if d[0] == 'analytic_account_id':
                    domain.pop(domain.index(d))
            domain.append(('analytic_account_id', 'in', add_analytics.ids))
        return domain

