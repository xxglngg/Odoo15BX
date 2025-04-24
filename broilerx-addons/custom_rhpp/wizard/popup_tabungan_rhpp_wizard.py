from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError, UserError

class PopupTabunganRhppWizard(models.TransientModel):
    _name = 'popup.tabungan.rhpp.wizard'
    _description = 'Popup Tabungan Wizard RHPP'

    analytic_rhpp_id = fields.Many2one('analytic.rhpp', string='Analytic Rhpp')

    @api.model
    def default_get(self, fields):
        res = super(PopupTabunganRhppWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        analytic_rhpp = self.env['analytic.rhpp'].browse(active_id)
        if 'analytic_rhpp_id' in fields:
            res.update({'analytic_rhpp_id': analytic_rhpp.id})
        return res

    def confirm_penarikan(self):
        for rec in self:
            analytic_rhpp =  self.env['analytic.rhpp'].search([('id', '=', rec.analytic_rhpp_id.id)])
            if analytic_rhpp:
                analytic_rhpp.state = 'unit'
    
    def cancel_penarikan(self):
        for rec in self:
            analytic_rhpp =  self.env['analytic.rhpp'].search([('id', '=', rec.analytic_rhpp_id.id)])
            if analytic_rhpp:
                analytic_rhpp.is_penarikan_tabungan = False
                analytic_rhpp.state = 'unit'