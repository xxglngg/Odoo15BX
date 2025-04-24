# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Inherit Model Stock Picking'


    seal_number = fields.Char()
    user_admin_surat_jalan = fields.Many2one('res.users')
    user_gudang_surat_jalan = fields.Many2one('res.users')
    user_pengemudi_surat_jalan = fields.Char()
    user_keamanan_surat_jalan = fields.Char()
    nomor_pelanggan = fields.Char()
    active_menu = fields.Boolean(compute="_get_active_menu")


    def _get_active_menu(self):
        print(self)
        active_id = self.env.context.get('active_id')
        data_picking_type = self.env['stock.picking.type'].search([('code','ilike','outgoing')])

        if self.picking_type_id.id in data_picking_type.ids:
            self.active_menu = True
        else:
            self.active_menu = False
        # if self.picking_type_id

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

    def action_print_sj(self):
        # Code Below for Checking if Product Packaging exist or not
        no_move_ids = True
        for x in self.move_ids_without_package:
            no_move_ids = False
            # if x.quantity_done:
            #     if not x.product_packaging_id:
            #         raise UserError("Product "+str(x.product_id.name)+" Has no product packaging")
        if no_move_ids:
            raise UserError("No operations found on this inventory transaction")
        return self.env.ref('report_surat_jalan.action_report_surat_jalan').report_action(self, config=False)
    
    def action_print_sj_dot_matrix(self):
        # Code Below for Checking if Product Packaging exist or not
        no_move_ids = True
        for x in self.move_ids_without_package:
            no_move_ids = False
            # if x.quantity_done:
            #     if not x.product_packaging_id:
            #         raise UserError("Product "+str(x.product_id.name)+" Has no product packaging")
        if no_move_ids:
            raise UserError("No operations found on this inventory transaction")
        return self.env.ref('report_surat_jalan.action_report_surat_jalan_dot_matrix').report_action(self, config=False)