# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InformationSaleOrderQuantityOrdered(models.Model):
    _name = 'sale.order.information.quantity.ordered'
    _description = 'new model for sale order view quantity ordered'

    name = fields.Char()
    sale_order_id = fields.Many2one('sale.order')
    sale_order_line_id = fields.Many2one('sale.order.line')
    check_insert_info_ordered = fields.Boolean(default=False)

class InformationSaleOrderQuantityDelivered(models.Model):
    _name = 'sale.order.information.quantity.delivered'
    _description = 'new model for sale order view quantity delivered'

    name = fields.Char()
    sale_order_id =fields.Many2one('sale.order')
    sale_order_line_id = fields.Many2one('sale.order.line')
    check_insert_info_delivered = fields.Boolean(default=False)

class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Inherit From Sale Order'

    info_quantity_ordered = fields.Many2many('sale.order.information.quantity.ordered', compute="_get_quantity_sale_order_information")
    info_quantity_delivered = fields.Many2many('sale.order.information.quantity.delivered', compute="_get_quantity_sale_order_information")

    def _get_quantity_sale_order_information(self):

        print(self)

        for data_sale_order in self:
            info_ordered = []
            info_delivered = []
            print(data_sale_order)
            if data_sale_order.order_line:
                for info_product_ids in data_sale_order.order_line:
                    check_id_sale_order = self.env['sale.order.information.quantity.ordered'].search([('sale_order_line_id','=',info_product_ids.id)])

                    if check_id_sale_order.check_insert_info_ordered:

                        check_id_sale_order.write({
                            'name': str(info_product_ids.product_uom_qty) +''+info_product_ids.product_uom.name
                        })
                        print(check_id_sale_order.id)
                        info_ordered.append(check_id_sale_order.id)
                    else:
                        info_ordered_id = self.env['sale.order.information.quantity.ordered'].create({
                            'sale_order_id':data_sale_order.id,
                            'name':str(info_product_ids.product_uom_qty)+''+info_product_ids.product_uom.name,
                            'sale_order_line_id':info_product_ids.id,
                        })

                        info_ordered.append(info_ordered_id.id)

                    check_id_sale_order_delivered = self.env['sale.order.information.quantity.delivered'].search([('sale_order_line_id','=',info_product_ids.id)])

                    if check_id_sale_order_delivered.check_insert_info_delivered:

                            check_id_sale_order_delivered.write({
                                'name': str(info_product_ids.qty_delivered)+''+info_product_ids.product_uom.name,
                            })
                            info_ordered.append(check_id_sale_order_delivered.id)
                    else:
                        info_delivered_id = self.env['sale.order.information.quantity.delivered'].create({
                            'sale_order_id': data_sale_order.id,
                            'name': str(info_product_ids.qty_delivered)+''+info_product_ids.product_uom.name,
                            'sale_order_line_id': info_product_ids.id,
                        })
                        info_ordered.append(info_delivered_id.id)

                data_sale_order.info_quantity_ordered = info_ordered
                data_sale_order.info_quantity_delivered = info_delivered

                update_check_delivered = self.env['sale.order.information.quantity.delivered'].search([('sale_order_id', '=', data_sale_order.id)])
                update_check_delivered.write({
                    'check_insert_info_delivered':True,
                })

                update_check_ordered = self.env['sale.order.information.quantity.ordered'].search([('sale_order_id', '=', data_sale_order.id)])
                update_check_ordered.write({
                    'check_insert_info_ordered': True,
                })
            else:
                data_sale_order.info_quantity_ordered = None
                data_sale_order.info_quantity_delivered = None