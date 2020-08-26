# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def export_contact_handshake(self):
        print("hello")
        return True
