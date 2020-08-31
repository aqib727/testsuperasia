# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import csv

from odoo import api, fields, models, SUPERUSER_ID, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def read_order_csv(self, filepath):
        with open(filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data_lines = list(reader)
        return data_lines

    def import_orders_handshake(self):
        filepath = '/home/cindey/odoo_git/super_asia/template_sample.csv'

        data = self.read_order_csv(filepath)
        print("hello")
        return True
