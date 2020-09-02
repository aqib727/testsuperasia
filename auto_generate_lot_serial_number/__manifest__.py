##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Auto Generate Lot/Serial',
    'version': '12.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Auto Generate Lot/Serial Number',
    'description':
    """
    Purchase Setting Configration Auto Generate Lot/Serial Number
    Set True and Set Prefix and Digits Values.
    """,
    'author': 'Bista Solutions Pvt. Ltd.',
    'website': 'http://www.bistasolutions.com',
    'depends': ['purchase', 'stock'],
    'data': [
        'data/lot_serial_sequence_data.xml',
        'security/stock_production_lot_security.xml',
        'views/res_config_settings_view.xml',
        'views/stock_production_lot_view.xml',
        'views/stock_quant_view.xml',
        'views/stock_move.xml',
    ],
    'installable': True,
}
