# Copyright 2020 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo.tests.common import TransactionCase


class TestStockRouting(TransactionCase):

    def setUp(self):
        super(TestStockRouting, self).setUp()

        self.base_company = self.env.ref('base.main_company')

        self.product_product_model = self.env['product.product']
        self.res_users_model = self.env['res.users']
        self.stock_location_model = self.env['stock.location']
        self.stock_move_model = self.env['stock.move']
        self.stock_picking_model = self.env['stock.picking']
        self.stock_quant_model = self.env['stock.quant']

        self.picking_internal = self.env.ref('stock.picking_type_internal')

        today = date.today()

        self.env['res.config.settings'].create({
            'outgoing_routing_strategy': 'location_id.removal_prio',
            'outgoing_routing_order': '0',
            'stock_reservation_strategy': 'quantity',
        }).execute()

        self.stock_A = self.stock_location_model.create({
            'name': 'A',
            'usage': 'internal',
        })

        self.stock_A1 = self.stock_location_model.create({
                'name': 'A-1',
                'usage': 'internal',
                'location_id': self.stock_A.id,
                'removal_prio': 2,
        })

        self.stock_A2 = self.stock_location_model.create({
                'name': 'A-2',
                'usage': 'internal',
                'location_id': self.stock_A.id,
                'removal_prio': 3,
        })

        self.stock_A3 = self.stock_location_model.create({
                'name': 'A-3',
                'usage': 'internal',
                'location_id': self.stock_A.id,
                'removal_prio': 1,
        })

        self.stock_B = self.stock_location_model.create({
            'name': 'B',
            'usage': 'internal',
        })

        self.product_Z = self.product_product_model.create({
            'name': 'Product',
            'type': 'product',
        })

        quant_1 = self.stock_quant_model.create({
            'product_id': self.product_Z.id,
            'location_id': self.stock_A1.id, # prio:2
            'quantity': 15.0,
            'in_date': today,
        })

        quant_2 = self.stock_quant_model.create({
            'product_id': self.product_Z.id,
            'location_id': self.stock_A2.id, # prio:3
            'quantity': 5.0,
            'in_date': today,
        })

        quant_3 = self.stock_quant_model.create({
            'product_id': self.product_Z.id,
            'location_id': self.stock_A3.id, # prio:1
            'quantity': 10.0,
            'in_date': today,
        })

        self.quants = quant_1 + quant_2 + quant_3

    def test_stock_reservation_by_quantity_case1(self):
        quants = self.stock_quant_model._update_reserved_quantity(self.product_Z, self.stock_A, 10)
        for quant, quantity in quants:
            if quant.location_id == self.stock_A1: self.assertEqual(quant.reserved_quantity, 0.0, 'No products should be reserved in A-1 (prio:2)')
            if quant.location_id == self.stock_A2: self.assertEqual(quant.reserved_quantity, 0.0, 'No products should be reserved in A-2 (prio:3)')
            if quant.location_id == self.stock_A3: self.assertEqual(quant.reserved_quantity, 10.0, '10 products should be reserved in A-3 (prio:1)')

    def test_stock_reservation_by_quantity_case2(self):
        quants = self.stock_quant_model._update_reserved_quantity(self.product_Z, self.stock_A, 12)
        for quant, quantity in quants:
            if quant.location_id == self.stock_A1: self.assertEqual(quant.reserved_quantity, 12.0, 'No products should be reserved in A-1 (prio:2)')
            if quant.location_id == self.stock_A2: self.assertEqual(quant.reserved_quantity, 0.0, '12 products should be reserved in A-2 (prio:3)')
            if quant.location_id == self.stock_A3: self.assertEqual(quant.reserved_quantity, 0.0, 'No products should be reserved in A-3 (prio:1)')

    def test_stock_reservation_by_quantity_case3(self):
        quants = self.stock_quant_model._update_reserved_quantity(self.product_Z, self.stock_A, 22)
        for quant, quantity in quants:
            if quant.location_id == self.stock_A1: self.assertEqual(quant.reserved_quantity, 12.0, '12 products should be reserved in A-1 (prio:2)')
            if quant.location_id == self.stock_A2: self.assertEqual(quant.reserved_quantity, 0.0, 'No products should be reserved in A-2 (prio:3)')
            if quant.location_id == self.stock_A3: self.assertEqual(quant.reserved_quantity, 10.0, '10 products should be reserved in A-3 (prio:1)')
