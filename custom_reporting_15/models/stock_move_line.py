from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # def _getIdInventory(self):
    #     for data in self:
    #         id_inventory = ''
    #         arr = []
    #         for package in data.result_package_id:
    #             for quant in package.quant_ids:
    #                 if quant.id_inventory:
    #                     arr.append(quant.id_inventory)
            
    #         if arr:
    #             id_inventory = ', '.join(arr)
    #         data.id_inventory = id_inventory
    
    def _getPalet(self):
        for data in self:
            location = []
            location = data.location_id.name.split("/") if data.location_id else None
            if len(location) > 1:
                value = str(location[-1])
            else:
                value = str(location[0])
            data.palet = value
    
    def _getGudang(self):
        for data in self:
            location = []
            location = data.location_id.location_id.name.split("/") if data.location_id.location_id else data.location_id
            if len(location) > 1:
                value = str(location[-2])
            else:
                value = str(location[0])
            data.gudang = value
    
    def _get_bag_qty(self):
        for rec in self:
            rec.bag_qty = 0
            qty = 0
            if rec.product_id.pcs_per_bag_ratio: 
                if rec.sh_sec_qty and rec.sh_sec_uom.name == 'Pcs':
                    qty = rec.sh_sec_qty/rec.product_id.pcs_per_bag_ratio
                else:
                    qty = rec.qty_done/rec.product_id.pcs_per_bag_ratio
            rec.bag_qty = qty

    # id_inventory = fields.Char(string="ID Inventory", compute=_getIdInventory)
    gudang = fields.Char(string="Gudang", compute=_getGudang)
    palet = fields.Char(string="Palet", compute=_getPalet)
    # bag_qty = fields.Float(string="Bag")
    bag_qty = fields.Float(string="Bag", compute=_get_bag_qty)