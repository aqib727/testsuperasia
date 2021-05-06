# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):

    _inherit = 'sale.order'
    
    delivery_type = fields.Selection(related='carrier_id.delivery_type')
    eshipper_lines = fields.One2many('order.eshipper.service','order_id',string="eShipper Quotes")
    