# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    brand = fields.Char(string='Brand', related='product_id.x_studio_brand',
                        store=True)


class SaleReport(models.Model):
    _inherit = 'sale.report'

    brand = fields.Char(string='Brand', store=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):

        fields['brand'] = ', l.brand AS brand'
        groupby += ',l.brand'
        return super(SaleReport, self)._query(with_clause=with_clause,
                                              fields=fields,
                                              groupby=groupby,
                                              from_clause=from_clause)