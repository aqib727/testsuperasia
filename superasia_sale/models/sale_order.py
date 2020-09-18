# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import csv
import logging

from odoo import api, fields, models, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def create_handshake_order(self, data):
        order_lines = []
        for line in data:
            # Find product by SKU
            prod = self.env['product.product'].search([('default_code', '=', line['sku'])], limit=1)
            if prod:
                values = {
                    'product_id': prod.id,
                    'product_uom_qty': line['qty'],
                    'price_unit': line['unitPrice'],
                    'name': line['description'],
                }
                order_lines.append((0, 0, values))

        # partner = self.env['res.partner'].search(['name', '=', line['Customer']])
        # if partner:
        order_id = self.env['sale.order'].create([{
            'partner_id': 19, # Temp id partner,
            'order_line': order_lines,
        }])

        # raise warning if no customer found aka the order was not created
        # else:
        return order_id

    def import_orders_handshake(self):
        folder_id = self.env['ir.config_parameter'].sudo().get_param('superasia_sale.google_drive_order_folder_id')
        # Use google drive model to get call info
        # Returns list(orders) of list(order) of dictionaries(rows)
        orders_data = self.env['google.drive.config'].get_handshake_drive_orders(folder_id)
        for order in orders_data:
            sale_id = self.create_handshake_order(order)
        return True
