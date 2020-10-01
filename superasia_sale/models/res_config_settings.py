# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    google_drive_product_folder = fields.Char(string='Product Folder', config_parameter='superasia_sale.google_drive_product_folder')
    google_drive_inventory_folder = fields.Char(string='Inventory Folder', config_parameter='superasia_sale.google_drive_inventory_folder')
    google_drive_contact_folder = fields.Char(string='Contact Folder', config_parameter='superasia_sale.google_drive_contact_folder')
    google_drive_order_folder = fields.Char(string='Sale Order Folder', config_parameter='superasia_sale.google_drive_order_folder')

    google_drive_product_folder_id = fields.Char(string='Product Folder ID', compute='_google_drive_folder_id', config_parameter='superasia_sale.google_drive_product_folder_id')
    google_drive_inventory_folder_id = fields.Char(string='Inventory Folder ID', compute='_google_drive_folder_id', config_parameter='superasia_sale.google_drive_inventory_folder_id')
    google_drive_contact_folder_id = fields.Char(string='Contact Folder ID', compute='_google_drive_folder_id', config_parameter='superasia_sale.google_drive_contact_folder_id')
    google_drive_order_folder_id = fields.Char(string='Sale Order Folder ID', compute='_google_drive_folder_id', config_parameter='superasia_sale.google_drive_order_folder_id')

    @api.depends('google_drive_product_folder', 'google_drive_inventory_folder', 'google_drive_contact_folder', 'google_drive_order_folder')
    def _google_drive_folder_id(self):
        for config in self:
            config.google_drive_product_folder_id = self.env['google.drive.config'].get_drive_folder_id(
                config.google_drive_product_folder)
            config.google_drive_inventory_folder_id = self.env['google.drive.config'].get_drive_folder_id(
                config.google_drive_inventory_folder)
            config.google_drive_contact_folder_id = self.env['google.drive.config'].get_drive_folder_id(
                config.google_drive_contact_folder)
            config.google_drive_order_folder_id = self.env['google.drive.config'].get_drive_folder_id(
                config.google_drive_order_folder)
