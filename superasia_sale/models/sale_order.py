# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import csv
import logging

from odoo import api, fields, models, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    handshake_order_id = fields.Char(string='Handshake Order ID')

    def create_handshake_order(self, data):
        orders = {}
        sale_order_ids = []
        for line in data:
            # Find product by SKU, partner by customer id
            partner = self.env['res.partner'].search([('handshake_id', '=', line['customer_id'])], limit=1)
            prod = self.env['product.product'].search([('default_code', '=', line['sku'])], limit=1)
            order_id = line.get('orderID')

            if prod and partner:
                values = {
                    'product_id': prod.id,
                    'product_uom_qty': line.get('qty'),
                    'price_unit': line.get('unit_price'),
                    'name': line.get('description'),
                }
                # Build the order dictionary, key = order id
                if orders.get(order_id):
                    orders[order_id]['order_lines'].append((0, 0, values))
                else:
                    orders[order_id] = {
                        'order_lines': [(0, 0, values)],
                        'customer': partner.id,
                    }
            elif not prod:
                _logger.error("Failed to find product with '%s' ID: order %s not imported",
                              line['customer_id'], line['orderID'])
            elif not partner:
                _logger.error("Failed to find customer with '%s' ID: order %s not imported",
                              line['customer_id'], line['orderID'])

        for order in orders:
            # Check to make sure the order is unique
            existing_order = self.env['sale.order'].search([('handshake_order_id', '=', order)])

            if not existing_order:
                sale_order_id = self.env['sale.order'].create([{
                    'partner_id': orders[order].get('customer'),
                    'order_line': orders[order].get('order_lines'),
                    'handshake_order_id': order,
                }])
                sale_order_ids += sale_order_id

        return sale_order_ids

    def import_orders_handshake(self):
        folder_id = self.env['ir.config_parameter'].sudo().get_param('superasia_sale.google_drive_order_folder_id')
        # Use google drive model to get call info
        # Returns list(orders) of list(order) of dictionaries(rows)
        orders_data = self.env['google.drive.config'].get_handshake_drive_orders(folder_id)
        for order in orders_data:
            sale_ids = self.create_handshake_order(order)
        return True
