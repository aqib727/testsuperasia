# Copyright 2019 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    recaptcha_key_site = fields.Char()
    recaptcha_key_secret = fields.Char()

    # def get_recaptcha_sitekey(self):
    #     if self.recaptcha_key_site:
    #         return self.recaptcha_key_site
    #     else:
    #         return "siteKeyMissing"
