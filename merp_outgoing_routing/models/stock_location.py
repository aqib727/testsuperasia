# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = "stock.location"

    removal_prio = fields.Integer(
        string='Removal Priority',
        default=0,
    )

    strategy_sequence = fields.Integer(
        string='Sequence',
        help='Sequence based on warehouse location outgoing strategy/order',
        compute='_compute_outgoing_strategy_sequence',
        store=False,
    )

    def _compute_outgoing_strategy_sequence(self):
        """
        """
        strategy = self.env.user.company_id.outgoing_routing_strategy
        strategy_order = self.env.user.company_id.outgoing_routing_order

        base, field = strategy.split('.', 1)
        if base not in ('location_id') and field not in self:
            return

        res = self.sudo().search([], order='{} {}'.format(
            field, ['asc', 'desc'][int(strategy_order)]))
        processed = self.env['stock.location']
        for sequence, location in enumerate(res):
            if location not in self:
                continue
            location.strategy_sequence = sequence
            processed |= location
        remaining_locations = self - processed
        max_seq = len(res)
        for remaining in remaining_locations:
            remaining.strategy_sequence =  max_seq

    @api.onchange('location_id')
    def _onchange_parent_location(self):
        """ Set location's parent removal priority by default
        """
        if self.location_id:
            self.removal_prio = self.location_id.removal_prio
