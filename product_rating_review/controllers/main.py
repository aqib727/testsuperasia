# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.mail import PortalChatter
from datetime import date


class PortalChatter(PortalChatter):

    @http.route(['/mail/chatter_post'], type='http', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        """get reviews from website products"""
        params = kw.copy()
        uid = request.session.uid
        user = request.env['res.users'].browse(uid)
        msg_data = super(PortalChatter, self).portal_chatter_post(
            res_model=res_model, res_id=res_id, message=message, **params)
        product = request.env['product.template'].browse(res_id)
        rating = float(kw.get('rating_value')) if kw.get('rating_value') else 0
        # store data from website at product backend
        request.env['customer.review'].sudo().create({
            'customer_id': uid,
            'name': message,
            'date': date.today(),
            'email': user.email,
            'product_id': product.id,
            'rating': rating / 2,
        })
        return msg_data