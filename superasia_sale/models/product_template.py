# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import csv

from odoo import api, fields, models, _
from datetime import datetime, timedelta

from tempfile import TemporaryDirectory


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def create_product_csv_data(self, product_ids):
        rows = []
        for prod in product_ids:
            rows.append({
                'Name': prod.name or '',
                'Internal Reference': prod.default_code or '',
                'Description': prod.description or '',
                'Price': prod.list_price or '',
            })
        return rows

    def create_inventory_csv_data(self, product_ids):
        rows = []
        warehouse_ids = self.env['stock.warehouse'].search([])

        for prod in product_ids:
            for wh in warehouse_ids:
                prod.invalidate_cache()
                amount = prod.sudo().with_context(allowed_company_ids=[wh.company_id.id], warehouse=wh.id).qty_available
                rows.append({
                    'sku': prod.name or '',
                    'type': prod.type or '',
                    'shelfQty': amount or 0.0,
                    'warehouseId': wh.name or '',
                })
        return rows

    def export_product_handshake(self):
        product_ids = self.env['product.template'].search([])

        inv_filename = "inventory_%s.%s" % (datetime.now().strftime("%Y_%m_%d"), "csv")
        prod_filename = "products_%s.%s" % (datetime.now().strftime("%Y_%m_%d"), "csv")

        with TemporaryDirectory() as temp_dir:
            inv_file_path = temp_dir + '/' + inv_filename
            prod_file_path = temp_dir + '/' + prod_filename

            inv_folder_id = self.env['ir.config_parameter'].sudo().get_param(
                'superasia_sale.google_drive_inventory_folder_id')
            prod_folder_id = self.env['ir.config_parameter'].sudo().get_param(
                'superasia_sale.google_drive_product_folder_id')

            if inv_folder_id:
                with open(inv_file_path, mode='w') as handshake_file:
                    fieldnames = ['sku', 'type', 'shelfQty', 'warehouseId']
                    writer = csv.DictWriter(handshake_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.create_inventory_csv_data(product_ids))

                uploaded_inv = self.env['google.drive.config'].push_handshake_drive_files(inv_folder_id, inv_file_path, inv_filename)

            if prod_folder_id:
                with open(prod_file_path, mode='w') as handshake_file:
                    fieldnames = ['Name', 'Internal Reference', 'Description', 'Price']
                    writer = csv.DictWriter(handshake_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.create_product_csv_data(product_ids))

                uploaded_prod = self.env['google.drive.config'].push_handshake_drive_files(prod_folder_id, prod_file_path, prod_filename)
