# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools.misc import format_date

from dateutil.relativedelta import relativedelta
from itertools import chain
from odoo.exceptions import UserError, ValidationError

from odoo.tools.float_utils import float_is_zero
from ...account_consolidation.report.handler.show_zero import ShowZeroHandler
from ...account_consolidation.report.builder.abstract import AbstractBuilder
from ...account_consolidation.report.builder.comparison import ComparisonBuilder
from ...account_consolidation.report.builder.default import DefaultBuilder
from ...account_consolidation.report.handler.journals import JournalsHandler
from ...account_consolidation.report.handler.periods import PeriodsHandler
from collections import OrderedDict


# class AbstractBuilderCustom(AbstractBuilder):
    
#     def _format_account_line(self, account, level: int, totals: list, options: dict, **kwargs) -> dict:
#         """
#         Build an account line.
#         :param account: the account object
#         :param level: the level of the line (to allow indentation to be kept)
#         :type level: int
#         :param totals: the already computed totals for the account
#         :param options: options of the report
#         :type options: dict
#         :return: a formatted dict representing the account line
#         :rtype: dict
#         """
#         # Columns
#         cols = [{
#             'name': self.value_formatter(abs(total)),
#             'no_format_name': abs(total),
#             'class': 'number' + (' text-muted' if float_is_zero(total, 6) else '')}
#             for total in totals]

#         # Line
#         name = account.name_get()[0][1]
#         account_line = {
#             'id': account.id,
#             'name': len(name) > 40 and not self.env.context.get('print_mode') and name[:40] + '...' or name,
#             'title_hover': _("%s (%s Currency Conversion Method)") % (account.name, account.get_display_currency_mode()),
#             'columns': cols,
#             'level': level
#         }
#         if account.group_id:
#             parent_id = 'section-%s' % account.group_id.id
#             account_line['parent_id'] = parent_id
#             if options is not None:
#                 account_line['unfolded'] = options.get('unfold_all', parent_id in options.get('unfolded_lines', []))
#         return account_line

#     def _build_section_line(self, section, level: int, options: dict, **kwargs) -> tuple:
#         """
#         Build a section line and all its descendants lines (if any).
#         :param section: the section object
#         :param level: the level of the line (to allow indentation to be kept)
#         :type level: int
#         :param options: options of the report
#         :type options: dict
#         :return: a tuple with :
#         - a list of formatted dict containing the section line itself and all the descendant lines of this
#         (so that the section line is the first dict of the list)
#         - the totals of the section line
#         :rtype: tuple
#         """
#         section_id = 'section-%s' % section.id
#         section_line = {
#             'id': section_id,
#             'name': section.name,
#             'level': level,
#             'unfoldable': True,
#             'unfolded': options.get('unfold_all', False) or section_id in options.get('unfolded_lines', [])
#         }
#         if section.parent_id:
#             section_line['parent_id'] = 'section-%s' % section.parent_id.id
#         lines = [section_line]

#         # HANDLE CHILDREN
#         section_totals = None
#         if len(section.child_ids) > 0:
#             for child_section in section.child_ids:
#                 # This will return the section line THEN all subsequent lines
#                 child_totals, descendant_lines = self._build_section_line(child_section, level + 1, options, **kwargs)
#                 section_totals = [x + y for x, y in
#                                   zip(section_totals, child_totals)] if section_totals is not None else child_totals
#                 if section_line['unfolded'] and ShowZeroHandler.section_line_should_be_added(descendant_lines, options):
#                     lines += descendant_lines

#         # HANDLE ACCOUNTS
#         if len(section.account_ids) > 0:
#             for child_account in section.account_ids:
#                 account_totals = self._compute_account_totals(child_account.id, **kwargs)
#                 account_line = self._format_account_line(child_account, level + 1, account_totals, options, **kwargs)
#                 section_totals = [x + y for x, y in
#                                   zip(section_totals, account_totals)] if section_totals is not None else account_totals
#                 if section_line['unfolded'] and ShowZeroHandler.account_line_should_be_added(account_line, options):
#                     lines.append(account_line)

#         if section_totals is None:
#             section_totals = self._get_default_line_totals(options, **kwargs)
#         section_line['columns'] = [{'name': self.value_formatter(abs(total)), 'no_format_name': abs(total)}
#                                    for total in section_totals]
#         return section_totals, lines


#     def _build_total_line(self, totals: list, options: dict, **kwargs) -> dict:
#         """
#         Build the total line, based on given totals list. Values are formatted using self value formatter.
#         :param totals: the list of totals amounts
#         :type totals: list
#         :param options: options of the report
#         :type options: dict
#         :return: a formatted dict representing the total line to be displayed on report
#         :rtype: dict
#         """
#         cols = [{
#             'name': self.value_formatter(abs(total)), 'no_format_name': abs(total),
#             'class': 'number' + (' text-danger' if not float_is_zero(total, 6) else '')
#         } for total in totals]

#         return {
#             'id': 'grouped_accounts_total',
#             'name': _('Total'),
#             'class': 'total',
#             'columns': cols,
#             'level': 1,
#         }

class AccountConsolidationTrialBalanceReport(models.AbstractModel):
    _inherit = "account.consolidation.trial_balance_report"

    ######### Override function ##########
    @api.model
    def _get_lines(self, options, line_id=None):
        selected_aps = self._get_period_ids(options)
        selected_ap = self._get_selected_period()

        # comparison
        if len(selected_aps) > 1:
            builder = ComparisonBuilder(self.env, selected_ap._format_value)
        else:
            journal_ids = JournalsHandler.get_selected_values(options)
            journals = self.env['consolidation.journal'].browse(journal_ids)
            builder = DefaultBuilder(self.env, selected_ap._format_value, journals)
        
        result = builder.get_lines(selected_aps, options, line_id)
        for data in result:
            if data['name'] != 'Total':
                for line in data['columns']:
                    amount_data = line['name'].encode('ascii','ignore').decode("utf-8") 
                    amount = amount_data.replace("-", " ")
                    line['name'] = amount
                    line['no_format_name'] = abs(line['no_format_name'])
        return result