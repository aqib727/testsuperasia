{
    'name': 'B2B and B2C Activation',
    'version': '1.0',
    'category': '',
    'description': "",
    'website': '',
    'summary': '',
    'author':'Bista Solutions - Archana Prasad',
    'depends': [
        'base','portal','sale','product','website','website_sale',
    ],
    'data': [
            'security/access_rights.xml',
            'security/ir.model.access.csv',
            'data/data.xml',
            'views/portal_template.xml',
            'views/sales_order.xml',
            'views/inherited_product_template_meta_fields.xml',
            'views/website_config_settings.xml',
            ],

        'qweb': [

    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
