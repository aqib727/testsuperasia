# Copyright 2020 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from odoo.tools.float_utils import float_compare

import functools


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    removal_prio = fields.Integer(
        related="location_id.removal_prio",
        store=True,
    )

    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        # THIS IS A OVERRIDE STANDARD METHOD
        strategy_order = self.env.user.company_id.outgoing_routing_order

        if removal_strategy == 'location_priority':
            return 'removal_prio %s, id' % (['ASC', 'DESC'][int(strategy_order)])
        return super(StockQuant, self)._get_removal_strategy_order(removal_strategy)

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False):
        """ Updates reserved quantity in quants
        """
        self = self.with_context(reservation_strategy=self.env.user.company_id.stock_reservation_strategy, reservation_quantity=quantity)
        return super(StockQuant, self)._update_reserved_quantity(product_id, location_id, quantity, lot_id, package_id, owner_id, strict)

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        """ Gather (and reorder, if required) quants
        """
        context = dict(self.env.context)
        quants = super(StockQuant, self)._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)

        strategy = self.env.user.company_id.stock_reservation_strategy

        func_reorder = getattr(self, '_reorder_{}'.format(strategy))
        if func_reorder:
            quants = func_reorder(quants, product_id)

        # mom taught us to clean after ourselves
        if context.get('reservation_strategy'):
            del context['reservation_strategy']
        if context.get('reservation_quantity'):
            del context['reservation_quantity']
        self = self.with_context(context)

        return quants

    def _reorder_none(self, quants, product_id):
        """ No reorder, i.e. use out of the box strategy
        """
        return quants

    def _reorder_base(self, quants, product_id):
        """ Reorders quants by location removal priority
        """
        def _r_getattr(obj, attr, *args):
            return functools.reduce(getattr, [obj] + attr.split('.'))

        route = self.env.user.company_id.outgoing_routing_strategy
        order = self.env.user.company_id.outgoing_routing_order

        return quants.sorted(
            key=lambda op: _r_getattr(op, route, 'None'),
            reverse=int(order)
        )

    def _reorder_quantity(self, quants, product_id):
        """ Reorders quants by product quantity in locations and location priority
        """
        default_route = 'name' # i.e. location_id.name

        route = self.env.user.company_id.outgoing_routing_strategy
        order = self.env.user.company_id.outgoing_routing_order

        base, field = route.split('.', 1)
        startegy = field if base in ('location_id') else default_route

        required = self.env.context.get('reservation_quantity', 0)
        rounding = product_id.uom_id.rounding

        locations = {}
        queues = [self.env['stock.quant'], self.env['stock.quant']] # (lprio, hprio)

        for quant in quants:
            locations.setdefault(quant.location_id, []).append(quant)

        for location in sorted(locations,
            key=lambda location: getattr(location, startegy, 'None'),
            reverse=int(order)
        ):
            location_quants = locations.get(location)
            quantity = sum([qt.quantity - qt.reserved_quantity for qt in location_quants])
            priority = float_compare(quantity, required, precision_rounding=rounding) >= 0
            for location_quant in location_quants:
                queues[priority] |= location_quant

        return queues[True] + queues[False]
