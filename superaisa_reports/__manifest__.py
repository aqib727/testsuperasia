# -*- coding: utf-8 -*-
{
    'name': "Superasia Reports",

    'summary': """
              Reports customizations.   
        """,

    'description': """
        Customize reports for superasia.
    """,

    'author': "Bista Solutions",
    'website': "https://www.bistasolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Reports',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'stock', 'purchase', 'product_barcode'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reports/batch_payment_inherit.xml',
        'reports/external_layout_template.xml',
        'reports/invoice_report_inherit.xml',
        'reports/picking_report_inherit.xml',
        'reports/PO_inherit.xml',
        'reports/ckca_check_template_extended.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
