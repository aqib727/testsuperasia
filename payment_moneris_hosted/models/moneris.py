# -*- coding: utf-'8' "-*-"

import base64
import logging
import werkzeug
from werkzeug import urls
import json
import xmltodict
from datetime import datetime
from odoo.http import request
from odoo import api, exceptions, fields, models, _
from odoo.addons.payment_moneris_hosted.controllers.main import MonerisController
from odoo.tools.float_utils import float_compare

from odoo.exceptions import ValidationError
from odoo import api, SUPERUSER_ID


_logger = logging.getLogger(__name__)

def _partner_format_address(address1=False, address2=False):
    return ' '.join((address1 or '', address2 or '')).strip()


def _partner_split_name(partner_name):
    return [' '.join(partner_name.split()[:-1]), ' '.join(partner_name.split()[-1:])]

class AcquirerMoneris(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('moneris', _('Moneris'))])
    moneris_transaction_type = fields.Selection(string='Transaction Type', selection=[('preauthorization', _('Preauthorization')), ('purchase', _('Purchase'))], default = 'purchase')
    moneris_psstore_id = fields.Char(string=_('Moneris PS Store ID'))
    moneris_hpp_key = fields.Char(string=_('Moneris HPP Key'))
    moneris_use_ipn = fields.Boolean(_('Use IPN'), default=True, help=_('Moneris Instant Payment Notification'))
    moneris_image_url = fields.Char("Checkout Image URL", groups='base.group_user', 
        help="A relative absolute URL pointing to a square image of your brand or product. As defined in your moneris_onsite profile. See: https://moneris_onsite.com/docs/checkout")
    moneris_order_confirmation = fields.Selection(string=_('Order Confirmation'), selection=[
        # ('none', 'No Automatic Confirmation'),
        # ('authorize', 'Authorize the amount and confirm it'),
        ('capture',_('Authorize & capture the amount and conform it'))], default='capture', readonly=True)
    moneris_store_card = fields.Selection(string=_('Store Card Data'), selection=[
        ('never', _('Never')), 
        ('customer', _('Let the customer decide')),
        ('always',_('Always'))], default='never')

    fees_active = fields.Boolean(default=False)
    fees_dom_fixed = fields.Float(default=0.35)
    fees_dom_var = fields.Float(default=3.4)
    fees_int_fixed = fields.Float(default=0.35)
    fees_int_var = fields.Float(default=3.9)

    def _get_moneris_urls(self, environment):
        """ Moneris URLS """
        if environment == 'enabled':
            moneris_url =  {
                'moneris_form_url': 'https://www3.moneris.com/HPPDP/index.php',
                'moneris_auth_url': 'https://www3.moneris.com/HPPDP/verifyTxn.php',
            }
        else:
            moneris_url =  {
                'moneris_form_url': 'https://esqa.moneris.com/HPPDP/index.php',
                'moneris_auth_url': 'https://esqa.moneris.com/HPPDP/verifyTxn.php',
            }

        _logger.info("\n Environment:" +  str(environment) + "\n+ " + str(moneris_url))
        return moneris_url

    def moneris_compute_fees(self, amount, currency_id, country_id):
        _logger.info("moneris_compute_fees-->")
        try:
            _logger.info("Session-------->")
            _logger.info(request.session)
        except Exception as e:
            print(str(e.args))

        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        _logger.info(str(fees))
        return fees

    def moneris_form_generate_values(self, values):
        _logger.info("moneris_form_generate_values-->")
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        moneris_tx_values = dict(values)
        _logger.info(moneris_tx_values)

        moneris_tx_values.update({
            'cmd': '_xclick',
            'business': self.moneris_psstore_id,
            'item_name': '%s: %s' % (self.company_id.name, values['reference']),
            'item_number': values['reference'],
            'amount': values['amount'],
            'currency_code': values['currency'] and values['currency'].name or '',
            'address1': values.get('partner_address'),
            'city': values.get('partner_city'),
            'country': values.get('partner_country') and values.get('partner_country').code or '',
            'state': values.get('partner_state') and (
                        values.get('partner_state').code or values.get('partner_state').name) or '',
            'email': values.get('partner_email') or '',
            'zip_code': values.get('partner_zip') or '',
            'first_name': values.get('partner_first_name') or '',
            'last_name': values.get('partner_last_name') or '',
            'moneris_return': urls.url_join(base_url, MonerisController._return_url),
            'notify_url': urls.url_join(base_url, MonerisController._notify_url),
            'cancel_return': urls.url_join(base_url, MonerisController._cancel_url),
            'handling': '%.2f' % moneris_tx_values.pop('fees', 0.0) if self.fees_active else False,
            'custom': json.dumps({'return_url': '%s' % moneris_tx_values.pop('return_url')}) if moneris_tx_values.get(
                'return_url') else False,
        })

        # Display Items
        order_lines = []
        order_name = values['reference'].split("-")[0] if len(values['reference'].split("-")) > 1 else values['reference']
        order_id = self.env['sale.order'].sudo().search([('name','=',order_name)])
        i =1
        shipping_cost = 0.0 
        gst = pst = hst = 0
        for line in order_id.order_line:
            try:
                if line.is_delivery:
                    shipping_cost = line.price_unit
            except Exception as e:
                _logger.warning("Shipping error" + str(e.args))
            item ={}
            item['name'] = str(i)
            item['id'] = line.product_id.default_code or line.product_id.id#Product Code - SKU (max 10 chars)
            item['description'] = line.product_id.name[:15]#Product Description - (max 15chars)
            item['quantity'] = line.product_uom_qty#Quantity of Goods Purchased -(max - 4 digits)
            item['price'] = line.price_unit#Unit Price - (max - "7"."2" digits,i.e. min 0.00 & max 9999999.99)
            item['subtotal'] = line.price_subtotal#Quantity X Price of Product -(max - "7"."2" digits, i.e. min0.00 & max 9999999.99)
            order_lines.append(item)
            i += 1
            if line.tax_id:
                if 'gst' in line.tax_id.name.lower():
                    gst += line.price_tax
                if 'pst' in line.tax_id.name.lower():
                    pst += line.price_tax
                if 'hst' in line.tax_id.name.lower():
                    hst += line.price_tax
            
        moneris_tx_values['order_lines'] = order_lines
        moneris_tx_values['cust_id'] = values.get('partner_id')
        # Computes taxes and Shipping Cost
        moneris_tx_values['gst'] = gst
        moneris_tx_values['pst'] = pst
        moneris_tx_values['hst'] = hst
        moneris_tx_values['shipping_cost'] = shipping_cost
        moneris_tx_values['note'] = ''
        moneris_tx_values['email'] = values.get('billing_partner_email')

        if 'reference' in values:
            order_id = self.env['sale.order'].sudo().search([('name','=',values['reference'].split("-")[0])])
            if not order_id:
                order_id = self.env['sale.order'].sudo().search([('id','=',request.session['sale_order_id']) ])
            try:
                if order_id.partner_invoice_id != False:
                    moneris_tx_values['bill_first_name'] = order_id.partner_invoice_id.name.split(" ")[0] if order_id.partner_invoice_id != False else '' or ""
                    moneris_tx_values['bill_last_name'] = order_id.partner_invoice_id.name.split(" ")[1] if len(order_id.partner_invoice_id.name.split(" ")) > 1 else "" or ""
            except Exception as e:
                moneris_tx_values['bill_first_name'] = values.get('partner_first_name') or ""
                moneris_tx_values['bill_last_name'] = values.get('partner_last_name') or ""
            # Billing Details
            moneris_tx_values['bill_company_name'] = order_id.partner_invoice_id.company_name if order_id.partner_invoice_id.company_name != False else ""
            bill_street = order_id.partner_invoice_id.street if order_id.partner_invoice_id.street != False else "" or ""
            bill_street = bill_street + order_id.partner_invoice_id.street2 if order_id.partner_invoice_id.street2 != False else bill_street
            moneris_tx_values['bill_address_one'] = bill_street or ""
            moneris_tx_values['bill_city'] = order_id.partner_invoice_id.city if order_id.partner_invoice_id.city != False else "" or ""
            moneris_tx_values['bill_state_or_province'] = order_id.partner_invoice_id.state_id.code if order_id.partner_invoice_id.state_id != False else "" or ""
            moneris_tx_values['bill_country'] = order_id.partner_invoice_id.country_id.name if order_id.partner_invoice_id.country_id != False else "" or ""
            moneris_tx_values['bill_phone'] = order_id.partner_invoice_id.phone or ""
            # Shipping Details
            moneris_tx_values['ship_first_name'] = order_id.partner_shipping_id.name.split(" ")[0] or ""
            moneris_tx_values['ship_last_name'] = order_id.partner_shipping_id.name.split(" ")[1] if len(order_id.partner_shipping_id.name.split(" ")) > 1 else "" or ""
            moneris_tx_values['ship_company_name'] = order_id.partner_shipping_id.company_name or ""
            street = order_id.partner_shipping_id.street if order_id.partner_shipping_id.street != False else "" or ""
            street = street + order_id.partner_shipping_id.street2 if order_id.partner_shipping_id.street2 != False else street
            moneris_tx_values['ship_address_one'] = street or ""
            moneris_tx_values['ship_city'] = order_id.partner_shipping_id.city if order_id.partner_shipping_id.city != False else "" or ""
            moneris_tx_values['ship_state_or_province'] = order_id.partner_shipping_id.state_id.code if order_id.partner_shipping_id.state_id != False else "" or ""
            moneris_tx_values['ship_country'] = order_id.partner_shipping_id.country_id.name if order_id.partner_shipping_id.country_id != False else "" or ""
            moneris_tx_values['ship_phone'] = order_id.partner_shipping_id.phone or ""
            # moneris_tx_values['partial_toggle'] = values.get('partial_toggle') if values.get('partial_toggle') else False
            # moneris_tx_values['moneris_partial_amount'] = values.get('partial_amount')
        return moneris_tx_values

    def moneris_get_form_action_url(self):
        self.ensure_one()
        _logger.info("moneris_get_form_action_url--->")
        moneris_form_url = self._get_moneris_urls(self.state)['moneris_form_url']
        _logger.info("moneris_form_url-------->\n" + str(moneris_form_url))
        return moneris_form_url


class TxMoneris(models.Model):
    _inherit = 'payment.transaction'

    moneris_txn_type = fields.Char('Transaction type')
    moneris_customer_id = fields.Char('Customer Id')
    moneris_receipt_id = fields.Char('Receipt Id')
    moneris_response_code = fields.Char('Response Code')
    moneris_credit_card = fields.Char('Credit Card')
    
    moneris_card_name = fields.Char('Card Type')
    moneris_expiry_date = fields.Char('Expiry Date')
    moneris_transaction_time = fields.Char('Transaction Time')
    moneris_transaction_date = fields.Char('Transaction Date')
    moneris_transaction_id = fields.Char('Transaction ID')
    moneris_payment_type = fields.Char('Payment Type')
    moneris_reference_no = fields.Char('Reference Number')
    moneris_bank_approval = fields.Char('Bank Approval')
    moneris_card_holder = fields.Char('Cardholder')
    moneris_order_id = fields.Char('Response Order Id')
    moneris_iso_code = fields.Char('Iso Code')
    moneris_transaction_key = fields.Char('Transaction Key')
    moneris_transaction_no = fields.Char('Transaction Number')
    moneris_card_amount = fields.Char()
    moneris_session = fields.Char('Moneris Session')

    moneris_card_type = fields.Selection(
        string='Payment Method',
        selection=[('card', 'Card'), 
        # ('gift', 'Gift Card'),  
        # ('loyalty', 'Loyalty Card'),
        # ('interac', 'Interac')
        ], 
        # default="card",
    )
    # GIFT CARD
    
    moneris_gift_txntype = fields.Char("Txn Type")
    moneris_gift_cardnum = fields.Char("Gift Card Num")
    moneris_gift_refnum = fields.Char("Gift Ref Num")
    moneris_gift_orderno = fields.Char("Gift Order No")
    moneris_gift_txnnum = fields.Char("Gift Txn Num")

    moneris_card_description = fields.Char()
    moneris_gift_charge = fields.Char("Gift Charge")
    moneris_rem_balance = fields.Char("Remaining Balance")
    moneris_gift_display = fields.Char("Gift Display")
    moneris_voucher_text = fields.Char("Voucher Text")
    # INTERAC
    moneris_interac_issname = fields.Char("ISSNAME")
    moneris_interac_invoice = fields.Char("INVOICE")
    moneris_interac_issconf = fields.Char("ISSCONF")
    # Partial Amount
    moneris_partial_amount = fields.Char()
    moneris_partial_toggle = fields.Boolean()
    # Gift Partial Transactions
    moneris_txn_related = fields.Char()

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------
    @api.model
    def _convert_data(self, data):
        """Convert Data"""
        _logger.info("_convert_data-->")
        # Change for GIFT Purchase
        _logger.info("\n charge_total" + str(data.get("charge_total"))+\
                    "\n gift_charge_total"+ str(data.get('charge_total'))+\
                    "\n response_order_id"+ str(data.get('response_order_id')) )
        if data.get('gift_charge_total'):
            _logger.info("gift_charge_total" + str(data.get('gift_charge_total')))
            if not data.get('charge_total'):
                data['charge_total'] = data.get('gift_charge_total')
            _logger.info("charge_total")
            _logger.info(data.get('charge_total'))
        if not data.get('response_order_id'):
            data['response_order_id'] = data.get('order_no') or ''
            _logger.info("order_no" + str(data.get('order_no')))
        
        # Change for INTREAC Purchase
        if 'Trans_name' in data and 'ISSNAME' in data:
            _logger.info("INTREAC Purchase-->")
        return data


    @api.model
    def _moneris_form_get_tx_from_data(self, data):
        _logger.info("_moneris_form_get_tx_from_data-->")
        data  = self._convert_data(data)
        _logger.info(data)
        _logger.info(request.session)
        reference, txn_id = data.get('rvaroid'), data.get('txn_num')
        _logger.info(str(reference) + ","+ str(txn_id))
        if not reference or not txn_id:
            error_msg = _('Moneris: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Moneris: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        _logger.info(txs[0])
        return txs[0]

    def _moneris_form_get_invalid_parameters(self,  data):
        _logger.info(request.session)
        invalid_parameters = []

        # TODO: txn_id: shoudl be false at draft, set afterwards, and verified with txn details
        if self.acquirer_reference and data.get('response_order_id') != self.acquirer_reference:
            invalid_parameters.append(('response_order_id', data.get('response_order_id'), self.acquirer_reference))
        # check what is buyed
        if float_compare(float(data.get('charge_total', '0.0')), (self.amount), 2) != 0:
            invalid_parameters.append(('charge_total', data.get('charge_total'), '%.2f' % self.amount))
        return invalid_parameters

    def _moneris_form_validate(self, data):
        _logger.info("_moneris_form_validate")
        _logger.info(request.session)
        _logger.info(data)
        status = data.get('result')
        _logger.info("-----------------form -----validate----------------------")
        if status == '1':
            _logger.info('Validated Moneris payment for tx %s: set as done' % (self.reference))
            date_time =''
            _logger.info(data.get('date_stamp'))
            try:
                date_time = data.get('date_stamp') + ' ' + data.get('time_stamp')
            except Exception as e:
                date_time = data.get('date_time')
            
            data.update(state='done', date_validate=data.get(date_time, fields.datetime.now()))
            _logger.info("---form validate----------------------")
            tranrec = self._moneris_convert_transaction(data)
            _logger.info(str("Transaction----->"))
            _logger.info(tranrec)
            
            response = self.sudo().write(tranrec)
            _logger.info(response)
            return response
        else:
            error = 'Received unrecognized status for Moneris payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            data.update(state='error', state_message=error)
            response = self.write(data)
            return response
        _logger.info("_moneris_form_validate-->" + str(response))

    def convert_transaction(self, data, transaction):
        ''' Compute the price of the order shipment'''
        print("convert_transaction")
        self.ensure_one()
        if hasattr(self, '%s_convert_transaction' % self.moneris_card_type):
            res = getattr(self, '%s_rate_shipment' % self.moneris_card_type)(data, transaction)
            return res

    def card_convert_transaction(self, data, transaction):
        ''' card_convert_transaction'''
        _logger.info("card_convert_transaction")
        order_id = self.env['sale.order'].sudo().search([('name','=',data.get('response_order_id').split("-")[0])])
        transaction['acquirer_reference'] = data.get('bank_transaction_id')#data['bank_transaction_id']
        transaction['amount'] = data.get('charge_total')#data['charge_total']
        if data.get('date_validate'):
            transaction['date'] = data.get('date_validate')
        else:
            dateTime =''
            _logger.info(data.get('date_stamp'))
            try:
                dateTime = data.get('date_stamp') + ' ' + data.get('time_stamp')
            except Exception as e:
                dateTime = data.get('date_time')
            transaction['date'] = data.get(dateTime, fields.datetime.now())
        # transaction['fees'] = 0.0#Set by Back-end#Fees#Monetary
        if order_id:
            _logger.info("order_id---->" + str(order_id))
            transaction['partner_country_id'] = order_id.partner_id.country_id.id#int(data['iso_code'])#Country#Many2one#     Required
            _logger.info("partner_country_id---->" + str(transaction['partner_country_id']))
        # transaction['payment_token_id'] = ""#Payment Token#Many2one
        # transaction['reference'] = ""#Reference#Char#Required#Automatic
        transaction['state'] = data.get('state')
        if data.get('message'): 
            transaction['state_message'] = data.get('message').replace("\n","")
        else:
            transaction['state_message'] = ''
        transaction['type'] = "validation"
        # Moneris Details
        if data.get('gift_card'):
            card_amount = float(data.get('charge_total')) - float(data.get('gift_card').get('gift_charge_total'))
        else:
            card_amount = float(data.get('charge_total'))
        transaction['moneris_card_amount'] = card_amount
        transaction['moneris_card_name'] = data.get('card') or '' 
        transaction['moneris_customer_id'] = data.get('moneris_customer_id') or '' 
        transaction['moneris_receipt_id'] = data.get('rvaroid') or ''
        transaction['moneris_response_code'] = data.get('response_code') or ''
        transaction['moneris_credit_card'] = data.get('f4l4') or data.get('card_num') or ''
        transaction['moneris_expiry_date'] = data.get('expiry_date') or ''
        transaction['moneris_transaction_time'] = data.get('time_stamp') or ''
        transaction['moneris_transaction_date'] = data.get('date_stamp') or ''
        transaction['moneris_transaction_id'] = data.get('txn_num') or ''
        transaction['moneris_payment_type'] = data.get('trans_name') or ''
        transaction['moneris_reference_no'] = data.get('moneris_reference_no') or ''
        transaction['moneris_txn_type'] = data.get('trans_name') or ''
        transaction['moneris_bank_approval'] = data.get('bank_approval_code') or ''
        transaction['moneris_card_holder'] = data.get('cvd_response_code') or ''
        transaction['moneris_order_id'] = data.get('rvaroid') or data.get('gift_card').get('order_no') or ''
        transaction['moneris_iso_code'] = data.get('iso_code') or ''
        transaction['moneris_transaction_key'] = data.get('transactionKey') or ''
        transaction['moneris_transaction_no'] = data.get('txn_num') or ''
        transaction['moneris_card_amount'] = data.get('txn_num') or ''
        transaction['moneris_card_type'] = 'card'
        return transaction

    def _moneris_convert_transaction(self, data):
        _logger.info("_moneris_convert_transaction")
        _logger.info(str(data))
        try:
            transaction = {}
            transaction = self.card_convert_transaction(data, transaction)
            if 'gift_charge_total' in data or 'gift_card' in data:
                try:
                    transaction = self.gift_convert_transaction(data, transaction)
                except Exception as e:
                    _logger.warning("Gift Tx Error: " + str(e.args))
                    # transaction['error'] = 'Gift Error: This app is not provided with gift card payment. Please communicate with App Provider.'
                    # raise ValidationError("This app is not provided with gift card payment. Please communicate with App Provider.")
            if 'ISSNAME' in data or 'ISSCONF' in data or 'INVOICE' in data:
                try:
                    transaction = self.interac_convert_transaction(data, transaction)
                except Exception as e:
                    _logger.warning("Interac Tx Error: " + str(e.args))
                    # transaction['error'] = 'Interac Error: This app is not provided with Interac payment. Please communicate with App Provider.'
                    # raise ValidationError("This app is not provided with Interac payment. Please communicate with App Provider.")
            return transaction
        except Exception as e:
            return {'error':str(e.args)}


    # def _moneris_convert_transaction(self, data):
    #     _logger.info("_moneris_convert_transaction")
    #     _logger.info(str(data))
    #     # _logger.info(request.session)
    #     try:
    #         order_id = self.env['sale.order'].sudo().search([('name','=',data.get('response_order_id').split("-")[0])])
    #         transaction = {}
    #         transaction['acquirer_reference'] = data['bank_transaction_id']
    #         transaction['amount'] = data['charge_total']
    #         transaction['date'] = data['date_validate']
    #         # transaction['fees'] = 0.0#Set by Back-end#Fees#Monetary
    #         if order_id:
    #             _logger.info("order_id---->" + str(order_id))
    #             transaction['partner_country_id'] = order_id.partner_invoice_id.country_id.id#int(data['iso_code'])#Country#Many2one#     Required
    #             _logger.info("partner_country_id---->" + str(transaction['partner_country_id']))
    #         # transaction['payment_token_id'] = ""#Payment Token#Many2one
    #         # transaction['reference'] = ""#Reference#Char#Required#Automatic
    #         transaction['state'] = data['state']
    #         if data.get('message'): 
    #             transaction['state_message'] = data.get('message').replace("\n","")
    #         else:
    #             transaction['state_message'] = ''
    #         transaction['type'] = "validation"
    #         # Moneris Details
    #         transaction['moneris_customer_id'] = data['moneris_customer_id'] if 'moneris_customer_id' in data else ''
    #         transaction['moneris_receipt_id'] = data['rvaroid'] if 'rvaroid' in data else ''
    #         transaction['moneris_response_code'] = data['response_code'] if 'response_code' in data else ''
    #         transaction['moneris_credit_card'] = data['f4l4'] if 'f4l4' in data else ''
    #         transaction['moneris_expiry_date'] = data['expiry_date'] if 'expiry_date' in data else ''
    #         transaction['moneris_transaction_time'] = data['time_stamp'] if 'time_stamp' in data else ''
    #         transaction['moneris_transaction_date'] = data['date_stamp'] if 'date_stamp' in data else ''
    #         transaction['moneris_transaction_id'] = data['txn_num'] if 'txn_num' in data else ''
    #         transaction['moneris_payment_type'] = data['trans_name'] if 'trans_name' in data else ''
    #         transaction['moneris_reference_no'] = data['moneris_reference_no'] if 'moneris_reference_no' in data else ''
    #         transaction['moneris_txn_type'] = data['trans_name'] if 'trans_name' in data else ''
    #         transaction['moneris_bank_approval'] = data['bank_approval_code'] if 'bank_approval_code' in data else ''
    #         transaction['moneris_card_holder'] = data['cvd_response_code'] if 'cvd_response_code' in data else ''
    #         transaction['moneris_order_id'] = data['rvaroid'] if 'rvaroid' in data else ''
    #         transaction['moneris_iso_code'] = data['iso_code'] if 'iso_code' in data else ''
    #         transaction['moneris_transaction_key'] = data['transactionKey'] if 'transactionKey' in data else ''
    #         transaction['moneris_transaction_no'] = data['txn_num'] if 'txn_num' in data else ''
    #         transaction['moneris_card_type'] = 'card'
    #         # Payment Token is not saved
    #         if 'gift_charge_total' in transaction or 'gift_card' in transaction:
    #             _logger.info("GIFT CARDS")
    #             transaction['moneris_card_type'] = 'gift'
    #             transaction['moneris_card_description'] = data['gift_card'].get('card_desc') if 'card_desc' in data['gift_card'] else ''
    #             transaction['moneris_gift_charge'] = data['gift_card'].get('gift_charge_total') if 'gift_charge_total' in data['gift_card'] else ''
    #             transaction['moneris_rem_balance'] = data['gift_card'].get('rem_balance') if 'rem_balance' in data['gift_card'] else ''
    #             transaction['moneris_gift_display'] = data['gift_card'].get('display_text') if 'display_text' in data['gift_card'] else ''
    #             transaction['moneris_voucher_text'] = data['gift_card'].get('voucher_text') if 'voucher_text' in data['gift_card'] else ''
    #         if 'Trans_name' in transaction and 'ISSNAME' in transaction:
    #             _logger.info("INTERAC ONLINE")
    #             transaction['moneris_card_type'] = 'interac'
    #             transaction['moneris_txn_type'] = data['Trans_name'] if 'Trans_name' in data else ''
    #             transaction['moneris_interac_issname'] = data['ISSNAME'] if 'ISSNAME' in data else ''
    #             transaction['moneris_interac_invoice'] = data['INVOICE'] if 'INVOICE' in data else ''
    #             transaction['moneris_interac_issconf'] = data['ISSCONF'] if 'ISSCONF' in data else ''

    #         return transaction
    #     except Exception as e:
    #         return {'error':str(e.args)}
