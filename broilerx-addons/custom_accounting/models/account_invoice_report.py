from odoo import models, fields, api, _

class InheritAccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    payment_paid = fields.Char(compute='_compute_payment_amount', string="Payment Paid")
    payment_name = fields.Char(compute='_compute_payment_amount', string="Payment Name")
    payment_journal = fields.Char(compute='_compute_payment_amount', string="Payment Journal")
    jumlah_ekoran = fields.Float(compute='_compute_analytic_jumlah_ekoran', string="Jumlah Ekoran")
    
    def _compute_analytic_jumlah_ekoran(self):
         for inv in self:
            for line in inv.move_id:
                ekor = sum(line.invoice_line_ids.mapped('jumlah_ekoran'))
                inv.jumlah_ekoran = ekor

    def _compute_payment_amount(self):
        for inv in self:
            if inv.move_id:
                inv.payment_paid = inv.move_id.payment_paid
                inv.payment_name = inv.move_id.payment_name
                inv.payment_journal = inv.move_id.payment_journal