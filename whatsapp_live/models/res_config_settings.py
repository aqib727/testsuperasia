# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Website(models.Model):

    _inherit = "website"

    whatsapp_number = fields.Char(string="Number Whatsapp")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_number = fields.Char(related='website_id.whatsapp_number', readonly=False,
                                  help="Attach mobile phone with country code, no plus sign, no special characters")
