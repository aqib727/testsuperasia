# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    portal_pay_afterconfirm = fields.Boolean(related='company_id.portal_pay_afterconfirm', string='Allow Online Payment After Sale Confirm', readonly=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        portal_pay_afterconfirm = params.get_param('portal_pay_afterconfirm', default=False)
        res.update(portal_pay_afterconfirm=portal_pay_afterconfirm)
        return res

    def set_values(self):
        super(ResConfigSettingsInherit, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("portal_pay_afterconfirm",  self.portal_pay_afterconfirm)

class ResCompanyInherit(models.Model):
    _inherit = "res.company"

    portal_pay_afterconfirm = fields.Boolean(string='Allow Online Payment After Sale Confirm')