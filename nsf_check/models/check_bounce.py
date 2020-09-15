# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2019 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


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


class AccountMove(models.Model):
    _inherit = "account.move"

    bounce_id = fields.Many2one('account.payment', string="Bounce",copy=False)

    @api.constrains('ref', 'type', 'partner_id', 'journal_id', 'invoice_date')
    def _check_duplicate_supplier_reference(self):
        moves = self.filtered(
            lambda move: move.is_purchase_document() and move.ref)
        if not moves:
            return

        self.env["account.move"].flush([
            "ref", "type", "invoice_date", "journal_id",
            "company_id", "partner_id", "commercial_partner_id",
        ])
        self.env["account.journal"].flush(["company_id"])
        self.env["res.partner"].flush(["commercial_partner_id"])

        # /!\ Computed stored fields are not yet inside the database.
        self._cr.execute('''
                SELECT move2.id
                FROM account_move move
                JOIN account_journal journal ON journal.id = move.journal_id
                JOIN res_partner partner ON partner.id = move.partner_id
                INNER JOIN account_move move2 ON
                    move2.ref = move.ref
                    AND move2.company_id = journal.company_id
                    AND move2.commercial_partner_id = partner.commercial_partner_id
                    AND move2.type = move.type
                    AND (move.invoice_date is NULL OR move2.invoice_date = move.invoice_date)
                    AND move2.id != move.id
                WHERE move.id IN %s
            ''', [tuple(moves.ids)])
        duplicated_moves = self.browse([r[0] for r in self._cr.fetchall()])
        if duplicated_moves:
            raise ValidationError(_(
                'Duplicated vendor reference detected. You probably encoded twice the same vendor bill/credit note:\n%s') % "\n".join(
                duplicated_moves.mapped(
                    lambda m: "%(partner)s - %(ref)s" % {
                        'ref': m.ref, 'partner': m.partner_id.display_name,})
            ))


