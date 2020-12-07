# -*- coding: utf-8 -*-
{
    'name': "Bista Account",

    'summary': """Account Access Rights""",

    'description': """
                Access rights to Own Customer only.
            """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': 'Accounting',
    'version': '1.2',
    'depends': ['base', 'account'],
    # always loaded
    'data': [
        'security/account_security.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
