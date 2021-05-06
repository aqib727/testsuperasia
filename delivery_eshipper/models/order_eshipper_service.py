# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from .eshipper_provider import eShipperProvider
from odoo.exceptions import UserError


class OrdereShipperService(models.Model):
    
    _name = 'order.eshipper.service'
    _description = "Shipping Quote"
    _rec_name = 'carrier_id'

    order_id = fields.Many2one('sale.order',string="Sales Order")
    service_name = fields.Char("Service")
    carrier_name = fields.Char("Carrier")
    carrier_id = fields.Many2one('delivery.carrier',string="Carrier")
    total_charge = fields.Float(string="Total Charges")
    transit_days = fields.Float(string="Transit Days")
    fulecharge = fields.Float(string='Fuel Charge')
    basecharge = fields.Float(string='Base Charge')
    
    def set_order_delivery_method(self):
        self.ensure_one()
        if self.order_id.state not in ('draft', 'sent'):
            raise UserError(_('You can add delivery price only on unconfirmed quotations.'))
        self.flush()
        # Remove delivery products from the sales order
        self.order_id._remove_delivery_line()
        self.order_id.write({
        	'carrier_id':self.carrier_id.id,
        	'delivery_rating_success':True,
        })
        if not self.order_id.carrier_id:
            raise UserError(_('No carrier set for this order.'))
        elif not self.order_id.delivery_rating_success:
            raise UserError(_('Please use "Check price" in order to compute a shipping price for this quotation.'))
        else:
            price_unit = self.total_charge
            # TODO check whether it is safe to use delivery_price here
            self.order_id._create_delivery_line(self.carrier_id, price_unit)
        return True
