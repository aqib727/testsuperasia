# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2019 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'NSF Check',
    'version': '1.0',
    'category': 'Accounting',
    'summary': "This Module provide check  bounce functionality.",
    'description': """
        This Module provide check  bounce functionality."
    """,
    'website': 'https://www.bistasolutions.com',
    'author': 'Bista Solutions',
    'images': [],
    'depends': ['account'],
    'data': [
            'views/payment_view.xml',
            'data/product_data.xml',
            'wizard/check_bounce_view.xml',
    ],
    'application': True,
    'installable': True,
}
