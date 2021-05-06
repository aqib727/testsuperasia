# -*- coding: utf-8 -*-
{
    'name': "req_field",

    'summary': """
        Multi-purpose module for superasia housekeeping
        """,
    'description': """
        Make fiew fields mandatory, default filter for users logged in to only see their orders.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'base', 'purchase', 'stock', 'product_expiry', 'stock_barcode', 'stock_landed_costs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/stock_landed_cost.xml',
        'views/prevent_product_creation.xml',
    ],
}
