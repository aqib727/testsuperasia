# -*- coding: utf-8 -*-
{
    'name': 'Signup page with Optional fields such as Address, Phone, Date of Birth & Captcha',
    'summary': 'Signup page with Optional extra fields such as Address, Phone, Date of Birth & Captcha.',
    'description': """
    Signup page with Optional extra fields such as Address, Phone, Date of Birth & Captcha.
    """,
    'author': 'Bista Solutions Pvt. Ltd.',
    'website': 'https://www.bistasolutions.com',
    'license': 'AGPL-3',
    'category': 'Website',
    'version': '0.1',
    'images': ['static/description/banner.jpg'],
    'depends': [
        'auth_signup',
    ],
    'data': [
        'data/ir_config_parameter_data.xml',
        'views/auth_signup_views.xml',
        'views/auth_signup_login_templates.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
    ],
}
