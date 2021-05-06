# -*- coding: utf-8 -*-
{
    # App information

    'name': 'eShipper Odoo Shipping Connector',
    'version': '13.0.1.0',
    'category': 'Website',
    'summary': 'Connect, Integrate & Manage your eShipping Shipping Operations from Odoo',
    'license': 'OPL-1',

    # Dependencies

    'depends': ['delivery', 'mail'],

    # Views

    'data': [
        'data/delivery_eshipper_data.xml',
        'data/delivery_carrier.xml',
        'views/delivery_carrier.xml',
        'views/stock_picking.xml',
        'views/sales_order.xml',
        'views/product_packaging.xml',
        'security/ir.model.access.csv'
    ],
    # Odoo Store Specific

    'images': ['static/description/main_screen.png'],

    # Author

    'author': 'Craftsync Technologies',
    'website': 'https://www.craftsync.com',
    'maintainer': 'Craftsync Technologies',

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '99',
    'currency': 'EUR',

}
