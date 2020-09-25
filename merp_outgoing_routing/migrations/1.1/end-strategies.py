# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

def migrate(cr, version):
	for t in [
		('location_id.name', 'name'),
		('location_id.removal_prio', 'removal_prio'),
		('product_id.name', 'product')
	]:
	    cr.execute('UPDATE res_company SET outgoing_routing_strategy=%s WHERE outgoing_routing_strategy=%s', t)
