# Copyright 2020 Bista Solutions
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Progressive web application by Bista",
    "summary": "PWA module for Odoo",
    "version": "13.0.1.0.1",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://www.bistasolutions.com",
    "author": "Bista Solutions",
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "depends": ["web", "mail", "website"],
    "data": [
        "views/webclient_templates.xml",
        "views/website_offline_fallback.xml",
    ],
    "qweb": ["static/src/xml/pwa_install.xml"],
    "images": ["static/description/pwa.png"],
}
