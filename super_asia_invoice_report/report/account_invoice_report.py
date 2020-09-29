# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    brand = fields.Char(string='Brand', related='product_id.x_studio_brand',
                        store=True)


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    brand = fields.Char(string='Brand', store=True)

    def _select(self):
        return super(AccountInvoiceReport,
                     self)._select() + ", line.brand AS brand"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", line.brand"
