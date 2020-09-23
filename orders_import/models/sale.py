# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    import_order_id = fields.Char('Order ID')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    note = fields.Text(string='Note')