# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockLocation(models.Model):
    _name = 'stock.location'
    _inherit = 'stock.location'
    _order = "sequence desc"

    sequence = fields.Integer(string='Sequence')