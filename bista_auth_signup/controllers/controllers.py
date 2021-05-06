from datetime import datetime

from odoo import http, _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from openerp.http import request


class AuthSignupHomeExt(AuthSignupHome):

    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignupHomeExt, self).get_auth_signup_qcontext()
        get_param = request.env['ir.config_parameter'].sudo().get_param
        if get_param('auth_signup_with_phone') == 'True':
            qcontext['auth_signup_with_phone'] = True
        if get_param('auth_signup_with_address') == 'True':
            qcontext['auth_signup_with_address'] = True
        if get_param('auth_signup_with_date_of_birth') == 'True':
            qcontext['auth_signup_with_date_of_birth'] = True
        if get_param('auth_signup_with_captcha') == 'True':
            qcontext['auth_signup_with_captcha'] = True
        qcontext['states'] = request.env["res.country.state"].sudo().search([('country_id', '=', 38)])
        qcontext['countries'] = request.env["res.country"].sudo().search([])
        return qcontext

    def do_signup(self, qcontext):
        """ Replaced the default do_signup base module to add extra fields. """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'phone', 'date_of_birth',
                                                     'street', 'street2', 'city', 'state_id', 'country_id',
                                                     'zip', 'customer_type', 'company_name', 'tax_hst_num',
                                                     'signup_refer', 'news_letter_check')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        # supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        # if request.lang.code in supported_langs:
        #     values['lang'] = request.lang
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        if values.get('date_of_birth'):
            values['date_of_birth'] = datetime.strptime(values.get('date_of_birth'), '%Y-%m-%d')
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        param_obj = request.env['ir.config_parameter'].sudo()
        request.params['auth_login_with_captcha'] = False
        if param_obj.get_param('auth_login_with_captcha') == 'True':
            request.params['auth_login_with_captcha'] = True
        return super(AuthSignupHomeExt, self).web_login(redirect, **kw)
