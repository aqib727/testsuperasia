# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
import requests
from math import ceil
from xml.etree import ElementTree as etree
import base64
from odoo.exceptions import UserError
from xml.dom.minidom import parseString


class eShipperProvider():

    def __init__(self, debug_logger, prod_environment, username, password):
        # Method used to initiate object of class
        # with required details
        # Need to pass username and password as it differs from client to client
        # URL is fixed #FIXME dynamic URL incase changed by eshipper in future
        self.debug_logger = debug_logger
        self.username = username
        self.password = password
        if prod_environment == 'production':
            self.url = "http://web.eshipper.com/rpc2"
        else:
            self.url = "http://test.eshipper.com/rpc2"

        
    def check_required_value(self, recipient, shipper, order=False, picking=False):
        recipient_required_field = ['city', 'zip', 'country_id']
        if not recipient.street and not recipient.street2:
            recipient_required_field.append('street')
        res = [field for field in recipient_required_field if not recipient[field]]
        if res:
            return _("The address of the customer is missing or wrong (Missing field(s) :\n %s)") % ", ".join(res).replace("_id", "")

        shipper_required_field = ['city', 'zip', 'phone', 'country_id']
        if not shipper.street and not shipper.street2:
            shipper_required_field.append('street')

        res = [field for field in shipper_required_field if not shipper[field]]
        if res:
            return _("The address of your company warehouse is missing or wrong (Missing field(s) :\n %s)") % ", ".join(res).replace("_id", "")

        if order:
            if not order.order_line:
                return _("Please provide at least one item to ship.")
            for line in order.order_line.filtered(lambda line: not line.product_id.weight and not line.is_delivery and line.product_id.type not in ['service', 'digital']):
                return _('The estimated price cannot be computed because the weight of your product is missing.')
        if picking:
            for move in picking.move_lines.filtered(lambda move: not move.product_id.weight):
                return _("The delivery cannot be done because the weight of your product is missing.")
        return False

    def _convert_to_lbs(self, weight_in_kg):
        # weight is accepted in lbs only by eshipper
        return round(weight_in_kg * 2.20462, 3)
    
        
    def _get_rate_param(self, order, carrier):
        packages = []
        res = {}
        total_weight_kg = sum([(line.product_id.weight * line.product_qty) for line in order.order_line.filtered(lambda l:not l.is_delivery)])
        total_weight = self._convert_to_lbs(total_weight_kg)
        res = {
            'serviceId':carrier.service_id,
            'carrier': carrier,
            'from_partner':order.warehouse_id.partner_id,
            'to_partner':order.partner_shipping_id,
            'weight': str(total_weight),
            'currency_name': order.currency_id.name,
        }
        
        max_weight = carrier.eshipper_default_packaging_id.max_weight
        
        if max_weight and total_weight > max_weight:
            total_package = int(total_weight / max_weight)
            last_package_weight = total_weight % max_weight
            res['total_packages'] = total_package
            res['last_package_weight'] = last_package_weight
            res['package_ids'] = carrier.canada_post_default_packaging_id
 
            for seq in range(total_package):
                packages.append(max_weight)
            if last_package_weight:
                packages.append(last_package_weight)
        else:
            packages.append(total_weight)
 
        res['packages'] = packages
    
        return res

    def prepare_root_xml(self):
        etree.register_namespace("", "http://www.eshipper.net/XMLSchema")
        root = etree.Element("EShipper")
        root.set('xmlns',self.url)
        root.set('username',self.username)
        root.set('password',self.password)
        root.set('version','3.0.0')
        return root
    
    def prepare_address_xml(self,node,partner_id,type="From"):
        from_node = etree.SubElement(node,type)
        from_node.set('id',str(partner_id.id))
        name = partner_id.name if not partner_id.parent_id else partner_id.parent_id.name
        from_node.set('company',name)
        from_node.set('attention',partner_id.name)
        from_node.set('address1',partner_id.street or '')
        from_node.set('address2',partner_id.street2 or '')
        from_node.set('city',partner_id.city or '')
        from_node.set('state',partner_id.state_id.code or '')
        from_node.set('country',partner_id.country_id.code or '')
        from_node.set('zip',partner_id.zip or '')
        from_node.set('phone',partner_id.phone or partner_id.mobile or '')
        from_node.set('email',partner_id.email or '')
        return from_node
    
    def prepare_payment_xml(self,node,type="3rd Party"):
        payment_node = etree.SubElement(node,"Payment")
        payment_node.set('type',type)
        return payment_node
    
    def prepare_references_xml(self,node,reference_1=False,reference_2=False,reference_3=False):
        if reference_1:
            ref_1_node = etree.SubElement(node,"Reference")
            ref_1_node.set('name',"OrderReference")
            ref_1_node.set('code',reference_1)
        if reference_2:
            ref_2_node = etree.SubElement(node,"Reference")
            ref_2_node.set('name',"OrderReference")
            ref_2_node.set('code',reference_2)
        if reference_3:
            ref_3_node = etree.SubElement(node,"Reference")
            ref_3_node.set('name',"OrderReference")
            ref_3_node.set('code',reference_3)
        
    def prepare_package_xml(self,node,weight,package):
        package_node = etree.SubElement(node,"Package")
        package_node.set('length',str(package.length))
        package_node.set('width',str(package.width))
        package_node.set('height',str(package.height))
        package_node.set('weight',str(weight))
        package_node.set('type',package.shipper_package_code)
        return package_node
        
    def prepare_packages_xml(self,node,type="Package"):
        packages_node = etree.SubElement(node,"Packages")
        packages_node.set('type',type)
        return packages_node
    
    def _create_rate_xml(self, param):
        root = self.prepare_root_xml()
        
        QuoteRequest = etree.SubElement(root, "QuoteRequest")
        QuoteRequest.set('serviceId',param.get('serviceId'))
        QuoteRequest.set('stackable','true')
        
        self.prepare_address_xml(QuoteRequest,param.get('from_partner'))
        self.prepare_address_xml(QuoteRequest,param.get('to_partner'),type="To")
        
        package_id = param.get('carrier').eshipper_default_packaging_id
        packages_node = self.prepare_packages_xml(QuoteRequest)
        for weight in param.get('packages',[]):
            self.prepare_package_xml(packages_node,weight,package_id)
        
        return etree.tostring(root,encoding='utf8')

    def _send_request(self, request_xml):
        try:
            url_code = self.url
            req = requests.post(url_code, data=request_xml)
            response_text = req.text
        except:
            raise UserError(
                "Problem with connection - Check your connectivity.")
        root = parseString(response_text)
        return root

    def cancel_request(self,order_id):
        root = self.prepare_root_xml()
        CancelRequest_node = etree.SubElement(root, "ShipmentCancelRequest")
        Order_node = etree.SubElement(CancelRequest_node, "Order")
        Order_node.set('orderId',order_id)
        request_text = etree.tostring(root,encoding='utf8')
        root = self._send_request(request_text)
        error_elements = root.getElementsByTagName('Error')
        if error_elements:
            error_message = ''
            for node in error_elements:
                error_message += node.getAttribute('Message')
            if error_message:
                raise UserError(error_message)
        return True

    def rate_request(self, order, carrier):
        response_lst = []
        dict_response = {
            'price': 0.0,
            'currency': False,
            'error_found': False
        }
        param = self._get_rate_param(order, carrier)
        request_text = self._create_rate_xml(param)
        
        try:
            root = self._send_request(request_text)
        except UserError as e:
            dict_response['error_found'] = e.name or e.value
            return dict_response
        
        error_elements = root.getElementsByTagName('Error')
        if error_elements:
            error_message = ''
            for node in error_elements:
                error_message += node.getAttribute('Message')
            dict_response['error_found'] = error_message
            return dict_response
        
        Quotes = root.getElementsByTagName('Quote')
        order.eshipper_lines.sudo().unlink()
        for Quote in Quotes:
            carrier_id = order.env['delivery.carrier'].sudo().with_context({'active_test':False}).search([
                    ('service_id','=', Quote.getAttribute('serviceId')),
                    '|',('company_id','=', order.company_id.id),('company_id','=', False)
                ],limit=1)
            if not carrier_id:
                carrier_id = order.env['delivery.carrier'].sudo().with_context({'active_test':False}).search([
                    ('name','=', Quote.getAttribute('serviceName')),
                    ('service_id','=', ''),
                    '|',('company_id','=', order.company_id.id),('company_id','=', False)
                ],limit=1)
                if not carrier_id:
                    carrier_id = carrier_id.sudo().create({
                        'delivery_type': 'eshipper',
                        'name': Quote.getAttribute('serviceName'),
                        'service_id':Quote.getAttribute('serviceid'),
                        'product_id': carrier.product_id.id,
                        'eshipper_default_packaging_id':carrier.eshipper_default_packaging_id.id,
                        'company_id':  order.company_id.id,
                    })
                else:
                    carrier_id.write({
                        'delivery_type': 'eshipper',
                        'name': Quote.getAttribute('serviceName'),
                        'service_id':Quote.getAttribute('serviceid'),
                        'product_id': carrier.product_id.id,
                        'eshipper_default_packaging_id':carrier.eshipper_default_packaging_id.id,
                        'company_id':  order.company_id.id,
                    })
            quote_line = {
                'order_id':order.id,
                'service_name': Quote.getAttribute('serviceName') or '',
                'carrier_name': Quote.getAttribute('carrierName') or '',
                'carrier_id': carrier_id and carrier_id.id,
                'total_charge': Quote.getAttribute('totalCharge') or 0.0,
                'transit_days': Quote.getAttribute('transitDays') or 0.0,
                'fulecharge': Quote.getAttribute('fuelSurcharge') or 0.0,
                'basecharge': Quote.getAttribute('baseCharge') or 0.0,
            }
            order.env['order.eshipper.service'].sudo().create(quote_line)
                       
        total_charges = Quotes and Quotes[0].getAttribute('totalCharge') or 0.0
        dict_response = {
            'currency': Quotes and Quotes[0].getAttribute('currency') or '',
            'price': float(total_charges)
        }
        response_lst.append(dict_response)
        return dict_response

    def _get_send_param(self, picking, carrier):
        packages = []
        res = {}
        total_weight = self._convert_to_lbs(picking.weight_bulk)
        res = {
            'picking':picking,
            'serviceId':carrier.service_id,
            'carrier': carrier,
            'from_partner':picking.sale_id.warehouse_id.partner_id,
            'to_partner':picking.partner_id,
            'weight': str(total_weight),
            'currency_name': picking.sale_id.currency_id.name,
        }
        max_weight = carrier.eshipper_default_packaging_id.max_weight
        if max_weight and total_weight > max_weight:
            total_package = int(total_weight / max_weight)
            last_package_weight = total_weight % max_weight
            res['total_packages'] = total_package
            res['last_package_weight'] = last_package_weight
            res['package_ids'] = carrier.eshipper_default_packaging_id
 
            for seq in range(total_package):
                packages.append(max_weight)
            if last_package_weight:
                packages.append(last_package_weight)
        else:
            packages.append(total_weight)
        res['packages'] = packages
        return res

    def _create_shipping_xml(self, param):
        
        picking = param.get('picking')
        carrier = param.get('carrier')
        sale_order = picking.sale_id
        
        root = self.prepare_root_xml()
        QuoteRequest_node = etree.SubElement(root, "ShippingRequest")
        QuoteRequest_node.set('serviceId',param.get('serviceId'))
        QuoteRequest_node.set('stackable','true')
        self.prepare_address_xml(QuoteRequest_node,param.get('from_partner'))
        self.prepare_address_xml(QuoteRequest_node,param.get('to_partner'),type="To")
        self.prepare_payment_xml(QuoteRequest_node,"3rd Party")
        package = param.get('carrier').eshipper_default_packaging_id
        weight = param.get('weight')
        package_id = param.get('carrier').eshipper_default_packaging_id
        packages_node = self.prepare_packages_xml(QuoteRequest_node)
        for weight in param.get('packages',[]):
            self.prepare_package_xml(packages_node,weight,package_id)
        ref_1 = "%s"%(picking.name)
        ref_2 = sale_order and sale_order.name
        ref_3 = "%s"%(picking.id)
        self.prepare_references_xml(QuoteRequest_node,ref_1,ref_2,ref_3)
        return etree.tostring(root,encoding='utf8')
    
    def send_shipping(self, picking, carrier):
        packages = []
        dict_response_lst = []
        param = self._get_send_param(picking, carrier)
        if picking.move_lines.filtered(lambda move: not move.product_id.weight):
            raise Warning ("The delivery cannot be done because the weight of your product is missing.")
        dict_response = {
            'tracking_number': 0.0,
            'price': 0.0,
            'currency': False,
            'error_found': False
        }
        request_text = self._create_shipping_xml(param)
        root = self._send_request(request_text)
        
        error_elements = root.getElementsByTagName('Error')
        if error_elements:
            error_message = ''
            for node in error_elements:
                error_message += node.getAttribute('Message')
            if error_message:
                raise UserError(error_message)
            
        eshipper_order = root.getElementsByTagName('Order')
        eshipper_order = eshipper_order and eshipper_order[0]
        eshipper_id = eshipper_order.getAttribute('id')
        packages = root.getElementsByTagName('Package')
        for package in packages:
            tracking_number = package.getAttribute('trackingNumber')
            Quote = root.getElementsByTagName('Quote')
            Label = root.getElementsByTagName('Labels')[0].childNodes[0].nodeValue
            tracking_url = root.getElementsByTagName('TrackingURL')[0].childNodes[0].nodeValue
            total_charges = Quote and Quote[0].getAttribute('totalCharge') or 0.0
            dict_response = {
                'currency': Quote and Quote[0].getAttribute('currency') or '',
                'price': float(total_charges),
                'tracking_number':tracking_number,
                'label': Label,
                'tracking_url':tracking_url,
                'order_id':eshipper_id
            }
            dict_response_lst.append(dict_response)
        return dict_response_lst
