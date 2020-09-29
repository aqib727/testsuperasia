# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'purchase.order.line'

    brand = fields.Char(string='Brand', related='product_id.x_studio_brand',
                        store=True)


class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    brand = fields.Char(string='Brand', store=True)

    def _select(self):
        return super(PurchaseReport,
                     self)._select() + ", l.brand AS brand"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", l.brand"
