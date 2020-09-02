# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    digits = fields.Integer(default=4)
    prefix = fields.Char()
    auto_generate_lot_serial = fields.Boolean(
        string="Auto Generate Lot/Serial Number",
        default=False)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    vendor_id = fields.Many2one(
        'res.partner', 'Vendor',
        help="show vendor in stock quant view.")

    def _update_available_quantity(self, product_id, location_id, quantity,
                                   lot_id=None, package_id=None, owner_id=None,
                                   in_date=None):
        ''' This method set vendor in stock quant view
            if product track by lot/serial number
            and auto generate lot/serial number configation set true.
        '''
        result = super(StockQuant, self)._update_available_quantity(
            product_id, location_id, quantity, lot_id, package_id,
            owner_id, in_date)
        if self.env.user.company_id.auto_generate_lot_serial:
            quants = self.sudo()._gather(
                product_id, location_id, lot_id=lot_id, package_id=package_id,
                owner_id=owner_id, strict=False)
            for quant in quants:
                quant.vendor_id = quant.lot_id.partner_id.id
        return result
