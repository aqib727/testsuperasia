# -*- coding: utf-8 -*-
{
    'name': "Super Asia Foods: Import/Export Data",

    'summary': """
    Import/export of csv files from a network folder for data update between Odoo and Handshake
        """,

    'description': """
        CIC - Task ID: 2287562
        The client is a food distributor of various grocery items. The client uses HandShake, a sales order management app for wholesale. HandShake’s front-end is used by the client’s salesperson on a mobile device to place orders while visiting a retail store and thereby making an order in the back-end system. HandShake’s backend has the following information - Quotations, Customer details, Product details. The client wants to integrate HandShake with Odoo, by doing an import/export of csv files from a network folder for data update between the systems. 
    """,

    'author': "PS-US Odoo",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Custom Development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'stock', 'google_drive'],

    # always loaded
    'data': [
        'data/actions.xml',
        # 'views/templates.xml',
    ],
    'license': 'OEEL-1',
}
