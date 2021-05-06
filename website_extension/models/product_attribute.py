from odoo import fields, models, api


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    image = fields.Binary('Image', help="Upload attribute image.")
