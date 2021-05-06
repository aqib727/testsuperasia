# from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from odoo.http import request
from odoo import http, models, fields, _
# from odoo import SUPERUSER_ID


class WebsiteExtension(http.Controller):
    @http.route(['/brands'], type='http', auth="public", website=True, csrf=False)
    def brands(self, **post):
        error = {}
        brand_data = []

        # product_attribute_brand = request.env['product.attribute'].search([('name', 'ilike', '%brand%')])
        # for brand in product_attribute_brand.value_ids:
        #     brand_data.append({'name': brand.name})

        return request.render('website_extension.brands_page', {
            'error': error,
            'brand_data': brand_data,
        })
