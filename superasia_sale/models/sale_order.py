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
            partner, prod, salesperson = '', '', False
            order_id = line.get('orderID')

            # Find product by SKU, partner by customer id, rep by name
            if line.get('sku'):
                prod = self.env['product.product'].search([('default_code', '=', line.get('sku'))], limit=1)

            # Only set sales person and partner once
            if order_id and order_id not in orders:
                if line.get('customer_id'):
                    partner = self.env['res.partner'].search([('handshake_id', '=', line.get('customer_id'))], limit=1)
                # Don't need to log error, set salesperson to odoobot if none found
                if line.get('rep'):
                    salesperson = self.env['res.users'].search([('name', '=', line.get('rep'))], limit=1)
            elif not order_id:
                _logger.error("Order ID is not in file: '%s' order not imported",
                              line.get('orderID'))

            if prod and order_id:
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
                        'customer': partner.id if partner else False,
                        'salesperson': salesperson.id if salesperson else False,
                    }
            elif not prod:
                _logger.error("Failed to find product with '%s' ID: order %s not imported",
                              line.get('sku'), line.get('orderID'))

        for order in orders:
            # Check to make sure the order is unique
            existing_order = self.env['sale.order'].search([('handshake_order_id', '=', order)])
            partner = orders[order].get('customer')

            if not existing_order and partner:
                sale_order_id = self.env['sale.order'].create([{
                    'partner_id': partner,
                    'order_line': orders[order].get('order_lines'),
                    'handshake_order_id': order,
                    'user_id': orders[order].get('salesperson'),
                }])
                sale_order_ids += sale_order_id
            elif not partner:
                _logger.error("Failed to find customer with '%s' ID or it does not exist: order %s not imported",
                              partner, order)

        return sale_order_ids

    def import_orders_handshake(self):
        folder_id = self.env['ir.config_parameter'].sudo().get_param('superasia_sale.google_drive_order_folder_id')
        # Use google drive model to get call info
        # Returns list(orders) of list(order) of dictionaries(rows)
        orders_data = self.env['google.drive.config'].get_handshake_drive_orders(folder_id)
        for order in orders_data:
            sale_ids = self.create_handshake_order(order)
        return True
