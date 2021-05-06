# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Block Update Quantity Process From Product',
    'version': '13.0.001',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Block Update Quantity Process From Product',
    'description': """
       Added a blocking message on Update Quantity button at product master to prevent unauthorized inventory adjustment.
    """,
    'author': 'Bista Solutions Pvt. Ltd.',
    'website': 'http://www.bistasolutions.com',
    'depends': ['base', 'stock'],
    'data': [
        #'wizard/wizard_confirm_sale_view.xml',
        #'views/sale_view.xml',
        'views/stock_quant.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
#This is a comment!!!!!!!!!!!!!!!!!!!!!!!!!!!
}
