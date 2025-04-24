# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(comodel_name="res.currency", related="company_id.currency_id",
                                          string="Company Currency", readonly=True)
    material_cost = fields.Monetary(string='Material Cost', currency_field="company_currency_id", compute='compute_material_cost', store=True)
    material_cost_by_quantity = fields.Monetary(string='Material Cost by Qty', currency_field="company_currency_id", compute='compute_material_cost', store=True)
    fix_cost = fields.Monetary(string='Fix Cost', currency_field="company_currency_id", compute='compute_fix_cost', store=True)
    adjusted_material_cost = fields.Monetary(string='Adjusted Material Cost', currency_field="company_currency_id", compute='compute_adjusted_material_cost', store=True)
    mrp_production_ids_stock_landed_cost_count = fields.Integer(compute="_compute_landed_costs")

    @api.depends('move_raw_ids', 'move_raw_ids.product_qty', 'move_raw_ids.price_unit')
    def compute_material_cost(self):
        for rec in self:
            if rec.state != 'draft':
                rec.material_cost = 0
                rec.material_cost_by_quantity = 0
                for line in rec.move_raw_ids:
                    if line.split_method == 'by_ratio':
                        rec.material_cost += line.subtotal_material
                    elif line.split_method == 'by_quantity':
                        rec.material_cost_by_quantity += line.subtotal_material
                rec.compute_fix_cost()
                rec.compute_by_quantity()

    @api.depends('material_cost', 'fix_cost')
    def compute_adjusted_material_cost(self):
        for rec in self:
            rec.adjusted_material_cost = rec.material_cost - rec.fix_cost

    @api.depends('move_raw_ids', 'move_byproduct_ids')
    def compute_fix_cost(self):
        for rec in self:
            rec.fix_cost = 0
            total_cost = 0
            if rec.state == 'draft':
                for line in rec.move_byproduct_ids:
                    line.is_fix_cost = line.byproduct_id.is_fix_cost
                    line.fix_cost_price = line.byproduct_id.fix_cost
                    line.product_uom_qty = line.quantity_done
                    line.ratio = line.byproduct_id.ratio

            for line in rec.move_byproduct_ids.filtered(lambda x: x.cost > 0):
                line.cost = 0

            for line in rec.move_byproduct_ids.filtered(lambda x: x.quantity_done > 0):
                if line.is_fix_cost:
                    line.cost = line.fix_cost_price * line.quantity_done
                    rec.fix_cost += line.cost
                    total_cost += line.cost

            total_ratio_qty = 0
            for line in rec.move_byproduct_ids.filtered(lambda x: x.quantity_done > 0):
                total_ratio_qty += line.ratio * line.quantity_done
                line.product_uom_qty = line.quantity_done
            for line in rec.move_byproduct_ids.filtered(lambda x: x.quantity_done > 0):
                if not line.is_fix_cost:
                    if total_ratio_qty:
                        line.cost = (line.ratio * line.quantity_done) / total_ratio_qty * rec.adjusted_material_cost
                        total_cost += line.cost
            if total_cost != rec.material_cost:
                selisih = rec.material_cost - total_cost
                for line in rec.move_byproduct_ids.filtered(lambda x: x.quantity_done > 0):
                    if not line.is_fix_cost and line.quantity_done > 0:
                        line.cost += selisih
                        break

    @api.depends('move_raw_ids', 'move_byproduct_ids.quantity_done')
    def compute_by_quantity(self):
        for rec in self:
            total_cost = 0
            products_move_raw_ids = rec.move_raw_ids.filtered(lambda x: x.split_method == 'by_quantity')
            total_qty_move_raw_ids = sum(x.quantity_done for x in products_move_raw_ids)
            total_qty_move_byproduct_ids = sum(x.quantity_done for x in rec.move_byproduct_ids)

            for line in rec.move_byproduct_ids.filtered(lambda x: x.quantity_done > 0):
                if total_qty_move_byproduct_ids:
                    line.cost += line.quantity_done / total_qty_move_byproduct_ids * rec.material_cost_by_quantity
                    total_cost += line.cost

            if total_cost != rec.material_cost + rec.material_cost_by_quantity:
                selisih = rec.material_cost + rec.material_cost_by_quantity - total_cost
                for line in rec.move_byproduct_ids.filtered(lambda x: x.quantity_done > 0):
                    if not line.is_fix_cost and line.quantity_done > 0:
                        line.cost += selisih
                        break


    @api.constrains('move_byproduct_ids')
    def _check_byproducts(self):
        for order in self:
            if any(move.cost_share < 0 for move in order.move_byproduct_ids):
                raise ValidationError(_("By-products cost shares must be positive."))
            # if sum(order.move_byproduct_ids.mapped('cost_share')) > 100:
            #     raise ValidationError(_("The total cost share for a manufacturing order's by-products cannot exceed 100."))
            # if sum(order.move_byproduct_ids.mapped('product_uom_qty')) > sum(order.move_raw_ids.mapped('product_uom_qty')):
            #     raise ValidationError(_("The total To Produce in Production Results cant greater than total To Consume in Components."))

            # if sum(order.move_byproduct_ids.mapped('quantity_done')) > sum(order.move_raw_ids.mapped('product_uom_qty')):
            #     raise ValidationError(_("The total To Produce in Production Results cant greater than total To Consume in Components."))
    @api.onchange('qty_producing')
    def _onchange_warning_product_qty(self):
        if self.qty_producing > self.product_uom_qty:
            raise ValidationError(_("Quantity cant greather than %s") % self.product_uom_qty)

    @api.onchange('move_raw_ids')
    def _onchange_warning_move_raw_ids(self):
        if sum(line.product_uom_qty for line in self.move_raw_ids) > self.product_uom_qty:
            # raise ValidationError(_("To consume in Components cant greather than %s") % self.product_uom_qty)
            pass

    def action_confirm(self):
        result = super(MrpProduction, self).action_confirm()
        self.guard_mo_one_product()
        self.qty_producing = self.product_qty
        self.action_assign()
        return result

    def action_assign(self):
        res = super(MrpProduction, self).action_assign()
        if self.purchase_id:
            for picking in self.purchase_id.picking_ids:
                for move_line_picking in picking.move_line_ids_without_package:
                    for move in self.move_raw_ids:
                        if move_line_picking.product_id.id == move.product_id.id:
                            if not move.show_lots_text and not move.production_id:
                                for move_line in move.move_line_ids:
                                    move_line.lot_id = move_line_picking.lot_id.id
        return res

    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        self.ensure_one()
        # super(MrpProduction, self)._cal_price(consumed_moves)
        work_center_cost = 0
        finished_move = self.move_finished_ids.filtered(
            lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            for work_order in self.workorder_ids:
                time_lines = work_order.time_ids.filtered(
                    lambda x: x.date_end and not x.cost_already_recorded)
                duration = sum(time_lines.mapped('duration'))
                time_lines.write({'cost_already_recorded': True})
                work_center_cost += (duration / 60.0) * \
                    work_order.workcenter_id.costs_hour
            qty_done = finished_move.product_uom._compute_quantity(
                finished_move.quantity_done, finished_move.product_id.uom_id)
            extra_cost = self.extra_cost * qty_done
            total_cost = (sum(-m.stock_valuation_layer_ids.value for m in consumed_moves.sudo()) + work_center_cost + extra_cost)
            byproduct_moves = self.move_byproduct_ids.filtered(lambda m: m.state not in ('done', 'cancel') and m.quantity_done > 0)
            byproduct_cost_share = 0
            byproduct_cost_share_value = 0
            for byproduct in byproduct_moves:
                if byproduct.cost_share == 0:
                    continue
                byproduct_cost_share += byproduct.cost_share
                byproduct_cost_share_value += byproduct.cost
                if byproduct.product_id.cost_method in ('fifo', 'average'):
                    # byproduct.price_unit = total_cost * byproduct.cost_share / 100 / byproduct.product_uom._compute_quantity(byproduct.quantity_done, byproduct.product_id.uom_id)
                    byproduct.price_unit = byproduct.cost / byproduct.product_uom._compute_quantity(byproduct.quantity_done, byproduct.product_id.uom_id)
            if finished_move.product_id.cost_method in ('fifo', 'average'):
                # finished_move.price_unit = total_cost * float_round(1 - byproduct_cost_share / 100, precision_rounding=0.0001) / qty_done
                finished_move.price_unit = (total_cost - byproduct_cost_share_value) / finished_move.quantity_done
        return True

    def _compute_landed_costs(self):
        for record in self:
            record['mrp_production_ids_stock_landed_cost_count'] = self.env['stock.landed.cost'].search_count([('mrp_production_ids', '=', record.id)])
            for byproduct_line in record.move_byproduct_ids.filtered(lambda x: x.quantity_done > 0):
                byproduct_line.landed_cost = 0

            for landed_cost in self.env['stock.landed.cost'].search([('mrp_production_ids', '=', record.id)]):
                if landed_cost.state == 'done':
                    for line in landed_cost.valuation_adjustment_lines:
                        for byproduct_line in record.move_byproduct_ids.filtered(lambda x: x.quantity_done > 0):
                            if byproduct_line.product_id == line.product_id:
                                byproduct_line.landed_cost += line.additional_landed_cost

    def button_mark_done(self):
        self.guard_product_reslut_nol()
        self.guard_mo_one_result()
        self.check_same_raw_product()

        for a in self.move_raw_ids:
            for b in a.move_line_ids:
                if b.product_uom_qty > 0 and b.qty_done == 0:
                    # b.sudo().unlink()
                    self.env.cr.execute("""DELETE FROM STOCK_MOVE_LINE WHERE ID = %s""", [b.id])
                    # print("======", b)

                if b.product_uom_qty == 0 and b.qty_done == 0:
                    self.env.cr.execute("""DELETE FROM STOCK_MOVE_LINE WHERE ID = %s""", [b.id])
                    # b.sudo().unlink()

        
        res = super(MrpProduction, self).button_mark_done()
        for rec in self:
            if rec.env.context.get('button_mark_done_production_ids'):
                for move in rec.move_byproduct_ids.filtered(lambda x: x.quantity_done > 0):
                    for move_line in move.move_line_ids.filtered(lambda x: x.qty_done > 0):
                        if move_line.lot_id and move_line.lot_id.product_qty:
                            move_line.lot_id.inventory_value += move_line.move_id.cost
                            move_line.lot_id.input_price = move_line.lot_id.inventory_value / move_line.lot_id.product_qty
                            move_line.lot_id.unit_price = move_line.lot_id.inventory_value / move_line.lot_id.product_qty
                            move_line.lot_id.landed_cost_price = 0
        return res


    def guard_mo_one_product(self):
        """Agar User Hanya bisa Create MO dengan 1 Product Component Saja"""
        print(".....Agar User Hanya bisa Create MO dengan 1 Product Component Saja....")
        for mo in self:
            no_component = 0
            count_double = mo.move_raw_ids.search_count([('raw_material_production_id','=',mo.id),('product_uom_qty', '>', 0),('product_id.detailed_type','=','product'),('product_id.product_tmpl_id.is_packaging','!=',True)])

            if count_double > 1 and mo.bom_id.is_special_bom != True:
                raise ValidationError(_("Component telah terisi, mohon untuk mengganti componen tersebut"))



    def guard_mo_one_result(self):
        """Agar User Hanya bisa Create MO dengan 1 Product Component Saja"""
        print(".....Agar User Hanya bisa Create MO dengan 1 Product Result Saja....")
        for mo in self:
            domain = [('production_id','=',mo.id),('quantity_done', '>', 0),('product_id.detailed_type','=','product'),('product_id.categ_id.id','!=','183')]

            count_result = 0
            for a in mo.env['stock.move'].search(domain):
                if a.quantity_done > 0:
                    count_result+=1

            is_lb_component = False
            for b in mo.env['stock.move'].search([('raw_material_production_id','=',mo.id),('product_id.categ_id.id','=','37')],limit=1):
                is_lb_component = True

            if count_result > 1 and is_lb_component == False:
                raise ValidationError(_("Production Result telah terisi %s, mohon untuk mengganti production result tersebut " %(count_result)))
            
            domain_component_adhoc = [('raw_material_production_id','=',mo.id),\
                                        ('product_id.detailed_type','=','product'),('product_id.product_tmpl_id.is_packaging','!=',True),('product_id.categ_id.id','!=','183')]

            count_component_adhoc = 0
            for a in mo.env['stock.move'].search(domain_component_adhoc):
                for b in a.move_line_ids:
                    if a.product_uom_qty == 0 and b.qty_done > 0:
                        count_component_adhoc+=1


            if count_component_adhoc > 0:
                raise ValidationError(_("Jangan Menambahkan Product Kembali Ketika proses sudah berjalan" ))
            


    # @api.onchange('purchase_id')
    def check_same_raw_product(self):

        for mo in self:
            if mo.bom_id.is_special_bom == False:
                for b in mo.move_raw_ids:
                    if b.product_id.product_tmpl_id.is_packaging != True and b.product_id.categ_id.id != '183':
                        for c in mo.move_byproduct_ids:
                            if b.product_id == c.product_id:
                                if c.quantity_done > 0:
                                    for d in c.move_line_ids:
                                        raise ValidationError(
                                            _("Product Result [%s] - %s Tidak Boleh Sama dengan Material" %(c.product_id.default_code, c.product_id.name)))
                                   
    def guard_product_reslut_nol(self):
        for mo in self:
            if mo.product_id.categ_id.id == 183:
                count_cost = 0
                for a in self.env['stock.move'].search([('production_id', '=', mo.id),('product_id.categ_id','!=',183),('cost','>',0)]):
                    count_cost += 1

                if count_cost == 0:
                    raise ValidationError(_("Anda Lupa Menginputkan product Result !!" ))
