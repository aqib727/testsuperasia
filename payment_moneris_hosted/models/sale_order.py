# -*- coding: utf-'8' "-*-"

from odoo import api, fields, models

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    # def has_to_be_paid(self, also_in_draft=False, include_draft=False):
    # def has_to_be_paid(self, include_draft=False):
    #     transaction = self.get_portal_last_transaction()
    #     if self.company_id.portal_pay_afterconfirm and self.company_id.portal_confirmation_pay and self.require_payment == True:
    #         return (self.state == 'sent' or (self.state == 'draft' and also_in_draft) or self.state == 'sale') and not self.is_expired and self.require_payment and transaction.state != 'done' and self.amount_total            
    #     return (self.state == 'sent' or (self.state == 'draft' and also_in_draft)) and not self.is_expired and self.require_payment and transaction.state != 'done' and self.amount_total

 # From Odoo Version 11
    payment_transaction_count = fields.Integer(
        string="Number of payment transactions",
        compute='_compute_payment_transaction_count')

    def _compute_payment_transaction_count(self):
        _logger.info("_compute_payment_transaction_count")
        for rec in self:
            transaction_data = self.env['payment.transaction'].sudo().search([('sale_order_ids','in',self.id)])
            _logger.info(len(transaction_data))
            rec.payment_transaction_count = len(transaction_data)
        # transaction_data = self.env['payment.transaction'].read_group([('sale_order_ids', 'in', self.ids)], ['sale_order_ids'], ['sale_order_ids'])
        # mapped_data = dict([(m['sale_order_ids'][0], m['sale_order_id_count']) for m in transaction_data])
        # for order in self:
        #     order.payment_transaction_count = mapped_data.get(order.id, 0)

    def action_view_transaction(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Payment Transactions',
            'res_model': 'payment.transaction',
        }
        if self.payment_transaction_count == 1:
            action.update({
                'res_id': self.env['payment.transaction'].search([('sale_order_ids', 'in', self.ids)]).id,
                'view_mode': 'form',
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('sale_order_ids', '=', self.ids)],
            })
        return action