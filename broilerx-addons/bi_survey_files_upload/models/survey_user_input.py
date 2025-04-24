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



        
class SurveyUserInput(models.Model):
    """ Metadata for a set of one user's answers to a particular survey """
    _inherit = "survey.user_input"
    
    def save_lines(self, question, answer, comment=None):
        """ Save answers to questions, depending on question type

            If an answer already exists for question and user_input_id, it will be
            overwritten (or deleted for 'choice' questions) (in order to maintain data consistency).
        """
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])

        if question.question_type in ['char_box', 'text_box', 'numerical_box', 'date', 'datetime']:
            self._save_line_simple_answer(question, old_answers, answer)
            if question.save_as_email and answer:
                self.write({'email': answer})
            if question.save_as_nickname and answer:
                self.write({'nickname': answer})

        elif question.question_type in ['simple_choice', 'multiple_choice']:
            self._save_line_choice(question, old_answers, answer, comment)
        elif question.question_type == 'matrix':
            self._save_line_matrix(question, old_answers, answer, comment)
        
        elif question.question_type in ['upload_file']:
            # pass
            for ans in answer:
                survey_user_input_line_id = self._save_line_file_upload(question, old_answers, ans)
                survey_user_input_line_id.attachment_id.res_id = survey_user_input_line_id.id
        else:
            raise AttributeError(question.question_type + ": This type of question has no saving function")
    
    
    
    def _save_line_file_upload(self, question, old_answers, answer):
        vals = self._get_line_file_values(question, answer, question.question_type)
        if old_answers:
            old_answers.sudo().unlink()
        return self.env['survey.user_input.line'].create(vals)


    def _get_line_file_values(self, question, answer, answer_type):
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': answer_type,
        }
        if not answer or (isinstance(answer, str) and not answer.strip()):
            vals.update(answer_type=None, skipped=True)
            return vals

        if answer_type == 'upload_file':
            
            attachment_obj = self.env['ir.attachment']
            attachment_id = attachment_obj.sudo().create({
                            'name': answer.get('name'),
                            'type': 'binary',
                            'datas': bytes(answer.get('data'), 'utf-8'),
                            'res_model': 'survey.user_input.line',
                            'mimetype': answer.get('type'),
                            'public':True
                        })
            
            vals['attachment_id'] = attachment_id.id
        else:
            vals['value_%s' % answer_type] = answer
        return vals
