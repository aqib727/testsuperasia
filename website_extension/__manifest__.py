# -*- coding: utf-8 -*-
{
    'name': "website_extension",

    'summary': """
        Website Extension module for add extra features for website.
    """,

    'description': """
        Website Extension module for add extra features for website.\n
        Features added:\n
        1. User group wise Price List filtering.
    """,

    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'website',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['website', 'website_sale', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pricelist_view.xml',
        'data/data.xml',
        'views/brands_page.xml',
        'views/product_attribute.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
