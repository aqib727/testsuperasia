# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2019 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import fields, models, _


class account_payment(models.Model):
    _inherit = "account.payment"

    is_check_bounce = fields.Boolean('Check Bounce',copy=False)
    state = fields.Selection(selection_add=[('bounced', 'Bounced')])

    def check_bounce(self):
        view_id = self.env.ref('nsf_check.view_check_bounce_form')
        return {
            'name': _("Check Bounce"),
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'check.bounce.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'default_invoice_ids': self.reconciled_invoice_ids.ids,
                        'default_account_payment_id': self.id}
        }


class account_move(models.Model):
    _inherit = "account.move"

    bounce_id = fields.Many2one('account.payment', string="Bounce",copy=False)
