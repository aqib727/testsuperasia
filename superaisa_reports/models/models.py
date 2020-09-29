# -*- coding: utf-8 -*-
#
from odoo import models, fields, api
#
#
# class font_reduce(models.Model):
#     # _name = 'font_reduce.font_reduce'
#     # _description = 'font_reduce.font_reduce'
#     _inherit = 'account.batch.payment'
#
#     count = fields.Integer('Count', compute='_compute_batch_payment_count')
#
#
#     def _compute_batch_payment_count(self):
#         for x in self:
#             x.count = len(x.payment_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_frozen = fields.Boolean('Frozen Item', default=False)
