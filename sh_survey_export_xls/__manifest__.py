# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Export Survey XLS Report",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "license": "OPL-1",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
    "summary": "Export Survey Answer In XLS Export Survey Answer In XLS Report Export Survey In XLS Export Completed Survey Answers Export  Group Surveys Export Survey In Excel Export Survey In XLSX Export Survey XLSX Survey Export Survey Excel Odoo",
    "description": """This module helps to export survey answers in XLS format. You can export survey with 2 options: 1) Only Completed Surveys 2) Group By Partner""",
    "version": "15.0.3",
    "depends": ['survey', ],
    "application": True,
    "data": [
        'security/ir.model.access.csv',
        'wizard/sh_survey_export_xls_wizard.xml',
    ],
    "auto_install": False,
    "installable": True,
    "images": ["static/description/background.png", ],
    "price": 30,
    "currency": "EUR"
}
