# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions
# Copyright (C) 2020 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Inventory Adjustment Extended',
    "version": "13.0.002",
    'author': 'Bista Solutions Pvt. Ltd.',
    "website": "http://www.bistasolutions.com",
    'depends': ['stock_account', 'repair'],
    'description': """ 
Inventory Adjustment Extended 
=============================
This module sets Expense account on journal items during Inventory Adjustment.
    """,
    'data': [
        'views/res_config_settings_view.xml',
        'views/inventory_adjustment_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
