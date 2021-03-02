# -*- coding: utf-8 -*-
{
    'name': "Landed Cost Customizations",

    'summary': """
        All the changes related to customizations done to the LC in inventory module
        """,
    'description': """
        Landed Cost totals + Landed cost split by percentages
        """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_landed_costs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_landed_cost.xml',
    ],
}
