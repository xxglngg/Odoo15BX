# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id_in_sale_order(self):
        if self.partner_id:
            self.invoice_policy = self.partner_id.invoice_policy
        else:
            self.invoice_policy = False


    partner_invoice_street = fields.Char(string=' ', related='partner_invoice_id.street')
    partner_shipping_street = fields.Char(string=' ', related='partner_shipping_id.street')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for sale in self:
            count_eror = 0
            for line in sale.order_line:
                if line.product_id.product_type_stream == 'downstream' and line.product_uom.id != 12 and line.uom_secondary_id.id != 12:
                    count_eror +=1
                if line.product_id.product_type_stream == 'downstream' and line.uom_secondary_id.id == 12 and line.qty_secondary == 0:
                    count_eror +=1
            if count_eror > 0:
                raise ValidationError(_("Ada product yang uom nya tidak kg" ))

            sale.update_secondary()
        return res


    def update_secondary(self):
        pick = self.env['stock.picking'].sudo().search([('origin','=',self.name)])

        moves = self.env['stock.move'].sudo().search([('picking_id','=',pick.id)])

        if pick.state != 'done':

            for a in self.order_line:
                moves = self.env['stock.move'].sudo().search([('picking_id','=',pick.id),('product_id','=',a.product_id.id)],limit=1)
                # print("=====>", moves, a.qty_secondary, moves.reserved_availability_secondary)
                if a.qty_secondary != moves.reserved_availability_secondary:
                    moves.sudo().write({
                        'reserved_availability_secondary':a.qty_secondary, 
                        'product_uom_secondary':a.uom_secondary_id.id,
                        'reserved_uom_secondary':a.uom_secondary_id.id,
                        'reserved_uom':a.product_uom.id})

                    # print("----xaa udah di update")

                # print("xx", moves, a.qty_secondary, moves.reserved_availability_secondary)


    def _prepare_invoice(self):
        """
        Update Invoice Date By Effective Date
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).', self.company_id.name, self.company_id.id))

        date_gr = False
        if self.effective_date:
            date_gr = self.effective_date + relativedelta(hours=7)

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'user_id': self.user_id.id,
            'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids.filtered(lambda bank: bank.company_id.id in (self.company_id.id, False))[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'invoice_date': date_gr,
        }
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    id_stj = fields.Char(string="ID STJ", compute="compute_stj")
    wac_id = fields.Many2one("account.move", string="STJ", compute='compute_wac_id')
    cost_wac = fields.Float(string="COGS", compute="compute_wac_id")
    effective_date = fields.Datetime(string="Effective Date", related="order_id.effective_date")
    purchase_price = fields.Monetary(string='Purchase Price', currency_field="currency_id")


    def compute_stj(self):
        for rec in self:
            rec.id_stj = False
            moves_list = rec.move_ids

            if moves_list:
                for mover in moves_list:
                    if not mover.origin_returned_move_id:
                        svl = self.env['stock.valuation.layer'].sudo().search([('stock_move_id','=',mover.id)],limit=1)
                        if svl:
                            rec.id_stj = svl.account_move_id.id


    @api.depends('id_stj')
    def compute_wac_id(self):

        for rec in self:
            rec.wac_id = False
            rec.cost_wac = False
            moves_list = rec.move_ids


            if rec.id_stj:
                move = self.env['account.move'].sudo().search([('id','=',rec.id_stj)],limit=1)
                
                move_line = self.env['account.move.line'].sudo().search([('move_id','=',move.id),('debit','!=',0)],limit=1)
                if abs(move_line.quantity) > 0:
                    nilai_debit = abs(move_line.debit / move_line.quantity)
                else:
                    nilai_debit = 0

                rec.wac_id = move
                rec.cost_wac = nilai_debit





