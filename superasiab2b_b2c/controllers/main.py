import base64
import io
from datetime import datetime
from dateutil import relativedelta
from datetime import datetime,timedelta
import datetime
import time
import json
import os
import logging
import requests
import werkzeug.utils
import werkzeug.wrappers
import psycopg2
from random import randint
import random

from itertools import islice
from xml.etree import ElementTree as ET
import unicodedata

import odoo
import re
from odoo.addons.auth_signup.models.res_partner import SignupError, now


from odoo import http, models, fields, _
from odoo import SUPERUSER_ID
from odoo.http import request
from odoo.tools import pycompat, OrderedSet
from odoo.addons.http_routing.models.ir_http import slug, _guess_mimetype
from odoo.addons.web.controllers.main import Binary
from odoo.addons.web.controllers.main import Home

import urllib.request
_logger = logging.getLogger(__name__)


def redirect_with_hash(*args, **kw):
    """
        .. deprecated:: 8.0

        Use the ``http.redirect_with_hash()`` function instead.
    """
    return http.redirect_with_hash(*args, **kw)


class Extension_Home(Home):
    @http.route()
    def web_login(self, redirect=None, **kw):
        _logger.info('========kw=========== %s' % kw)   
        response = super(Extension_Home, self).web_login()             
        _logger.info('========kw=========== %s' % kw)                
        _logger.info('========request.uid=========== %s' % request.uid)                

        user_obj=request.env['res.users']

        b2bid = request.env['ir.model.data'].get_object('superasiab2b_b2c','group_b2baccount')
        portalid = request.env['ir.model.data'].get_object('base','group_portal')

        group_list = [b2bid.id,portalid.id]

        user_data=user_obj.search([('id','=',request.uid),('groups_id','in',group_list)])


        if user_data:
            return werkzeug.utils.redirect('/shop')

        return response

class superasiab2b_b2c(http.Controller):
    

    @http.route(['/b2b_activation'], type='http', auth="public", website=True,csrf=False)
    def b2b_activation(self, **post):
        error = {}
        default = {}
        env = request.env(user=SUPERUSER_ID)
        # country_obj=request.env['res.country']
        # country_data=country_obj.search([])
        # state_obj=request.env['res.country.state']
        # state_data=state_obj.search([])
        # countries = request.env['res.country'].sudo().search([])

        # states = request.env['res.country.state'].sudo().search([])

        return request.render('superasiab2b_b2c.b2b_activation',{
            'error':error,
            'default':default,
            # 'countries': countries,
            # 'states': states,
            })
        

  
    @http.route(['/b2baccountactivation'], Method=['POST'], type='http', auth="public", website=True,csrf=False)
    def b2baccountactivation(self, **post):
            error = {}
            default = {}
            current_date = time.strftime("%Y-%m-%d")
            env = request.env(user=SUPERUSER_ID)

            company_name = post.get('company_name')
            contact_name = post.get('contact_name')
            street = post.get('street')
            # city = post.get('city')
            # zipcode = post.get('zipcode')
            # country_id = post.get('country_id')
            # state_id = post.get('state_id')
            email = post.get('email')
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if not (re.search(regex,email)):  
                return request.render('superasiab2b_b2c.invalidemail',{
                    })         
            website = post.get('website')
            mobile = post.get('mobile')
            if mobile:
                mobile = '+1' + mobile

            orm_user = request.env['res.users']
            
            activeuser = orm_user.search([('login','=',email),('active','=',True)])
            if activeuser:
                return request.redirect('/repeat_user')


            internalid = request.env['ir.model.data'].get_object('base','group_user')
            saleid = request.env['ir.model.data'].get_object('sales_team','group_sale_salesman')
            accountid = request.env['ir.model.data'].get_object('account','group_account_invoice')
            superasiaid = request.env['ir.model.data'].get_object('superasiab2b_b2c','group_b2baccount')

            group_list = [internalid.id,saleid.id,accountid.id,superasiaid.id]

            _logger.info('========group_list=========== %s' % group_list)                


            
            vals = {
            'name':company_name,
            'login' : email,
            # 'password':'Admin@1234567',
            'groups_id':[(6,0,group_list)],
            'active':False
            # 'odoobot_state':'disabled'

            }


            
            user_data = orm_user.create(vals)
            user_id = user_data.id

            profile_obj = request.env['res.partner']
            profile_ids=profile_obj.search([('user_id','=',user_data.id)])
            if profile_ids:
                return request.redirect('/accountexist')


            # state_data = ''
            # _logger.info('========state_id======== %s' % state_id)
            # if state_id:

            #         state_obj=request.env['res.country.state']
            #         state_data=state_obj.search([('id','=',int(state_id))])
            #         _logger.info('========state_data======== %s' % state_data)
            #         state_data = state_data.id


            # country_data = ''
            # if country_id:
            #     country_obj=request.env['res.country']
            #     country_data=country_obj.search([('id','=',int(country_id))])
            #     country_data = country_data.id
            

            partner_id = user_data.partner_id
            login = user_data.login

            profile_vals={
            'street': street,
            # 'city': city,
            # 'zip': zipcode,
            # 'country_id':country_data,
            # 'state_id':state_data,
            'email':login,
            'mobile':mobile,
            'website':website,
            'company_type':'company',
            }
            
            partner_id.write(profile_vals)

            
            if partner_id:
                ir_mail_server = request.env['ir.mail_server']
                mail_server_id = ir_mail_server.search([('name','=','Superasia')])
                smtp_user = str(mail_server_id.smtp_user)
                temp_obj = request.env['mail.template']
                template_data = temp_obj.search([('name','=','Account Activation')])
                if template_data:
                    replaced_data= template_data.body_html.replace('${object.company_name}',company_name)
                    replaced_dataone= replaced_data.replace('${object.email}',email)
                    # replaced_datatwo= replaced_dataone.replace('${object.company_name}',company_name)
                    msg = ir_mail_server.build_email(
                    email_from=smtp_user,     
                    email_to=[email],
                    subject="Account Activation",
                    body=replaced_dataone,
                    body_alternative="",
                    object_id=1,
                    subtype='html'
                    )
                    res = mail_server_id.send_email(msg)

            return request.render('superasiab2b_b2c.reset_password_email', {
                'user_data': user_data
            })



    @http.route(['/b2cactivation'], type='http', auth="public", website=True,csrf=False)
    def b2cactivation(self, **post):
        error = {}
        default = {}
        env = request.env(user=SUPERUSER_ID)

        return request.render('superasiab2b_b2c.b2cactivation',{
            'error':error,
            'default':default,
            })
        

  
    @http.route(['/b2caccountactivation'], Method=['POST'], type='http', auth="public", website=True,csrf=False)
    def b2caccountactivation(self, **post):
            error = {}
            default = {}
            current_date = time.strftime("%Y-%m-%d")
            env = request.env(user=SUPERUSER_ID)

            company_name = post.get('company_name')
            email = post.get('email')
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if not (re.search(regex,email)):  
                return request.render('superasiab2b_b2c.invalidemail',{
                    })         

            mobile = post.get('mobile')
            if mobile:
                mobile = '+1' + mobile
            password = post.get('password')
            confirmpassword = post.get('confirmpassword')
            _logger.info('========password=========== %s' % password)                
            _logger.info('========confirmpassword=========== %s' % confirmpassword)                
            if password != confirmpassword:
                return request.render('superasiab2b_b2c.confirmpassword',{
                    })



            orm_user = request.env['res.users']
            
            activeuser = orm_user.search([('login','=',email),('active','=',True)])
            if activeuser:
                return request.redirect('/repeat_user')




            internalid = request.env['ir.model.data'].get_object('base','group_portal')

            group_list = [internalid.id]
            _logger.info('========group_list=========== %s' % group_list)                

            pricelistid = request.env['product.pricelist'].search([('group_id','in',internalid.id)])
            _logger.info('========pricelistid=========== %s' % pricelistid) 
            
            vals = {
            'name':company_name,
            'login' : email,
            'password':confirmpassword,
            'groups_id':[(6,0,group_list)],
            # 'odoobot_state':'disabled'

            }


            
            user_data = orm_user.create(vals)
            user_id = user_data.id

            profile_obj = request.env['res.partner']
            profile_ids=profile_obj.search([('user_id','=',user_data.id)])
            if profile_ids:
                return request.redirect('/accountexist')

            

            partner_id = user_data.partner_id
            login = user_data.login

            profile_vals={
            'email':login,
            'company_type':'company',
            'property_product_pricelist':pricelistid.id
            }
            
            partner_id.write(profile_vals)

            
            if partner_id:
                ir_mail_server = request.env['ir.mail_server']
                mail_server_id = ir_mail_server.search([('name','=','Superasia')])
                smtp_user = str(mail_server_id.smtp_user)
                temp_obj = request.env['mail.template']
                template_data = temp_obj.search([('name','=','Account Activation')])
                if template_data:
                    replaced_data= template_data.body_html.replace('${object.company_name}',company_name)
                    replaced_dataone= replaced_data.replace('${object.email}',email)
                    msg = ir_mail_server.build_email(
                    email_from=smtp_user,     
                    email_to=[email],
                    subject="Account Activation",
                    body=replaced_dataone,
                    body_alternative="",
                    object_id=1,
                    subtype='html'
                    )
                    res = mail_server_id.send_email(msg)

            return request.render('superasiab2b_b2c.reset_password_emailb2c',{
                'user_data': user_data
            })

    
    @http.route(['/acceptconditions'], Method=['POST'], type='http', auth="public", website=True)
    def acceptconditions(self, **post):
        return request.render('superasiab2b_b2c.acceptconditions',{

                })

        

    @http.route(['/repeat_user'], Method=['POST'], type='http', auth="public", website=True)
    def repeat_user(self, **post):

        return request.render('superasiab2b_b2c.repeat_user',{
                })

    @http.route(['/accountexist'], Method=['POST'], type='http', auth="public", website=True)
    def accountexist(self, **post):

        return request.render('superasiab2b_b2c.portaluserexist',{
                })
