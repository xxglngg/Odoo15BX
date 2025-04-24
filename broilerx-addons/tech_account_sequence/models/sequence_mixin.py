# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import ValidationError
import re


class SequenceMixin(models.AbstractModel):
    _inherit = 'sequence.mixin'

    _sequence_fixed_regex_inv = r'^(?P<seq>\d{0,9})(?P<prefix1>.*?)(?P<year>((?<=\D)|(?<=^))((19|20|21)?\d{2}))(?P<suffix>\D*?)$'

    @api.model
    def _deduce_sequence_number_reset(self, name):
        for regex, ret_val, requirements in [
            (self._sequence_monthly_regex, 'month', ['seq', 'month', 'year']),
            (self._sequence_yearly_regex, 'year', ['seq', 'year']),
            (self._sequence_fixed_regex, 'never', ['seq']),
            (self._sequence_fixed_regex_inv, 'never', ['seq']),
        ]:
            match = re.match(regex, name or '')
            if match:
                groupdict = match.groupdict()
                if all(req in groupdict for req in requirements):
                    return ret_val
        raise ValidationError(_(
            'The sequence regex should at least contain the seq grouping keys. For instance:\n'
            '^(?P<prefix1>.*?)(?P<seq>\d*)(?P<suffix>\D*?)$'
        ))

    def _get_sequence_format_param(self, previous):
        sequence_number_reset = self._deduce_sequence_number_reset(previous)
        regex = self._sequence_fixed_regex
        if sequence_number_reset == 'year':
            regex = self._sequence_yearly_regex
        elif sequence_number_reset == 'month':
            regex = self._sequence_monthly_regex
        format_values = re.match(regex, previous).groupdict()
        format_values['seq_length'] = len(format_values['seq'])
        format_values['year_length'] = len(format_values.get('year', ''))
        if not format_values.get('seq') and 'prefix1' in format_values and 'suffix' in format_values:
            format_values['prefix1'] = format_values['suffix']
            format_values['suffix'] = ''
        for field in ('seq', 'year', 'month'):
            format_values[field] = int(format_values.get(field) or 0)

        placeholders = re.findall(r'(prefix\d|seq|suffix\d?|year|month)', regex)
        format = ''.join(
            "{seq:0{seq_length}d}" if s == 'seq' else
            "{month:02d}" if s == 'month' else
            "{year:0{year_length}d}" if s == 'year' else
            "{%s}" % s
            for s in placeholders
        )
        return format, format_values
