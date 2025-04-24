# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models

class Move(models.Model):
    _inherit = 'stock.move'

    def _check_stock_account_installed(self):
        stock_account_app = self.env['ir.module.module'].sudo().search([('name','=','stock_account')],limit=1)
        if stock_account_app.state != 'installed':
            return False
        else:
            return True


    def _sh_unreseve_qty(self):
        
        for move_line in self.sudo().mapped('move_line_ids'):
            # unreserve qty
            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity + move_line.qty_done})

            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity - move_line.qty_done})

    def action_move_cancel(self):
        for rec in self:
            rec.sudo().write({'state': 'cancel'})
            rec.mapped('move_line_ids').sudo().write({'state': 'cancel'})
            rec._sh_unreseve_qty()

            if rec._check_stock_account_installed():
                # cancel related accouting entries
                account_move = rec.sudo().mapped('account_move_ids')
                account_move_line_ids = account_move.sudo().mapped('line_ids')
                reconcile_ids = []
                if account_move_line_ids:
                    reconcile_ids = account_move_line_ids.sudo().mapped('id')
                reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                if reconcile_lines:
                    reconcile_lines.sudo().unlink()
                account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                account_move.sudo().write({'state':'draft','name':'/'})
                account_move.sudo().with_context({'force_delete':True}).unlink()
            
                # cancel stock valuation
                stock_valuation_layer_ids = rec.sudo().mapped('stock_valuation_layer_ids')
                if stock_valuation_layer_ids:
                    stock_valuation_layer_ids.sudo().unlink()

    def action_move_cancel_draft(self):
        for rec in self:
            rec.sudo().write({'state': 'draft'})
            rec.mapped('move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()

            if rec._check_stock_account_installed():
                # cancel related accouting entries
                account_move = rec.sudo().mapped('account_move_ids')
                account_move_line_ids = account_move.sudo().mapped('line_ids')
                reconcile_ids = []
                if account_move_line_ids:
                    reconcile_ids = account_move_line_ids.sudo().mapped('id')
                reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                if reconcile_lines:
                    reconcile_lines.sudo().unlink()
                account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                account_move.sudo().write({'state':'draft','name':'/'})
                account_move.sudo().with_context({'force_delete':True}).unlink()
            
                # cancel stock valuation
                stock_valuation_layer_ids = rec.sudo().mapped('stock_valuation_layer_ids')
                if stock_valuation_layer_ids:
                    stock_valuation_layer_ids.sudo().unlink()

    def action_move_cancel_delete(self):
        for rec in self:
            rec.sudo().write({'state': 'draft'})
            rec.mapped('move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()

            if rec._check_stock_account_installed():
                # cancel related accouting entries
                account_move = rec.sudo().mapped('account_move_ids')
                account_move_line_ids = account_move.sudo().mapped('line_ids')
                reconcile_ids = []
                if account_move_line_ids:
                    reconcile_ids = account_move_line_ids.sudo().mapped('id')
                reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                if reconcile_lines:
                    reconcile_lines.sudo().unlink()
                account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                account_move.sudo().write({'state':'draft','name':'/'})
                account_move.sudo().with_context({'force_delete':True}).unlink()
            
                # cancel stock valuation
                stock_valuation_layer_ids = rec.sudo().mapped('stock_valuation_layer_ids')
                if stock_valuation_layer_ids:
                    stock_valuation_layer_ids.sudo().unlink()
            rec.mapped('move_line_ids').sudo().unlink()
            rec.sudo().unlink()


class Picking(models.Model):
    _inherit = 'stock.picking'

    def _check_stock_account_installed(self):
        stock_account_app = self.env['ir.module.module'].sudo().search([('name','=','stock_account')],limit=1)
        if stock_account_app.state != 'installed':
            return False
        else:
            return True

    def action_picking_cancel(self):
        for rec in self:
            # cancel packages
            if rec.move_line_ids.mapped('result_package_id'):
                packages = rec.move_line_ids.mapped('result_package_id')
                if packages:
                    packages.unpack()
                
            if rec.package_level_ids_details:
                rec.package_level_ids_details.sudo().unlink()

            if rec.sudo().mapped('move_ids_without_package'):
                rec._sh_unreseve_qty()
                rec.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'cancel'})
                rec.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                

                if rec._check_stock_account_installed():
                        
                    # cancel related accouting entries
                    account_move = rec.sudo().mapped('move_ids_without_package').sudo().mapped('account_move_ids')
                    account_move_line_ids = account_move.sudo().mapped('line_ids')
                    reconcile_ids = []
                    if account_move_line_ids:
                        reconcile_ids = account_move_line_ids.sudo().mapped('id')
                    reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                    if reconcile_lines:
                        reconcile_lines.sudo().unlink()
                    account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                    account_move.sudo().write({'state':'draft','name':'/'})
                    account_move.sudo().with_context({'force_delete':True}).unlink()
                    
                    # cancel stock valuation
                    stock_valuation_layer_ids = rec.sudo().mapped('move_ids_without_package').sudo().mapped('stock_valuation_layer_ids')
                    if stock_valuation_layer_ids:
                        stock_valuation_layer_ids.sudo().unlink()

            rec.sudo().write({'state': 'cancel'})

    def action_picking_cancel_draft(self):
        for rec in self:
            # cancel packages
            if rec.move_line_ids.mapped('result_package_id'):
                packages = rec.move_line_ids.mapped('result_package_id')
                if packages:
                    packages.unpack()
                
            if rec.package_level_ids_details:
                rec.package_level_ids_details.sudo().unlink()


            if rec.sudo().mapped('move_ids_without_package'):
                rec.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec._sh_unreseve_qty()

                if rec._check_stock_account_installed():
                        
                    # cancel related accouting entries
                    account_move = rec.sudo().mapped('move_ids_without_package').sudo().mapped('account_move_ids')
                    account_move_line_ids = account_move.sudo().mapped('line_ids')
                    reconcile_ids = []
                    if account_move_line_ids:
                        reconcile_ids = account_move_line_ids.sudo().mapped('id')
                    reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                    if reconcile_lines:
                        reconcile_lines.sudo().unlink()
                    account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                    account_move.sudo().write({'state':'draft','name':'/'})
                    account_move.sudo().with_context({'force_delete':True}).unlink()
                    
                    # cancel stock valuation
                    stock_valuation_layer_ids = rec.sudo().mapped('move_ids_without_package').sudo().mapped('stock_valuation_layer_ids')
                    if stock_valuation_layer_ids:
                        stock_valuation_layer_ids.sudo().unlink()

            
            rec.sudo().write({'state': 'draft'})

    def action_picking_cancel_delete(self):
        for rec in self:
            # cancel packages
            if rec.move_line_ids.mapped('result_package_id'):
                packages = rec.move_line_ids.mapped('result_package_id')
                if packages:
                    packages.unpack()
                
            if rec.package_level_ids_details:
                rec.package_level_ids_details.sudo().unlink()

            if rec.sudo().mapped('move_ids_without_package'):
                rec.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec._sh_unreseve_qty()

                if rec._check_stock_account_installed():
                        
                    # cancel related accouting entries
                    account_move = rec.sudo().mapped('move_ids_without_package').sudo().mapped('account_move_ids')
                    account_move_line_ids = account_move.sudo().mapped('line_ids')
                    reconcile_ids = []
                    if account_move_line_ids:
                        reconcile_ids = account_move_line_ids.sudo().mapped('id')
                    reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                    if reconcile_lines:
                        reconcile_lines.sudo().unlink()
                    account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                    account_move.sudo().write({'state':'draft','name':'/'})
                    account_move.sudo().with_context({'force_delete':True}).unlink()
                    
                    # cancel stock valuation
                    stock_valuation_layer_ids = rec.sudo().mapped('move_ids_without_package').sudo().mapped('stock_valuation_layer_ids')
                    if stock_valuation_layer_ids:
                        stock_valuation_layer_ids.sudo().unlink()

                rec.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().unlink()
                rec.sudo().mapped('move_ids_without_package').sudo().unlink()
            rec.sudo().write({'state': 'draft', 'show_mark_as_todo': True})
            rec.sudo().unlink()

    def _sh_unreseve_qty(self):
        print(">>>>>>>>>>",self.state)
        if self.state != 'done':
            self.do_unreserve()


        for move_line in self.sudo().mapped('move_ids_without_package').mapped('move_line_ids'):
            # unreserve qty
            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity + move_line.qty_done})
            else:
                self.env['stock.quant'].sudo().create({'location_id': move_line.location_id.id,
                                                       'product_id': move_line.product_id.id,
                                                       'lot_id':move_line.lot_id.id,
                                                       'quantity':move_line.qty_done
                                                       })

            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity - move_line.qty_done})
            else:
                self.env['stock.quant'].sudo().create({'location_id': move_line.location_dest_id.id,
                                                       'product_id': move_line.product_id.id,
                                                       'lot_id':move_line.lot_id.id,
                                                       'quantity':move_line.qty_done * (-1)
                                                       })

    def sh_cancel(self):

        if self.company_id.picking_operation_type == 'cancel':
            # cancel packages
            if self.move_line_ids.mapped('result_package_id'):
                packages = self.move_line_ids.mapped('result_package_id')
                if packages:
                    packages.unpack()
                
            if self.package_level_ids_details:
                self.package_level_ids_details.sudo().unlink()

            if self.sudo().mapped('move_ids_without_package'):
                self._sh_unreseve_qty()
                self.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'cancel'})
                self.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                

                if self._check_stock_account_installed():
                    # cancel related accouting entries
                    account_move = self.sudo().mapped('move_ids_without_package').sudo().mapped('account_move_ids')
                    account_move_line_ids = account_move.sudo().mapped('line_ids')
                    reconcile_ids = []
                    if account_move_line_ids:
                        reconcile_ids = account_move_line_ids.sudo().mapped('id')
                    reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                    if reconcile_lines:
                        reconcile_lines.sudo().unlink()
                    account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                    account_move.sudo().write({'state':'draft','name':'/'})
                    account_move.sudo().with_context({'force_delete':True}).unlink()
                    
                    # cancel stock valuation
                    stock_valuation_layer_ids = self.sudo().mapped('move_ids_without_package').sudo().mapped('stock_valuation_layer_ids')
                    if stock_valuation_layer_ids:
                        stock_valuation_layer_ids.sudo().unlink()

            self.sudo().write({'state': 'cancel'})

        elif self.company_id.picking_operation_type == 'cancel_delete':
            # cancel packages
            if self.move_line_ids.mapped('result_package_id'):
                packages = self.move_line_ids.mapped('result_package_id')
                if packages:
                    packages.unpack()
                
            if self.package_level_ids_details:
                self.package_level_ids_details.sudo().unlink()

            if self.sudo().mapped('move_ids_without_package'):
                self.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self._sh_unreseve_qty()

                if self._check_stock_account_installed():
                    # cancel related accouting entries
                    account_move = self.sudo().mapped('move_ids_without_package').sudo().mapped('account_move_ids')
                    account_move_line_ids = account_move.sudo().mapped('line_ids')
                    reconcile_ids = []
                    if account_move_line_ids:
                        reconcile_ids = account_move_line_ids.sudo().mapped('id')
                    reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                    if reconcile_lines:
                        reconcile_lines.sudo().unlink()
                    account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                    account_move.sudo().write({'state':'draft','name':'/'})
                    account_move.sudo().with_context({'force_delete':True}).unlink()
                    
                    # cancel stock valuation
                    stock_valuation_layer_ids = self.sudo().mapped('move_ids_without_package').sudo().mapped('stock_valuation_layer_ids')
                    if stock_valuation_layer_ids:
                        stock_valuation_layer_ids.sudo().unlink()

                self.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().unlink()
                self.sudo().mapped('move_ids_without_package').sudo().unlink()
            self.sudo().write({'state': 'draft', 'show_mark_as_todo': True})
            self.sudo().unlink()

            return {
                'name': 'Inventory Transfer',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'target': 'current',
            }


        elif self.company_id.picking_operation_type == 'cancel_draft':
            # cancel packages
            if self.move_line_ids.mapped('result_package_id'):
                packages = self.move_line_ids.mapped('result_package_id')
                if packages:
                    packages.unpack()
                
            if self.package_level_ids_details:
                self.package_level_ids_details.sudo().unlink()
                
            if self.sudo().mapped('move_ids_without_package'):
                self.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self._sh_unreseve_qty()

                if self._check_stock_account_installed():
                    # cancel related accouting entries
                    account_move = self.sudo().mapped('move_ids_without_package').sudo().mapped('account_move_ids')
                    account_move_line_ids = account_move.sudo().mapped('line_ids')
                    reconcile_ids = []
                    if account_move_line_ids:
                        reconcile_ids = account_move_line_ids.sudo().mapped('id')
                    reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                    if reconcile_lines:
                        reconcile_lines.sudo().unlink()
                    account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                    account_move.sudo().write({'state':'draft','name':'/'})
                    account_move.sudo().with_context({'force_delete':True}).unlink()
                    
                    # cancel stock valuation
                    stock_valuation_layer_ids = self.sudo().mapped('move_ids_without_package').sudo().mapped('stock_valuation_layer_ids')
                    if stock_valuation_layer_ids:
                        stock_valuation_layer_ids.sudo().unlink()
                        
            self.sudo().write({'state': 'draft'})
