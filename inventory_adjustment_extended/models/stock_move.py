# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions
# Copyright (C) 2020 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import models, _
from odoo.exceptions import UserError


class Inventory(models.Model):
    _inherit = "stock.inventory"
    _description = "Inventory"

    def action_validate(self):
        return super(Inventory, self.with_context(inventory_adjustment=True)).action_validate()

class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        company_id = self.sudo().company_id
        default_adjustment_account_id = company_id.adjustment_account_id
        if self._context.get('inventory_adjustment', False):
            accounts_data = \
                self.product_id.product_tmpl_id.get_product_accounts()
            if self.location_id.valuation_out_account_id:
                acc_src = self.location_id.valuation_out_account_id.id
            else:
                if default_adjustment_account_id:
                    acc_src = default_adjustment_account_id.id
                else:
                    acc_src = accounts_data['expense'].id

            if self.location_dest_id.valuation_in_account_id:
                acc_dest = self.location_dest_id.valuation_in_account_id.id
            else:
                if default_adjustment_account_id:
                    acc_dest = default_adjustment_account_id.id
                else:
                    acc_dest = accounts_data['expense'].id

            acc_valuation = accounts_data.get('stock_valuation', False)
            if acc_valuation:
                acc_valuation = acc_valuation.id
            if not accounts_data.get('stock_journal', False):
                raise UserError(_(
                    'You don\'t have any stock journal defined on your '
                    'product category, check if you have installed a chart of '
                    'accounts.'))
            if not acc_src:
                raise UserError(_(
                    'Cannot find a stock input account for the product %s. '
                    'You must define one on the product category, or on the '
                    'location, before processing this operation.') % (
                    self.product_id.display_name))
            if not acc_dest:
                raise UserError(_(
                    'Cannot find a stock output account for the product %s. '
                    'You must define one on the product category, or on the '
                    'location, before processing this operation.') % (
                    self.product_id.display_name))
            if not acc_valuation:
                raise UserError(_(
                    'You don\'t have any stock valuation account defined on '
                    'your product category. You must define one before '
                    'processing this operation.'))
            journal_id = accounts_data['stock_journal'].id
            return journal_id, acc_src, acc_dest, acc_valuation
        return super(StockMove, self)._get_accounting_data_for_valuation()
