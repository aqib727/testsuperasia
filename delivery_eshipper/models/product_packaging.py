# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductPackaging(models.Model):
    
    _inherit = 'product.packaging'

    package_carrier_type = fields.Selection(selection_add=[('eshipper', 'eShipper')])
