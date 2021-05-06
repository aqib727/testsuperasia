# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPickingReqField(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        if any(self.move_ids_without_package.filtered(lambda n:not n.expiry_date)):
            raise UserError(_('Please fill out all the Expiry dates under the operations tab!'))
        res = super(StockPickingReqField, self).button_validate()
        return res






