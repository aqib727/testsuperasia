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

    def read_order_csv(self, filepath):
        with open(filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data_lines = list(reader)
        return data_lines

    def import_orders_handshake(self):
        filepath = '/home/cindey/odoo_git/super_asia/template_sample.csv'

        data = self.read_order_csv(filepath)
        order = self.create_handshake_order(data)
        print("hello")
        return True
