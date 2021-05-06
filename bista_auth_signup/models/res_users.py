from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    date_of_birth = fields.Date(related='partner_id.date_of_birth', string='Date of Birth')
    customer_type = fields.Selection([('person', 'Individual'), ('company', 'Company')], string="Customer Type")
    signup_refer = fields.Char(string="How did the customer hear about us?")
    news_letter_check = fields.Boolean(default=False, string="Signed up for newsletter")
    company_name = fields.Char(string="Company Name")
    tax_hst_num = fields.Char(string="Tax/HST Number")
