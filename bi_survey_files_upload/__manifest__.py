# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Survey File Attachment Upload',
    'version': '15.0.0.0',
    'category': 'Survey',
    'summary': 'Survey file upload Survey attachment upload on Survey attach file on Survey attachment upload attachment on Survey binary field Survey multi file upload Survey multi attachment on Survey attach file on Survey attachment answer Survey file upload option',
    'description': """This odoo app add single or multiple file upload options in survey. User can add question in servery as file upload option as answer, participant can upload file as survey answer id upload more then one file warning will show, If enable "Upload Multipal file" option then participant can add multiple file as attachments. Participants can view all uploaded attachments by clicking "review your answer" button on survey. User can also see all uploaded attachments on survey answers.""",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    "price": 15,
    "currency": 'EUR',
    'depends': ['base','survey'],
    'data': [
            'views/survey_question.xml',
            'views/survey_user_input_line.xml',
            'views/survey_template.xml',
             ],
    
    'assets': {
        'survey.survey_assets': [
            'bi_survey_files_upload/static/src/js/survey.js',
            'bi_survey_files_upload/static/src/scss/survey.scss',
            ],
    },
    "license":'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/pNT7LpF22Ik',
    "images":['static/description/Banner.png'],
}
