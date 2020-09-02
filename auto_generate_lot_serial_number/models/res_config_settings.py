# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    digits = fields.Integer(related='company_id.digits', readonly=False)
    prefix = fields.Char(related='company_id.prefix', readonly=False)
    auto_generate_lot_serial = fields.Boolean(
        related='company_id.auto_generate_lot_serial', readonly=False,
        string="Auto Generate Lot/Serial Number",
        default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            digits=self.digits,
            prefix=self.prefix,
            auto_generate_lot_serial=self.auto_generate_lot_serial,
        )
        return res
