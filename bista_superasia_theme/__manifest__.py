
{
    'name': "SuperAsia Website Theme",
    'version': '13.0.1.0.0',
    'category': 'Website',
    'summary': 'SuperAsia Website Theme.',
    'description': """SuperAsia Website Theme.""",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': 'www.bistasolutions.com',
    'license': 'AGPL-3',
    "depends": ['base','web','website','portal','bista_web_pwa','superasiab2b_b2c','sale','payment','website_sale','website_form','auth_signup','website_mass_mailing'],
    "data": [
        'views/assets.xml',
        'views/homepage_template.xml',
        'views/header_footer_inherit.xml',
        'views/shop_page_inherit.xml',
        'views/cart_page_inherit.xml',
        'views/contact_us_template_inherit.xml',

    ],

    "installable": True,
    "application":True
}
