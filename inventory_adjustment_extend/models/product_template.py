# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions
# Copyright (C) 2020 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Product Template"

    def get_product_accounts(self, fiscal_pos=None):

        accounts = super(ProductTemplate, self).get_product_accounts(fiscal_pos=fiscal_pos)
        account_id = int(self.env[
            'ir.config_parameter'].sudo().get_param(
            'inventory_adjustment_extended.adjustment_account_id', False))
        default_adjustment_account_id = self.env['account.account']
        if account_id:
            default_adjustment_account_id = self.env['account.account'].browse(
                account_id)

        if default_adjustment_account_id and self._context.get('active_model', False) == self._name:
            accounts['stock_output'] = default_adjustment_account_id


        return accounts