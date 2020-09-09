# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2019 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class check_bounce_wizard(models.TransientModel):
    _name = "check.bounce.wizard"
    _description = "Check Bounce Wizard"

    bank_charge = fields.Float("Bank Charge")
    account_id = fields.Many2one('account.account', 'Account')
    customer_fees = fields.Float('Customer Fees')
    invoice_ids = fields.Many2many(
        'account.move',
        'account_invoice_payment_rel_bounce',
        'payment_id',
        'invoice_id',
        string="Invoices",
        copy=False)
    account_payment_id = fields.Many2one('account.payment', 'Payment')

    def confirm_check_bounce(self):
        if self.bank_charge < 0 or self.customer_fees < 0:
            raise ValidationError(_('please enter proper amount.'))

        if self.invoice_ids:
            if not self.bank_charge and not self.customer_fees:
                return
            bank_charge_prod_id = self.env.ref('nsf_check.bank_charge1')
            cust_charge_prod_id = self.env.ref('nsf_check.customer_charge1')
            for invoice in self.invoice_ids:
                invoice.bounce_id = self.account_payment_id.id
                for move_line in invoice.line_ids:
                    move_line.remove_move_reconcile()

                invoice_line_lst = []
                if cust_charge_prod_id and self.customer_fees:
                    invoice_line = {
                        'product_id': cust_charge_prod_id.id,
                        'name': cust_charge_prod_id.name,
                        'price_unit': self.customer_fees or 0.0,
                        'account_id': self.account_id.id,
                        'quantity': 1.0,
                        'tax_ids': [(6, 0, cust_charge_prod_id.taxes_id.ids)],
                    }
                    invoice_line_lst.append((0,0,invoice_line))
                if bank_charge_prod_id and self.bank_charge:
                    invoice_line1 = {
                        'product_id': bank_charge_prod_id.id,
                        'name': bank_charge_prod_id.name,
                        'price_unit': self.bank_charge or 0.0,
                        'account_id': self.account_id.id,
                        'quantity': 1.0,
                        'tax_ids': [(6, 0, bank_charge_prod_id.taxes_id.ids)],
                    }
                    invoice_line_lst.append((0,0,invoice_line1))
                new_invoice_vals = {}
                new_invoice_vals.update(
                    {
                        'partner_id': invoice.partner_id.id,
                        'type': 'out_invoice',
                        'invoice_line_ids': invoice_line_lst
                    })
                new_invoice_id = self.env['account.move'].create(
                    new_invoice_vals)
                if new_invoice_id:
                    new_invoice_id.action_post()

            if self.account_payment_id:
                self.account_payment_id.is_check_bounce = True
                move_ids = self.account_payment_id.move_line_ids.mapped('move_id')
                for move in move_ids:
                    move._reverse_moves(
                        [{'ref': _('Reversal of %s') % move.name}], cancel=True)
            self.account_payment_id.state = 'bounced'

        return True
