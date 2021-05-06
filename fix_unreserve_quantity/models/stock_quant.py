# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def check_stock_quant(self):
        for quant in records:
            prd_moves = env['stock.move.line'].sudo().search(
                [('product_id', '=', quant.product_id.id),
                 '|', ('location_id', '=', quant.location_id.id),
                 ('location_dest_id', '=', quant.location_id.id), ('state', 'in',
                                                                   ['waiting',
                                                                    'confirmed',
                                                                    'partially_available',
                                                                    'assigned'])])
            sum_reserved_qty = sum(prd_moves.mapped('product_uom_qty'))
            # log("Poduct MOves---> %s ANDsum_reserved_qty---> %s"%( prd_moves, sum_reserved_qty), level='info')
            # a = str(prd_moves)+str(sum_reserved_qty)
            # raise Warning(a)
            quant.sudo().write({'reserved_quantity': sum_reserved_qty})
