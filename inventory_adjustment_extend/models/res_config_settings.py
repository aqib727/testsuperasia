# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions
# Copyright (C) 2020 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, _, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    adjustment_account_id = fields.Many2one('account.account', related='company_id.adjustment_account_id', copy=False, readonly=False)
    # adjustment_account_id = fields.Many2one(
    #     'account.account', config_parameter="inventory_adjustment_extended.adjustment_account_id")

    @api.model
    def get_values(self):
        ICP = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        res.update(
            adjustment_account_id=int(
                ICP.get_param(
                    'inventory_adjustment_extended.adjustment_account_id',
                    default=False)), )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param(
            'inventory_adjustment_extended.adjustment_account_id',
            self.adjustment_account_id.id or False)
        return res