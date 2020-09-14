# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import csv

from odoo import api, fields, models, _
from datetime import datetime, timedelta

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tempfile import TemporaryDirectory
from shutil import copyfile


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
        print(warehouse_ids.name_get())

        for prod in product_ids:
            # print("----------------"+str(prod.name) + "--------------------")
            for wh in warehouse_ids:
                prod.invalidate_cache()
                amount = prod.sudo().with_context(allowed_company_ids=[wh.company_id.id], warehouse=wh.id).qty_available
                # print(str(wh.name) + ": " + str(amount))
                rows.append({
                    'sku': prod.name or '',
                    'type': prod.type or '',
                    'shelfQty': amount or 0.0,
                    'warehouseId': wh.name or '',
                })

        return rows

    def create_product_csv(self):
        product_ids = self.env['product.template'].search([])

        report_name = 'products_{date}'.format(date=datetime.now().strftime("%Y_%m_%d"))

        filename = "%s.%s" % (report_name, "csv")

        with open('/home/cindey/odoo_git/super_asia/' + filename, mode='w') as handshake_file:
            fieldnames = ['Name', 'Internal Reference', 'Description', 'Price']
            writer = csv.DictWriter(handshake_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.create_product_csv_data(product_ids))

    def create_inventory_csv(self):
        product_ids = self.env['product.template'].search([])

        report_name = 'inventory_{date}'.format(date=datetime.now().strftime("%Y_%m_%d"))

        filename = "%s.%s" % (report_name, "csv")

        with open('/home/cindey/odoo_git/super_asia/' + filename, mode='w') as handshake_file:
            fieldnames = ['sku', 'type', 'shelfQty', 'warehouseId']
            writer = csv.DictWriter(handshake_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.create_inventory_csv_data(product_ids))

    def export_product_handshake(self):

        with TemporaryDirectory() as temp_dir:
            copyfile('/home/cindey/odoo_git/super_asia/testsuperasia/superasia_sale/static/src/json/client_secrets.json', temp_dir + 'client_secrets.json')

            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()


            drive = GoogleDrive(gauth)

            file = drive.CreateFile({'title': 'My Awesome File.txt'})
            file.SetContentString('Hello World!')  # this writes a string directly to a file
            file.Upload()

        print("hello")
        self.create_product_csv()
        self.create_inventory_csv()
        return True
