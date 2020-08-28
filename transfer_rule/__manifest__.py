# -*- coding: utf-8 -*-
{
    'name': "Product Rule",

    'summary': """Product Rule for Internal Transfer""",

    'description': """
                Configure Product rule to make automatic internal
                transfer from the scheduler.
            """,

    'author': "Shawaz Jahangiri",
    'website': "http://www.bistasolutions.com",
    'category': 'Inventory',
    'version': '1.2',
    'depends': ['base', 'stock'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/transfer_rule_view.xml',
        'data/data.xml',
        'views/res_config_setting_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
