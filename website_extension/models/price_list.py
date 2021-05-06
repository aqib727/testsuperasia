from odoo import fields, models, api


class res_groups(models.Model):
    _inherit = 'res.groups'

    e_commerce = fields.Boolean(string="E-commerce")


class PricelistExtension(models.Model):
    _inherit = 'product.pricelist'

    group_id = fields.Many2many('res.groups', string="Account Type", domain="[('e_commerce', '=', True)]")


class PricelistItemExtension(models.Model):
    _inherit = 'product.pricelist.item'

    min_quantity = fields.Integer(
        'Min. Quantity', default=1,
        help="For the rule to apply, bought/sold quantity must be greater "
             "than or equal to the minimum quantity specified in this field.\n"
             "Expressed in the default unit of measure of the product.")
