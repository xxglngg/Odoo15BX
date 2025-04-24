from odoo import models, fields, api
from odoo.http import request
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    license_plate = fields.Char(string="No. Kendaraan", help='License plate number of the vehicle (i = plate number for a car)')
    pengirim = fields.Char(string="Pengirim",)
    qc_by = fields.Many2one(comodel_name="res.users", string="QC by",)
    admin_by = fields.Many2one(comodel_name="res.users", string="Administrasi", )

    document_code = fields.Char(string="Kode Doc.",)
    rev_number = fields.Char(string="Rev",)
    picking_type_code = fields.Selection(related="picking_type_id.code", readonly=True, string="Rev",)

    def action_print_spm(self):
        return self.env.ref('custom_reporting_15.action_report_spm').report_action(self)
    
    def action_print_spj(self):
        return self.env.ref('custom_reporting_15.action_report_spj').report_action(self)

    def action_print_ttb(self):
        return self.env.ref('custom_reporting_15.action_report_ttb').report_action(self)
