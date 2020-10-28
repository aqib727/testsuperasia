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
    'depends': ['base', 'product', 'stock', 'stock_barcode'],
    # always loaded
    'data': [
        'views/product_view.xml',
        'views/stock_barcode_templates.xml',
        'views/stock_location.xml',
        'views/stock_picking_views.xml',
    ],
    'qweb': [
        "static/src/xml/qweb_templates.xml",],
    # only loaded in demonstration mode
    'demo': [],
}
