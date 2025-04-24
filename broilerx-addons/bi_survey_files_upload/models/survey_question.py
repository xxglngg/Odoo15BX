# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import http, models, fields, _
from odoo.http import request
import base64
import json
import re
import ast

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'
    _description = 'Survey Question'


    def validate_question(self, answer, comment=None):
        res = super(SurveyQuestion, self).validate_question(answer, comment)
        if not self.multipal_file and len(answer) > 1 and self.question_type in ['upload_file']:
            return {self.id: "Please add only one file."}
        return res


    @api.depends('is_page')
    def _compute_question_type(self):
        for question in self:
            if not question.question_type or question.is_page:
                question.question_type = False




    question_type = fields.Selection(selection_add=[('upload_file', 'Upload File')], string='Question Type', compute='_compute_question_type', readonly=False, store=True)    
    multipal_file = fields.Boolean('Upload Multipal file')
    
    
    
