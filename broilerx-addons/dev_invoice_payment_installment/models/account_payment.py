# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime

class account_payment(models.Model):
    _inherit = 'account.payment'
    
    installment_id = fields.Many2one('invoice.installment.lines', string='Installment')
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
