# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import csv

from odoo import api, fields, models, _
from datetime import datetime, timedelta

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def create_csv_data(self, product_ids):
        rows = []
        for prod in product_ids:
            rows.append({
                'Name': prod.name or '',
                'Internal Reference': prod.default_code or '',
                'Description': prod.description or '',
                'Price': prod.list_price or '',
                'Inventory Count': prod.qty_available or 0.0,
            })

        return rows

    def create_product_csv(self):
        product_ids = self.env['product.template'].search([])

        report_name = 'products_{date}'.format(date=datetime.now().strftime("%Y_%m_%d"))

        filename = "%s.%s" % (report_name, "csv")

        with open('/home/cindey/odoo_git/super_asia/' + filename, mode='w') as broker_file:
            fieldnames = ['Name', 'Internal Reference', 'Description', 'Price', 'Inventory Count']
            writer = csv.DictWriter(broker_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.create_csv_data(product_ids))

    def export_product_handshake(self):
        print("hello")
        self.create_product_csv()
        return True
