# -*- coding: utf-8 -*-
{
    'name': "Super Asia Foods: Follow-Up Report Customization",

    'summary': """
    Remove some information from Follow Up Report and change layout
        """,

    'description': """
        BMU - Task ID: 2371212
        The client is a food distributor of various grocery items. They would like to customize the Followup Report to remove some information and change the layout. 
    """,

    'author': "PS-US Odoo",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Custom Development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'account_followup', 'base'],

    # always loaded
    'data': [
        'views/report_followup_custom.xml',
        # 'views/customer_statements_followup_inherit.xml'
    ],
    'license': 'OEEL-1',
}