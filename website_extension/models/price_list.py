from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class res_groups(models.Model):
    _inherit = 'res.groups'

    e_commerce = fields.Boolean(string="E-commerce")


class PricelistExtension(models.Model):
    _inherit = 'product.pricelist'

    group_id = fields.Many2many('res.groups', string="Account Type", domain="[('e_commerce', '=', True)]")

    def b2c_pricelist_price_calc(self):
        _logger.info("b2c_pricelist_price_calc cron job function")
        pricelist_items = self.env['product.pricelist'].search([('name', 'ilike', 'B2C')], limit=1).item_ids
        # pricelist_product_products = pricelist_items.product_id
        pricelist_product_templates = pricelist_items.product_tmpl_id
        # _logger.info('========B2C pricelist items=========' % pricelist_items)
        product_tmpl_list = self.env['product.template'].search([('is_published', '=', True)])

        for product_tmpl in product_tmpl_list:
            if product_tmpl.uom_id.factor_inv == 1:
                b2c_price = product_tmpl.lst_price
            else:
                unit_price = product_tmpl.lst_price / product_tmpl.uom_id.factor_inv
                b2c_price = unit_price + (unit_price * 0.5)
            if product_tmpl in pricelist_product_templates:
                # _logger.info('======== %s found in B2C pricelist=========' % product_tmpl)
                prod_in_pricelist = next((pricelist_prod for pricelist_prod in pricelist_items if pricelist_prod.product_tmpl_id.id == product_tmpl.id), None)
                _logger.info('======== %s price in B2C pricelist========= %s' % (product_tmpl, prod_in_pricelist.fixed_price))
                if prod_in_pricelist.fixed_price != b2c_price:
                    prod_in_pricelist.write({
                        'fixed_price': b2c_price
                    })
            else:
                # _logger.info('======== %s NOT found in B2C pricelist=========' % product_tmpl)
                _logger.info('======== B2C price for %s is ========= %s' % (product_tmpl, b2c_price))
                self.env['product.pricelist.item'].create({
                    'applied_on': '1_product',
                    'product_tmpl_id': product_tmpl.id,
                    'fixed_price': b2c_price,
                    'base': 'list_price',
                    'compute_price': 'fixed',
                    'pricelist_id': pricelist_items.pricelist_id.id
                })


class PricelistItemExtension(models.Model):
    _inherit = 'product.pricelist.item'

    min_quantity = fields.Integer(
        'Min. Quantity', default=1,
        help="For the rule to apply, bought/sold quantity must be greater "
             "than or equal to the minimum quantity specified in this field.\n"
             "Expressed in the default unit of measure of the product.")
