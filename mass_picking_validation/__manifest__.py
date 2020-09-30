{
    'name': 'Picking Mass Validations',
    'version': '1.0',
    'category': 'Sales',
    'description': """
   Validate multiple Pickings.
    """,
    'author': 'Shawaz Jahangiri',
    'author': 'Bista Solutions',
    'website': 'https://www.bistasolutions.com',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_views.xml',
        'wizard/mass_picking_validation_wiz_view.xml',

    ],
    'installable': True,
    'application': True,
}
