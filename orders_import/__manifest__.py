# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2017 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Orders Import',
    'version': '1.1',
    'category': 'Sales',
    'description': """
   Import Bulk Sale Order Using from Excel or CSV File.
    """,
    'author': 'Shawaz Jahangiri',
    'website': 'https://www.bistasolutions.com',
    'depends': ['base', 'sale'],
    'data': [
        'wizard/order_import_wiz_view.xml',
        'views/sale_order_line.xml',
    ],
    'installable': True,
    'application': True,
}
