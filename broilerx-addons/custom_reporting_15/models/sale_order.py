from faulthandler import disable
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class SaleOrder(models.Model):
	_inherit = 'sale.order'

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	