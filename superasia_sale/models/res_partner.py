# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import csv

from odoo import api, fields, models, _
from datetime import datetime, timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def create_csv_data(self, partner_ids):
        rows = []
        for partner in partner_ids:
            rows.append({
                'Name': partner.name or '',
                'Street': partner.street or '',
                'Street 2': partner.street2 or '',
                'City': partner.city or '',
                'State': partner.state_id.name or 0.0,
                'Country': partner.country_id.name or '',
                'ZIP': partner.zip or '',
                'Phone': partner.phone or '',
                'Mobile': partner.mobile or '',
                'Email': partner.email or '',
                'Salesperson': partner.user_id.name or '',
                'Payment Term': partner.property_payment_term_id.name or '',
                'Pricelist': partner.property_product_pricelist.name or '',
            })

        return rows

    def create_contact_csv(self):
        partner_ids = self.env['res.partner'].search([])

        report_name = 'contacts_{date}'.format(date=datetime.now().strftime("%Y_%m_%d"))

        filename = "%s.%s" % (report_name, "csv")

        with open('/home/cindey/odoo_git/super_asia/' + filename, mode='w') as broker_file:
            fieldnames = ['Name', 'Street', 'Street 2', 'City', 'State', 'Country', 'ZIP',
                          'Phone', 'Mobile', 'Email', 'Salesperson', 'Payment Term', 'Pricelist']
            writer = csv.DictWriter(broker_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.create_csv_data(partner_ids))

    def export_contact_handshake(self):
        print("hello")
        self.create_contact_csv()
        return True
