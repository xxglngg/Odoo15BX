# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import http, models, fields, _
from odoo.http import request
import base64
import json
import re
import ast
from odoo.tools import float_compare, float_is_zero

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


    
class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'
    _description = 'Survey User Input Line'
    
    answer_type = fields.Selection(selection_add=[('upload_file', 'Upload File')], string='Answer Type')
    attachment_id = fields.Many2one('ir.attachment', string='Attachment')
    attachment = fields.Binary("File", related='attachment_id.datas')
    name = fields.Char(name="file name", related='attachment_id.name')
    
    
    
    @api.constrains('skipped', 'answer_type')
    def _check_answer_type_skipped(self):
        for line in self:
            if (line.skipped == bool(line.answer_type)):
                raise ValidationError(_('A question can either be skipped or answered, not both.'))

            # allow 0 for numerical box
            if line.answer_type == 'numerical_box' and float_is_zero(line['value_numerical_box'], precision_digits=6):
                continue
            if line.answer_type == 'suggestion':
                field_name = 'suggested_answer_id'
                
            elif line.answer_type == 'upload_file':
                field_name = False
                
            elif line.answer_type:
                field_name = 'value_%s' % line.answer_type
            else:  # skipped
                field_name = False

            if field_name and not line[field_name]:
                raise ValidationError(_('The answer must be in the right type'))
    
    
