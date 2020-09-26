# -*- coding: utf-8 -*-
{
    'name': "Product Barcode",

    'summary': """Product Barcode""",

    'description': """
                Product Barcode customization.
            """,

    'author': "Shawaz Jahangiri",
    'website': "http://www.bistasolutions.com",
    'category': 'Product',
    'version': '1.2',
    'depends': ['base', 'product', 'stock'],
    # always loaded
    'data': [
        'views/product_view.xml',
        'views/stock_barcode_templates.xml',
        'views/stock_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
