# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritAccuntMove(models.Model):
    _inherit = 'account.move'
    _description = "Additional Sequence Account Move Line"

    name_invoice = fields.Char(compute="_get_active_name_invoice")

    def _get_active_name_invoice(self):
        print(self)
        true = 0
        if len(self.ids) > 0:
            for data_name in self:
                if data_name.name and data_name.move_type == 'out_invoice':
                    invoice_name = data_name.name
                    for check_character in range(len(invoice_name)):
                        if invoice_name[check_character] == '/':
                            true = 1
                    if true == 1:
                        invoice_split = invoice_name.split('/')
                        total_char = len(invoice_split)
                        last = invoice_split[total_char-1]
                        invoice_split.remove(last)
                        invoice_split.insert(0,last)
                        i = 0
                        invoice = ''
                        for str_invoice in invoice_split:
                            if i == 0:
                                invoice = str_invoice
                            else:
                                invoice = invoice +'/'+str_invoice
                            i+=1
                        print(invoice)
                        data_name.write({
                            'name_invoice':invoice,
                        })
                    else:
                        data_name.name_invoice = data_name.name
                else:
                    data_name.name_invoice = data_name.name
        else:
            self.name_invoice = self.name

class InheritAccuntMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = "Additional Sequence Account Move Line"

    name_invoice = fields.Char()
