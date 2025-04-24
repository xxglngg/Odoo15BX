from odoo import models, fields, api


class InheritBaseImport(models.TransientModel):
    _inherit = 'base_import.import'
    
    @api.model
    def download_template_purchase(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/template_report_purchase',
            'target': 'new',
        }
        
    @api.model
    def download_template_sale(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/template_report_sale',
            'target': 'new',
        }
