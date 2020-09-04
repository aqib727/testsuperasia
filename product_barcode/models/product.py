# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unit_barcode = fields.Char('Unit Barcode')

    _sql_constraints = [
        ('unit_barcode_uniq', 'unique(unit_barcode)', 'A Unit barcode can only be assigned to one product !')]
