# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from datetime import date, datetime, timedelta, time
from odoo.exceptions import UserError
import base64
import xlrd
import json

class CreateSJWizard(models.TransientModel):
    _name = "create.sj.wizard"
    _description = "Create Surat Jalan Wizard"

    def _default_sale_order(self):
        if self.env.context["active_model"] == "sale.order.line":
            return (
                self.env["sale.order.line"]
                .browse(self.env.context["active_ids"][0])
                .order_id
            )
        return self.env["sale.order"].browse(self.env.context["active_id"])

    def _default_location_dest_id(self):
        return self.env["stock.location"].browse(
            self._default_sale_order()._get_destination_location()
        )

    @api.model
    def default_get(self, fields):
        res = super(CreateSJWizard, self).default_get(fields)

        active_model = self.env.context["active_model"]
        if active_model == "sale.order.line":
            so_line_ids = self.env.context["active_ids"] or []
            sale_lines = (
                self.env["sale.order.line"]
                .browse(so_line_ids)
                .filtered(
                    lambda p: p.product_id.type in ["product", "consu"]
                    and p.qty_to_deliver
                )
            )
        elif active_model == "sale.order":
            po_ids = self.env.context["active_ids"] or []
            sale_lines = (
                self.env["sale.order"]
                .browse(po_ids)
                .mapped("order_line")
                .filtered(
                    lambda p: p.product_id.type in ["product", "consu"]
                    and p.qty_to_deliver
                )
            )
        self._check_sale_line_constrains(sale_lines)
        res["line_ids"] = self.fill_lines(sale_lines)
        res["partner_id"] = sale_lines.mapped("order_id.partner_id").id
        return res

    def _check_sale_line_constrains(self, sale_lines):
        if len(sale_lines.mapped("order_id.partner_id")) > 1:
            raise UserError(_("Please select one partner at a time"))
        if len(sale_lines.mapped("order_id")) > 1:
            raise UserError(_("Please select one sale order at a time"))

    def fill_lines(self, so_lines):
        lines = [
            (
                0,
                0,
                {
                    "sale_order_line_id": line.id,
                    "name": line.name,
                    "product_id": line.product_id.id,
                    "price_unit": line.price_unit,
                    "product_uom_qty": line.product_uom_qty,
                    "qty": 0, 
                },
            )
            for line in so_lines
        ]
        return lines
    
    # @api.model
    # def _default_warehouse_id(self):
    #     # !!! Any change to the default value may have to be repercuted
    #     # on _init_column() below.
    #     return self.env.user._get_default_warehouse_id()

    sale_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        readonly=True,
        default=_default_sale_order,
    )
    line_ids = fields.One2many(
        comodel_name="create.sj.wizard.line",
        inverse_name="wizard_id",
        string="Lines",
    )
    partner_id = fields.Many2one("res.partner", "Customer")
    partner_domain = fields.Char(compute='_domain_partner_id', readonly=True, store=False,)

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True,
        #default=_default_warehouse_id, 
        check_company=True)
    
    company_id = fields.Many2one("res.company", related="sale_id.company_id")
    
    @api.depends('partner_id', )
    def _domain_partner_id(self):
        for rec in self:
            if rec.sale_id.partner_id:
                if rec.sale_id.partner_id.parent_id:
                    domain = ['|',('id','=',rec.sale_id.partner_id.parent_id.id), ('parent_id','=',rec.sale_id.partner_id.parent_id.id)]
                else:
                    domain = ['|',('id','=',rec.sale_id.partner_id.id), ('parent_id','=',rec.sale_id.partner_id.id)]
                    # domain = ['|',('id','=',rec.sale_id.partner_id.id), ('parent_id','=',rec.sale_id.partner_id.id), ('type','=','delivery')]
            else:
                domain = []
                        
            rec.partner_domain = json.dumps(domain)

    def _get_procurement_group(self):
        return self.sale_id.procurement_group_id

    def _prepare_procurement_group_vals(self):
        return {
            'name': self.sale_id.name,
            'move_type': self.sale_id.picking_policy,
            'sale_id': self.sale_id.id,
            'partner_id': self.partner_id.id,
        }
    
    def _get_destination_location(self):
        self.ensure_one()
        if self.partner_id:
            return self.partner_id.property_stock_customer.id
        return self.warehouse_id.out_type_id.default_location_dest_id.id

    def _prepare_picking(self):
        # res = self.sale_id._prepare_picking()
        # if self.partner_id:
        #     res["partner_id"] = self.partner_id.id
        # # if self.supplier_pli_number:
        # #     res["surat_jalan"] = self.supplier_pli_number
        # return res
    
        group_id = self._get_procurement_group()

        if not group_id:
            group_id = self.env['procurement.group'].create(self._prepare_procurement_group_vals())
            self.sale_id.procurement_group_id = group_id
        else:
            # In case the procurement group is already created and the order was
            # cancelled, we need to update certain values of the group.
            updated_vals = {}
            if group_id.partner_id != self.partner_id:
                updated_vals.update({'partner_id': self.partner_id.id})
            if group_id.move_type != self.sale_id.picking_policy:
                updated_vals.update({'move_type': self.sale_id.picking_policy})
            if updated_vals:
                group_id.write(updated_vals)
        
        print("group_id", group_id)

        # wh = self.sale_id.warehouse_id
        wh = self.warehouse_id
    
        picking_type = wh.out_type_id
        if not picking_type:
            raise UserError(_('SJ Opr. Type NOT_DEFINED.'))
        else:
            src_loc_id = picking_type.default_location_src_id.id
            picking_type_id = picking_type.id
            
        values = {
            'sale_id': self.sale_id.id,
            'group_id': group_id.id,
            'picking_type_id': picking_type_id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': datetime.now(),
            'origin': self.sale_id.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': src_loc_id,
            'company_id': self.sale_id.company_id.id,
        }
        return values

    def _create_stock_moves(self, picking_id):
        return self.line_ids._create_stock_moves(picking_id)

    def create_sj(self):
        # Check quantity is not above remaining quantity
        if any(line.qty > line.remaining_qty for line in self.line_ids):
            raise UserError(
                _(
                    "You can not create SJ more than the remaining "
                    "quantity. If you need to do so, please edit "
                    "the sale order first."
                )
            )
        
        qty = 0
        for line in self.line_ids:
            qty += line.qty

        if not qty:
            raise UserError(
                _(
                    "Qty masih 0, tidak bisa membuat picking tanpa mengisi qty terlebih dulu."
                )
            )

        StockPicking = self.env["stock.picking"]
        res = self._prepare_picking()
        picking_id = StockPicking.create(res)
        moves = self._create_stock_moves(picking_id)
        moves = moves.filtered(
            lambda x: x.state not in ("done", "cancel")
        )._action_confirm()
        moves._action_assign()
        picking_id.message_post_with_view(
            "mail.message_origin_link",
            values={"self": picking_id, "origin": self.sale_id},
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        self.sale_id.write({'picking_ids': [(4, picking_id.id, _)]})
        # picking_id.sh_cancel()
    
class CreateSJWizardLine(models.TransientModel):
    _name = "create.sj.wizard.line"
    _description = "Create Surat Jalan Wizard Line"

    wizard_id = fields.Many2one(
        string="Wizard",
        comodel_name="create.sj.wizard",
        required=True,
        ondelete="cascade",
    )
    sale_order_line_id = fields.Many2one("sale.order.line")
    name = fields.Text(string="Description", readonly=True)
    product_id = fields.Many2one(
        "product.product",
        related="sale_order_line_id.product_id",
        string="Product",
    )
    product_uom = fields.Many2one(
        "uom.uom",
        related="sale_order_line_id.product_uom",
        string="Unit of Measure",
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        related="sale_order_line_id.product_uom_qty",
        digits="Product Unit of Measure",
    )
    qty_waiting_deliver = fields.Float(
        string="In Delivery Quantity",
        related="sale_order_line_id.qty_waiting_deliver",
        digits="Product Unit of Measure",
    )
    qty_delivered = fields.Float(
        string="Delivered Quantity",
        related="sale_order_line_id.qty_delivered",
        digits="Product Unit of Measure",
    )
    remaining_qty = fields.Float(
        string="Remaining Quantity",
        compute="_compute_remaining_qty",
        readonly=True,
        digits="Product Unit of Measure",
    )
    qty = fields.Float(
        string="Quantity to Deliver",
        digits="Product Unit of Measure",
        help="This is the quantity taken into account to create the picking",
    )
    price_unit = fields.Float(
        related="sale_order_line_id.price_unit", readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="sale_order_line_id.currency_id"
    )
    partner_id = fields.Many2one(
        "res.partner", related="sale_order_line_id.address_cust_m2o", string="Customer",
    )
    tax_id = fields.Many2many(
        "account.tax", related="sale_order_line_id.tax_id"
    )
    
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = (
                line.product_uom_qty - line.qty_waiting_deliver
            )

    def _get_procurement_group(self):
        return self.sale_order_line_id.order_id.procurement_group_id

    def _prepare_procurement_group_vals(self):
        return {
            'name': self.sale_order_line_id.order_id.name,
            'move_type': self.sale_order_line_id.order_id.picking_policy,
            'sale_id': self.sale_order_line_id.order_id.id,
            'partner_id': self.partner_id.id,
        }
    
    def _prepare_stock_moves(self, picking):
        for rec in self:
            group_id = self._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(self._prepare_procurement_group_vals())
                self.sale_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != self.partner_id:
                    updated_vals.update({'partner_id': self.partner_id.id})
                if group_id.move_type != self.sale_order_line_id.order_id.picking_policy:
                    updated_vals.update({'move_type': self.sale_order_line_id.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)
            
            print("group_id", group_id)
            
            values = {}
            if rec.qty:
                print(picking.sale_id.commitment_date, picking.sale_id.date_order, rec.sale_order_line_id.customer_lead, group_id)
                date_deadline = picking.sale_id.commitment_date or (picking.sale_id.date_order + timedelta(days=rec.sale_order_line_id.customer_lead or 0.0))
                values = {
                        'sale_line_id': rec.sale_order_line_id.id,
                        'partner_id': picking.partner_id.id,
                        'group_id': group_id.id,
                        'warehouse_id': picking.sale_id.warehouse_id.id,
                        'picking_id': picking.id,
                        'origin': picking.origin,
                        'date': picking.scheduled_date,
                        'date_deadline': date_deadline,
                        'picking_type_id': picking.picking_type_id.id,
                        'location_id': picking.location_id.id,
                        'location_dest_id': picking.location_dest_id.id,
                        'name': rec.sale_order_line_id.product_id.name,
                        'description_picking': rec.sale_order_line_id.product_id.name,
                        'product_id': rec.sale_order_line_id.product_id.id,
                        'product_uom_qty': rec.qty,
                        'product_uom': rec.product_uom.id,
                        'price_unit': rec.price_unit or 0.0,
                        'state': 'draft',
                }
            print("fsfsdsd", values)
        return values

    def _create_stock_moves(self, picking):
        values = []
        for line in self:
            data = line._prepare_stock_moves(picking)
            if data:
                data["product_uom_qty"] = line.product_uom._compute_quantity(
                    line.qty, line.product_uom, rounding_method="HALF-UP"
                )
                values.append(data)
        return self.env["stock.move"].create(values)
