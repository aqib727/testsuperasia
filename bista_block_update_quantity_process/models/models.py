# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (http://www.bistasolutions.com)
#
##############################################################################


from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Popup(models.Model):
    _inherit = 'product.template'


    def action_update_quantity_on_hand(self):
        ''' Added the blocking message as user was doing unauthorized inventory adjustment from product master '''
        raise UserError(_("To update quantity, please go to 'Inventory Adjustments' under the 'Inventory/Operations' tab. "
                                "Contact administrator for further information."))

