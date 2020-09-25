# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class StockPackOperation(models.Model):
    _inherit = 'stock.move.line'

    @api.model
    def _compute_operation_valid(self):
        res = True
        if hasattr(super(StockPackOperation, self), '_compute_operation_valid'):
            res &= super(StockPackOperation, self)._compute_operation_valid()
        res &= self.qty_done != self.product_qty
        # res &= self.state not in ('draft', 'cancel', 'done')
        return res
