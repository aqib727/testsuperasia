# -*- coding: utf-8 -*-

import json
import logging
import requests
import werkzeug
from werkzeug import urls
from werkzeug.exceptions import Forbidden, NotFound
import lxml.html
import xmltodict
from ast import literal_eval

from odoo import http, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo.http import request
# from odoo.addons.base.ir.ir_qweb.fields import nl2br
# from odoo.addons.http_routing.models.ir_http import slug
# from odoo.addons.website.controllers.main import QueryURL
# from odoo.addons.website.controllers.main import Website
# from odoo.addons.website_form.controllers.main import WebsiteForm
# from odoo.osv import expression

_logger = logging.getLogger(__name__)

def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&amp;", "&")
    s = s.replace("&quot;", "\"")
    return s

class MonerisController(http.Controller):
    _notify_url = '/payment/moneris/ipn/'
    _return_url = '/payment/moneris/dpn/'
    _cancel_url = '/payment/moneris/cancel/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from moneris. """
        _logger.info(request.session)
        return_url = post.pop('return_url', '')
        if not return_url:
            t = unescape(post.pop('rvarret', '{}'))
            custom = json.loads(t)
            return_url = custom.get('return_url', '/')
        if not return_url:
            return_url = '/payment/shop/validate'
        _logger.info(str(return_url))
        return return_url

    def moneris_validate_data(self, **post):
        """ 
        Moneris IPN: three steps validation to ensure data correctness
         - step 1: return an empty HTTP 200 response -> will be done at the end
           by returning ''
         - step 2: POST the complete, unaltered message back to Moneris (preceded
           by cmd=_notify-validate), with same encoding
         - step 3: moneris send either VERIFIED or INVALID (single word)

        Once data is validated, process it. 
        """
        _logger.info("moneris_validate_data-->")
        res = False
        _logger.info("----------post---------------")
        _logger.info(post)
        reference = post.get('rvaroid')
        tx = None
        if reference:
            tx_ids = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
            if tx_ids:
                tx = request.env['payment.transaction'].sudo().browse(tx_ids[0].id)
        _logger.info("----------tx & ref ---------------")
        _logger.info(str(tx) + ", " + str(reference))
        if tx:
            _logger.info("\n tx-->" + str(tx) + \
                            "\n TX Date--> " +  str(tx.date) + \
                            "\n acquirer_id--> " +  str(tx.acquirer_id) + \
                            "\n state--> " +  str(tx.acquirer_id.state) + \
                            "\n state--> " +  str(tx and tx.acquirer_id and tx.acquirer_id.state or 'enabled'))
            moneris_urls = request.env['payment.acquirer']._get_moneris_urls(tx and tx.acquirer_id and tx.acquirer_id.state or 'prod')
            validate_url = moneris_urls['moneris_auth_url']
            _logger.info("moneris_urls---> " + str(moneris_urls))
            _logger.info("validate_url---> " + str(validate_url))
        else:
            _logger.warning('Moneris: No order found')
            return res

        sid = tx.acquirer_id.moneris_psstore_id
        key = tx.acquirer_id.moneris_hpp_key
        
        new_post = dict(ps_store_id=sid, hpp_key=key, transactionKey=post.get('transactionKey'))
        _logger.info("new_post--->")
        _logger.info(str(new_post))
        urequest = requests.post(validate_url, new_post)
        _logger.info("urequest---------------->")
        _logger.info(str(urequest))
        try:
            _logger.info("urequest.text----------->")
            _logger.info(str(urequest.text))
        except Exception as e:
            _logger.info("Exception: " + str(e.args))
            _logger.info(str(urequest))
        new_response ={}
        try:
            tree = lxml.html.fromstring(urequest.content)
            form_values = tree.xpath('//input')
            for field in form_values:
                if field.name != None:
                    new_response[field.name] = field.value
        except Exception as e:
            _logger.warning(str(e.args))
            raise ValidationError(str(e.args))

        success = post.get('response_code')
        if 'gift_card' in post:
            success = post['gift_card'].get('response_code')
            post = dict(post)
            gift_card = dict(post['gift_card'])
            post.update(gift_card)
            _logger.info("New Post for Gift Card--> " + str(post))
        _logger.info("success--> " + str(success))
        txn_key = ""
        _logger.info("New response-->")
        _logger.info("New response-->")
        _logger.info(str(new_response))        
        _logger.info(str(new_response.get('status')))
        _logger.info(str(post.get('response_order_id')))
        try:
            if success and new_response.get('response_code'):
                _logger.info(str(success) + "," + str(new_response.get('response_code')))
            if (int(success) < 50 and post.get('result') == '1'):
                #     and new_response.get('response_code') is not 'null' and int(new_response.get('response_code')) < 50 and
                #     new_response.get('transactionKey') == post.get('transactionKey') and
                #     new_response.get('order_id') == post.get('response_order_id')
                # ):
                _logger.info('Moneris: validated data')
                res = request.env['payment.transaction'].sudo().form_feedback(post, 'moneris')
                _logger.info('form_feedback--> '+ str(res))
                txn_key = post.get('transactionKey')
                if txn_key:
                    _logger.info('txn_key--> '+ str(txn_key))
            else:
                res = 'Moneris: answered INVALID on data verification: ' + new_response.get('status') + '/' + post.get('response_order_id')

        except ValueError:
            res = 'Moneris: answered INVALID on data verification: ' + new_response.get('status') + '/' + post.get('response_order_id')

        if txn_key != "":
            res = "status=approved&transactionKey={}".format(txn_key)
        _logger.info('\n res--> '+ str(res))

        if 'transactionKey' in res:
            try:
                _logger.info("Before request.session------------>")
                _logger.info(request.session)
                session = dict(request.session)
                if tx:
                    order_id_new = tx.sale_order_ids
                    if len(order_id_new) == 0:
                        order_id_new = request.env['sale.order'].sudo().search([('name','=',post.get('response_order_id').split("-")[0])], limit=1)
                    _logger.info("\n tx" + ": " + str(tx) + 
                            "\n tx.sale_order_ids: " + str(tx.sale_order_ids) + \
                            "\n tx.sale_order_ids_nbr: " + str(tx.sale_order_ids_nbr) + \
                            "\n tx.response_order_id: " + str(post.get('response_order_id')) + \
                            "\n order_id_new: " + str(order_id_new) 
                    )

                    _logger.info(order_id_new)
                    if '__payment_tx_ids__' not in session:
                        _logger.info('__payment_tx_ids__')
                        try:
                            request.session['__payment_tx_ids__'] = []
                            request.session['__payment_tx_ids__'].append(int(tx.id))
                            _logger.info("TX Appending")
                        except Exception as e:
                            _logger.info("Excception __payment_tx_ids__: " + str(e.args))
                            request.session['__payment_tx_ids__'] = (int(tx.id))
                            _logger.info(request.session['__payment_tx_ids__'])

                    if '__payment_tx_ids__' in session:
                        _logger.info(type(request.session['__payment_tx_ids__']))
                        _logger.info(request.session['__payment_tx_ids__'])
                        if tx.id not in session['__payment_tx_ids__']:
                            try:
                                request.session['__payment_tx_ids__'].append(int(tx.id))
                                _logger.info("TX Appending")
                            except Exception as e:
                                _logger.info("Excception __payment_tx_ids__: " + str(e.args))
                                request.session['__payment_tx_ids__'] = (int(tx.id))
                                _logger.info("TX Tuple Add")

                    if '__website_sale_last_tx_id' in session:
                        try:
                            if tx.id  != session['__website_sale_last_tx_id']:
                                request.session['__website_sale_last_tx_id'] = int(tx.id)
                            _logger.info(type(session['__website_sale_last_tx_id']))
                            _logger.info(request.session['__website_sale_last_tx_id'])
                        except Exception as e:
                            if tx.id  != session['__website_sale_last_tx_id']:
                                request.session['__website_sale_last_tx_id'] = (int(tx.id))
                            _logger.info("Excception __website_sale_last_tx_id: " + str(e.args))

                    if '__website_sale_last_tx_id' not in session:
                        try:
                            _logger.info("---------------->") 
                            request.session['__website_sale_last_tx_id'] = (int(tx.id))
                            _logger.info(request.session['__website_sale_last_tx_id'])   
                        except Exception as e:
                            request.session['__website_sale_last_tx_id'] = int(tx.id)
                            _logger.warning("Error __website_sale_last_tx--> " + str(e.args))
                        _logger.info("---------------->")                             

                    if 'sale_order_id' not in session:
                        try:
                            _logger.info("sale_order_id---------------->") 
                            request.session['sale_order_id'] = int(order_id_new.id)
                            _logger.info(request.session['__website_sale_last_tx_id'])   
                            _logger.info(type(request.session['sale_order_id']))
                            _logger.info(request.session['sale_order_id'])
                        except Exception as e:
                            request.session['sale_order_id'] = (int(order_id_new.id))
                            _logger.info("sale_order_id-->"+str(e.args))


                    if 'sale_last_order_id' not in session:
                        try:
                            _logger.info("sale_last_order_id---------------->") 
                            request.session['sale_last_order_id'] = int(order_id_new.id)
                            _logger.info(type(request.session['sale_last_order_id']))
                            _logger.info(request.session['sale_last_order_id'])
                        except Exception as e:
                            request.session['sale_last_order_id'] =  (int(order_id_new.id))
                            _logger.info("sale_last_order_id-->"+str(e.args))

                    _logger.info("Updated request.session------------>")
                    _logger.info(request.session)  
                    if order_id_new:
                        if order_id_new.sudo().company_id:
                            res += "&infoemail={}".format(order_id_new.sudo().company_id.email)
                    if 'infoemail' not in res:
                        res += "&infoemail={}".format(tx.company_id.email)
            except Exception as e:
                _logger.info(str(e.args))
        print("Response")
        print(res)
        return res

    @http.route('/payment/moneris/ipn/', type='http', auth='none', methods=['POST'], csrf=False)
    def moneris_ipn(self, **post):
        """ Moneris IPN. """
        _logger.info("Moneris IPN.")
        res = self.moneris_validate_data(**post)
        _logger.info("moneris_ipn--> " + str(res))
        return werkzeug.utils.redirect('/moneris?{}'.format(res))

    @http.route('/payment/moneris/dpn', type='http', auth="none", methods=['POST'], csrf=False)
    def moneris_dpn(self, **post):
        """ Moneris DPN """
        _logger.info("moneris_dpn-->")
        _logger.info("post--> " + str(post))
        if 'xml_response' in post:
            if 'gift_charge_total' in post['xml_response']:
                if '<receipt_text' in post['xml_response']:
                    part1 = post['xml_response'].split('<receipt_text')[0]
                    part2 = post['xml_response'].split('</receipt_text>')[1]
                    post['xml_response'] = part1+part2
            post = xmltodict.parse(post['xml_response'])
            if 'response' in post:
                post = post['response']
        if post.get('gift_card'):
            _logger.info("gift post--> " + str(post.get('gift_card')))
        return_url = self._get_return_url(**post)
        _logger.info("return_url--> " + str(return_url))
        if self.moneris_validate_data(**post):
            return werkzeug.utils.redirect(return_url)
        else:
            return werkzeug.utils.redirect(self._cancel_url)

    @http.route('/payment/moneris/cancel', type='http', auth="none", methods=['GET','POST'], csrf=False)
    def moneris_cancel(self, **post):
        """ When the user cancels its Moneris payment: GET on this route """
        _logger.info("moneris_cancel-->")
        
        if 'xml_response' in post:
            if 'gift_charge_total' in post['xml_response']:
                if '<receipt_text' in post['xml_response']:
                    part1 = post['xml_response'].split('<receipt_text')[0]
                    part2 = post['xml_response'].split('</receipt_text>')[1]
                    post['xml_response'] = part1+part2
            post = xmltodict.parse(post['xml_response'])
            if 'response' in post:
                post = post['response']

        _logger.info("post-->\n"  +  str(post))
        reference = post.get('rvaroid')
        order_id_new = ""
        if post.get('response_order_id'):
            order_id_new = request.env['sale.order'].sudo().search([('name','=',post.get('response_order_id').split("-")[0])], limit=1)
        post['infoemail'] = ""
        if len(order_id_new) == 0:
            if reference:
                order_id_new = request.env['sale.order'].sudo().search([('name','=',reference.split("-")[0])], limit=1)
            else:
                if 'order_id' in post:
                    order_id_new = request.env['sale.order'].sudo().search([('name','=',post['order_id'].split("-")[0])], limit=1)

        if order_id_new:
            if order_id_new.company_id:
                post['infoemail'] = order_id_new.company_id.email
        if post.get('infoemail') == "":
            _logger.info("infoemail is null")

        _logger.info("order_id_new")
        _logger.info(order_id_new)
        _logger.info("post")
        _logger.info(post)
        if reference:
            sales_order_obj = request.env['sale.order']
            so_ids = sales_order_obj.sudo().search([('name', '=', reference)])
            # if so_ids:
            #     '''return_url = '/shop/payment/get_status/' + str(so_ids[0])'''
            #     so = sales_order_obj.browse(so_ids[0].id)

        msg = "/moneris?status=cancelled&"
        for key, value in post.items():
            msg += str(key)
            msg+= '='
            msg+= str(value)
            msg+='&'
        _logger.info("msg-->")
        _logger.info(msg)
        return werkzeug.utils.redirect(msg)

    @http.route('/moneris', type='http', auth='public', methods=['GET'], website=True)
    def moneris_status(self, **get):
        _logger.info("moneris_status-->")
        _logger.info(get)
        status = ''
        transactionKey = ''
        response_code = ''
        message = ''
        infoemail = ''
        
        if 'status' in get:
            status = get['status']
        if 'transactionKey' in get:
            transactionKey = get['transactionKey']
        if 'response_code' in get:
            response_code = get['response_code']
        if 'message' in get:
            message = get['message']
        if 'infoemail' in get:
            infoemail = get['infoemail']
        if 'infoemail' not in get:
            if 'response_order_id' in get:
                    order_id_new = request.env['sale.order'].sudo().search([('name','=',get['response_order_id'].split("-")[0])], limit=1)
                    if len(order_id_new) > 0:
                        infoemail = order_id_new.company_id.email
        return request.render('payment_moneris_hosted.moneris_status', {'status': status, 'transactionKey': transactionKey, 'response_code': response_code, 'message': message, 'infoemail': infoemail})

