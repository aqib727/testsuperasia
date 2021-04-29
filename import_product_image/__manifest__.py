# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Product Images from Excel(from Path and URL)',
    'version': '13.0.0.1',
    'summary': 'This apps helps to import product images with product using local path as well as URL',
    'description': """

   """,
    'author': 'Bista',
    'depends': ['base', 'sale_management'],
    'data': [
        "security/ir.model.access.csv",
        "views/import_image_view.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images": ['static/description/Banner.png'],
}
