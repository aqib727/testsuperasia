# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class StockConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    outgoing_routing_strategy = fields.Selection(
        [
            # path should be valid for both stock pickings and quants
            ('location_id.removal_prio', 'Location removal priority'),
            ('location_id.name', 'Location name'),
            ('product_id.name', 'Product name'),
        ],
        string='Picking Strategy', default='location_id.name',
        related='company_id.outgoing_routing_strategy',
        readonly=False)

    outgoing_routing_order = fields.Selection(
        [
            ('0', 'Ascending (A-Z)'),
            ('1', 'Descending (Z-A)'),
        ],
        string='Picking Order', default='0',
        related='company_id.outgoing_routing_order',
        readonly=False)

    stock_reservation_strategy = fields.Selection(
        [
            ('base', 'Routing Strategy'),
            ('quantity', 'By Quantity'),
            ('none', 'Default'),
        ],
        string='Reservation Strategy', default='base',
        related='company_id.stock_reservation_strategy',
        readonly=False)
