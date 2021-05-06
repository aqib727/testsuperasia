# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from .eshipper_provider import eShipperProvider
from odoo.exceptions import UserError, Warning


class ProvidereShipper(models.Model):
    
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('eshipper', "eShipper")])
    eshipper_username = fields.Char(string='eShipper Username', groups=False)
    eshipper_passwd = fields.Char(string='eShipper Password', groups=False)
    eshipper_default_packaging_id = fields.Many2one('product.packaging', string='Default Packaging Type', domain=[('package_carrier_type','=','eshipper')])
    service_id = fields.Char("Service ID")
    country_of_origin = fields.Char("country of origin")
    is_default_eshipper_services = fields.Boolean(default=False)

    def update_eshipper_data(self):
        if self.delivery_type == 'eshipper':
            eshipper_ids = self.search([('delivery_type', '=', 'eshipper'), ('id', '!=', self.id), ('company_id', '=', self.company_id.id)])
            eshipper_ids.write({
                'eshipper_username':self.eshipper_username,
                'eshipper_passwd':self.eshipper_passwd,
            })

    def active_new_services(self):
        self.ensure_one()
        if self.delivery_type == 'eshipper':
            return {
                'name': _('eShipper Services'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'delivery.carrier',
                'view_id': self.env.ref('delivery_eshipper.view_delivery_carrier_eshipper_tree').id,
                'domain':[('active','=',False),('delivery_type','=','eshipper')],
        }

    def eshipper_cancel_shipment(self, pickings):
        self.ensure_one()
        default_eshipper = self.sudo().search([('is_default_eshipper_services','=',True)],limit=1)
        prod_environment = 'production'
        if not default_eshipper.prod_environment:
            prod_environment = 'sandbox'
        
        if not default_eshipper.eshipper_username or not default_eshipper.eshipper_passwd:
            raise Warning('Missing eShipper Credentials. Please configure first.')
        srm = eShipperProvider(self.log_xml, prod_environment, default_eshipper.sudo().eshipper_username,
                                 default_eshipper.sudo().eshipper_passwd)
        for picking in pickings:
            if picking.eshipper_order_id:
                result = srm.cancel_request(picking.eshipper_order_id)
                picking.write({
                    'eshipper_order_id':False,
                    'eshipper_tracking_url':False,
                })
        
        return True
            
    def eshipper_rate_shipment(self, order):
        prod_environment = 'production'
        default_eshipper = self.search([('is_default_eshipper_services','=',True)],limit=1)
        if not default_eshipper.prod_environment:
            prod_environment = 'sandbox'
        
        if not default_eshipper.eshipper_username or not default_eshipper.eshipper_passwd:
            raise Warning('Missing eShipper Credentials. Please configure first.')
        srm = eShipperProvider(self.log_xml, prod_environment, default_eshipper.sudo().eshipper_username,
                                 default_eshipper.sudo().eshipper_passwd)
        check_value = srm.check_required_value(order.partner_shipping_id,order.warehouse_id.partner_id, order=order)
        if check_value:
            return {
                'success': False,
                'price': 0.0,
                'error_message': check_value,
                'warning_message': False
            }
        result = srm.rate_request(order, self)
        if result.get('error_found'):
            return {
                'success': False,
                'price': 0.0,
                'error_message': result['error_found'],
                'warning_message': False
            }

        if order.currency_id.name == result['currency']:
            price = float(result['price'])
        else:
            quote_currency = self.env['res.currency'].search(
                [('name', '=', result['currency'])], limit=1)
            price = quote_currency.compute(
                float(result['price']), order.currency_id)

        if not price:
            return {
                'success': False,
                'price': 0.0,
                'error_message': "Selected service is not valid for your location.",
                'warning_message': False
            }
        return {
            'success': True,
            'price': price,
            'error_message': False,
            'warning_message': False
        }

    def eshipper_send_shipping(self, pickings):
        res = []
        prod_environment = 'production'
        default_eshipper = self.sudo().search([('is_default_eshipper_services','=',True)],limit=1)
        if not default_eshipper.prod_environment:
            prod_environment = 'sandbox'
        
        if not default_eshipper.eshipper_username or not default_eshipper.eshipper_passwd:
            raise Warning('Missing eShipper Credentials. Please configure first.')
        srm = eShipperProvider(self.log_xml, prod_environment, default_eshipper.sudo().eshipper_username,
                                 default_eshipper.sudo().eshipper_passwd)
        for picking in pickings:
            shipping = srm.send_shipping(picking, self)
            tracking_number_ref = []
            order_currency = picking.sale_id.currency_id or picking.company_id.currency_id
            label_attached = False
            for each_shipping in shipping:
                if order_currency.name == each_shipping['currency']:
                    carrier_price = float(each_shipping['price'])
                else:
                    quote_currency = self.env['res.currency'].search(
                        [('name', '=', each_shipping['currency'])], limit=1)
                    carrier_price = quote_currency.compute(float(each_shipping['price']), order_currency)
                tracking_number_ref.append(each_shipping['tracking_number'])
                
                shipping_data = {
                    'exact_price': carrier_price,
                    'tracking_number': each_shipping['tracking_number'],
                    'eshipper_tracking_url':each_shipping.get('tracking_url'),
                    'eshipper_order_id':each_shipping.get('order_id'),
                }
                if not label_attached:
                    shipping_data['label_data'] = each_shipping.get('label' , '')
                    label_attached = True
                
                res += [shipping_data]
            logmessage = (_("Shipment created into eShipper <br/> <b>Tracking Number : </b>%s <br/> <b>Cost : </b>%.2f %s ") % (','.join(map(str, tracking_number_ref)), carrier_price, order_currency.name))
            picking.message_post(body=logmessage)
        return res

    def unlink(self):
        eshipper_default = self.env.ref('delivery_eshipper.delivery_carrier_eshipper_default')
        if eshipper_default.id in self.ids:
            raise Warning('You cannot remove default eshipper delivery method')
        eshipper_services = self.filtered(lambda x : x.delivery_type == 'eshipper')
        eshipper_services.write({'active':False})
        self = self - eshipper_services       
        return super(ProvidereShipper, self).unlink()
