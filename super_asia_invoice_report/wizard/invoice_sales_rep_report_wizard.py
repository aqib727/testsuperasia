# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2020 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import xlsxwriter, base64
import tempfile


class AccountSalesRepReport(models.TransientModel):
    _name = 'account.invoice.sales.rep.report'
    _description = 'XLS Report Temp1'

    user_id = fields.Many2one('res.users', string='User', required=True)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    report_data = fields.Binary()

    type = fields.Selection(selection=[
        ('sal_report', 'Sales Rep Wise Invoice Report'),
        ('age_report', 'Sales Rep Wise Aging Report'),
        ('close_report', 'Sales Rep Wise Closing Report'),
        ], string='Report Type', required=True, store=True, index=True,
        readonly=True, default="sal_report", change_default=True)

    def generate_xlsx_report(self, data):
        file_name = 'SuperAsiaSalesReport.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + file_name)
        # sheet = workbook.add_worksheet("Vendor Stock Report")

        center_format = workbook.add_format({'align': 'center', 'border': 1})
        left_format = workbook.add_format({'align': 'left', 'border': 1})
        right_format = workbook.add_format({'align': 'right', 'border': 1})
        # Start Invoice Report
        invoice_data = data.get('invoice_data')
        if invoice_data:
            header_format = workbook.add_format(
                {'bg_color': '#5B9DB5', 'font_color': '#FFFFFF', 'bold': True,
                 'align': 'center', 'font_size': 11, 'border': 1})
            sheet = workbook.add_worksheet('Invoice Data')
            sheet.set_column('A:P', 15)
            sheet.write(0, 0, 'Sales Rep', header_format)
            sheet.write(0, 1, 'Type', header_format)
            sheet.write(0, 2, 'Doc. Date', header_format)
            sheet.write(0, 3, 'Month', header_format)
            sheet.write(0, 4, 'Year', header_format)
            sheet.write(0, 5, 'Doc. No.', header_format)
            sheet.write(0, 6, 'Customer', header_format)
            sheet.write(0, 7, 'Customer #', header_format)
            sheet.write(0, 8, 'Customer Name', header_format)
            sheet.write(0, 9, 'City', header_format)
            sheet.write(0, 10, 'Product', header_format)
            sheet.write(0, 11, 'Product Category', header_format)
            sheet.write(0, 12, 'Brand', header_format)
            sheet.write(0, 13, 'SKU', header_format)
            sheet.write(0, 14, 'QTY', header_format)
            sheet.write(0, 15, 'Size', header_format)
            sheet.write(0, 16, 'Unit', header_format)
            sheet.write(0, 17, 'Amount', header_format)
            i = 1
            for inv in invoice_data:
                sheet.write(i, 0, inv.get('user_id', ''), left_format)
                sheet.write(i, 1, inv.get('type', ''), left_format)
                sheet.write(i, 2, inv.get('date', ''), center_format)
                sheet.write(i, 3, inv.get('month', ''), center_format)
                sheet.write(i, 4, inv.get('year', ''), center_format)
                sheet.write(i, 5, inv.get('number', ''), center_format)
                sheet.write(i, 6, inv.get('code_with_customer', ''), left_format)
                sheet.write(i, 7, inv.get('cust_code', ''), left_format)
                sheet.write(i, 8, inv.get('customer_name', ''), left_format)
                sheet.write(i, 9, inv.get('city'), left_format)
                sheet.write(i, 10, inv.get('product', ''), left_format)
                sheet.write(i, 11, inv.get('category', ''), left_format)
                sheet.write(i, 12, inv.get('brand', ''), left_format)
                sheet.write(i, 13, inv.get('sku', ''), center_format)
                sheet.write(i, 14, inv.get('qty', ''), right_format)
                sheet.write(i, 15, inv.get('size', ''), center_format)
                sheet.write(i, 16, inv.get('unit', ''), center_format)
                sheet.write(i, 17, inv.get('price_unit', ''), right_format)
                i = i + 1
        # Invoice Report End
        # Start Aged Report
        aged_data = data.get('aged_data')
        if aged_data:
            header_format1 = workbook.add_format(
                {'bg_color': '#D0D0D0', 'font_color': '#000000', 'bold': True,
                 'align': 'center', 'font_size': 11, 'border': 1})
            yellow_format = workbook.add_format(
                {'bg_color': '#FFFF00', 'font_color': '#000000', 'bold': True,
                 'align': 'right', 'font_size': 11, 'border': 1})
            red_format = workbook.add_format({'align': 'right','font_color': '#FF0000', 'border': 1})
            sheet1 = workbook.add_worksheet('Aged Data')
            sheet1.set_column('A:G', 15)
            sheet1.set_column('H:H', 20)
            sheet1.write(0, 0, 'Sales Rep', header_format1)
            sheet1.write(0, 1, 'Name', header_format1)
            sheet1.write(0, 2, '1-30 Days', header_format1)
            sheet1.write(0, 3, '31-60 Days', header_format1)
            sheet1.write(0, 4, '61-90 Days', header_format1)
            sheet1.write(0, 5, '> 90 Days', header_format1)
            sheet1.write(0, 6, '> 120 Days', header_format1)
            sheet1.write(0, 7, 'Amount Outstanding', header_format1)

            i = 1
            for inv in aged_data:
                sheet1.write(i, 0, inv.get('rep'), left_format)
                sheet1.write(i, 1, inv.get('name'), left_format)
                if inv.get('m1') and inv.get('m1') > 0:
                    sheet1.write(i, 2, inv.get('m1'), yellow_format)
                elif inv.get('m1') and inv.get('m1') < 0:
                    sheet1.write(i, 2, inv.get('m1'), red_format)
                else:
                    sheet1.write(i, 2, inv.get('m1'), right_format)
                if inv.get('m2') and inv.get('m2') > 0:
                    sheet1.write(i, 3, inv.get('m2'), yellow_format)
                elif inv.get('m2') and inv.get('m2') < 0:
                    sheet1.write(i, 3, inv.get('m2'), red_format)
                else:
                    sheet1.write(i, 3, inv.get('m2'), right_format)
                if inv.get('m3') and inv.get('m3')> 0:
                    sheet1.write(i, 4, inv.get('m3'), yellow_format)
                elif inv.get('m3') and inv.get('m3') < 0:
                    sheet1.write(i, 4, inv.get('m3'), red_format)
                else:
                    sheet1.write(i, 4, inv.get('m3'), right_format)
                if inv.get('m4') and inv.get('m4') > 0:
                    sheet1.write(i, 5, inv.get('m4'), yellow_format)
                elif inv.get('m4') and inv.get('m4') < 0:
                    sheet1.write(i, 5, inv.get('m4'), red_format)
                else:
                    sheet1.write(i, 5, inv.get('m4'), right_format)
                if inv.get('m5') and inv.get('m5') > 0:
                    sheet1.write(i, 6, inv.get('m5'), yellow_format)
                elif inv.get('m5') and inv.get('m5') < 0:
                    sheet1.write(i, 6, inv.get('m5'), red_format)
                else:
                    sheet1.write(i, 6, inv.get('m5'), right_format)
                sheet1.write(i, 7, inv.get('amt_out_std'), right_format)
                i = i + 1
        # End Aged Report
        # Start Closing Report
        closing_data = data.get('closing_data')
        if closing_data:
            header_format2 = workbook.add_format(
                {'bg_color': '#44546A', 'font_color': '#FFFFFF', 'bold': True,
                 'align': 'center', 'font_size': 11})
            sheet = workbook.add_worksheet('Closing Data')
            sheet.set_column('A:K', 15)
            sheet.write(0, 0, 'Sales Rep', header_format2)
            sheet.write(0, 1, 'Transaction Type', header_format2)
            sheet.write(0, 2, 'Document Number', header_format2)
            sheet.write(0, 3, 'Customer/Project', header_format2)
            sheet.write(0, 4, 'Date', header_format2)
            sheet.write(0, 5, 'Invoice Month', header_format2)
            sheet.write(0, 6, 'Invoice Year', header_format2)
            sheet.write(0, 7, 'Date Closed', header_format2)
            sheet.write(0, 8, 'Closing Month', header_format2)
            sheet.write(0, 9, 'Closing Year', header_format2)
            sheet.write(0, 10, 'Days', header_format2)

            i = 1
            for inv in closing_data:
                sheet.write(i, 0, inv.get('user_id', ''), left_format)
                sheet.write(i, 1, inv.get('type', ''), left_format)
                sheet.write(i, 2, inv.get('number', ''), left_format)
                sheet.write(i, 3, inv.get('customer_name', ''), left_format)
                sheet.write(i, 4, inv.get('date', ''), right_format)
                sheet.write(i, 5, inv.get('month', ''), right_format)
                sheet.write(i, 6, inv.get('year', ''), right_format)
                sheet.write(i, 7, inv.get('close_date', 'Open'), right_format)
                sheet.write(i, 8, inv.get('close_month', ''), right_format)
                sheet.write(i, 9, inv.get('close_year', ''), right_format)
                sheet.write(i, 10, inv.get('diff_days', ''), right_format)
                i = i + 1
            # End Closing Report
        workbook.close()
        superasia_file = base64.b64encode(open('/tmp/' +
                                                 file_name, 'rb').read())
        if superasia_file:
            self.write({'report_data': superasia_file})
        filename = 'SuperAsia Sales Report.xlsx'
        return {
            'name': 'SuperAsia Report',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=account.invoice.sales.rep.report&id=" + str(
                self.id) + "&filename_field=filename&field=report_data&download=true&filename=" + filename,
            'target': 'self',
        }

    def invoice_report(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError(_("From date can not be higher than to date."))
        data = {'invoice_data': [], 'aged_data': [], 'closing_data': []}
        payment_env = self.env['account.payment']
        # Start Aged Data
        if self.type == 'age_report':
            query = """
                SELECT i.name,sum(m5) as m5, sum(m4) as m4,sum(m3) as m3, sum(m2) as m2, sum(m1) as m1 from
                    (SELECT cust.name as name,
                        CASE 
                            WHEN aml.date_maturity <= current_date - interval '1' day 
                            AND aml.date_maturity >= current_date - interval '30' day
                            THEN sum(aml.debit-aml.credit) END as m1,
                        CASE 
                            WHEN aml.date_maturity <= current_date - interval '31' day 
                            AND aml.date_maturity >= current_date - interval '60' day
                            THEN sum(aml.debit-aml.credit) END as m2,
                        CASE 
                            WHEN aml.date_maturity <= current_date - interval '61' day 
                            AND aml.date_maturity >= current_date - interval '90' day
                            THEN sum(aml.debit-aml.credit) END as m3,
                        CASE 
                            WHEN aml.date_maturity <= current_date - interval '91' day 
                            AND aml.date_maturity >= current_date - interval '120' day
                            THEN sum(aml.debit-aml.credit) END as m4,
                        CASE 
                            WHEN aml.date_maturity < current_date - interval '120' day
                            THEN sum(aml.debit-aml.credit)
                            END as m5
                
                    FROM 
                        account_move_line aml
                        left join account_move am on aml.move_id=am.id
                        left join res_partner cust on aml.partner_id=cust.id
                        left join account_account ac on aml.account_id=ac.id
                        left join account_account_type act on ac.user_type_id=act.id
                    WHERE
                    am.invoice_user_id=%s
                    AND act.type='receivable'
                    AND aml.reconciled=False
                    AND am.company_id=%s
                    AND am.partner_id is not null
                    AND am.state not in ('cancel', 'draft')
                    AND aml.date <= '%s'
                    GROUP BY
                        cust.id,
                        aml.date_maturity) as i
                GROUP BY
                    i.name
                """ % (self.user_id.id, self.company_id.id, self.date_to)
            # query = """
            # SELECT
            #     cust.name
            # FROM
            #     account_move_line aml
            # left join account_move am on aml.move_id=am.id
            # left join res_partner cust on aml.partner_id=cust.id
            # left join account_account ac on aml.account_id=ac.id
            # left join account_account_type act on ac.user_type_id=act.id
            # WHERE
            #     am.invoice_user_id=%s
            #     AND am.type='out_invoice'
            #     AND act.type='receivable'
            #     AND aml.reconciled=False
            #     AND aml.debit > 0
            #     AND am.company_id=%s
            #     AND am.partner_id is not null
            #     AND am.state not in ('cancel', 'draft')
            #     AND aml.date <= %s
            # GROUP BY
            #     cust.id
            # """ % (self.user_id.id, self.company_id.id, self.date_to)
            self._cr.execute(query)
            aged_data = self._cr.dictfetchall()
            for adata in aged_data:
                amt_out_std = (adata.get('m1') or 0.0) + (adata.get('m2') or 0.0) + \
                              (adata.get('m3') or 0.0) + (adata.get('m4') or 0.0) + \
                              (adata.get('m5') or 0.0)
                data['aged_data'].append({'rep': self.user_id.name,
                                          'name': adata.get('name'),
                                          'm1': adata.get('m1'),
                                          'm2': adata.get('m2'),
                                          'm3': adata.get('m3'),
                                          'm4': adata.get('m4'),
                                          'm5': adata.get('m5'),
                                          'amt_out_std': amt_out_std})
        # End Aged Data
        invoice_ids = self.env['account.move'].search([
            ('type', '=', 'out_invoice'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '!=', 'cancel'),
            ('company_id', '=', self.company_id.id),
            ('invoice_user_id', '=', self.user_id.id)])
        for inv in invoice_ids:
            year = inv.date.year
            month = inv.date.month
            invoice_date = inv.date.strftime("%m/%d/%Y")
            # Invoice Data
            if self.type == 'sal_report':
                for line in inv.invoice_line_ids:
                    data['invoice_data'].append({
                        'user_id': inv.invoice_user_id.name or '',
                        'type': 'invoice',#inv.type,
                        'date': invoice_date or '',
                        'month': month or '',
                        'year': year or '',
                        'number': inv.name or '',
                        'code_with_customer': inv.partner_id.name or '',
                        'cust_code': inv.partner_id.name.split() and inv.partner_id.name.split()[0] or '',
                        'customer_name': inv.partner_id.name or '',
                        'city': inv.partner_id.city or '',
                        'product': line.product_id.name or '',
                        'category': line.product_id.categ_id.name or '',
                        'brand': line.product_id.product_tmpl_id.x_studio_brand or '',
                        'sku': line.product_id.default_code or '',
                        'qty': line.quantity or '',
                        'size': line.product_id.x_studio_size or '',
                        'unit': line.product_uom_id.name or '',
                        'price_unit': line.price_unit})
            # Closing Data
            if self.type == 'close_report':
                all_payments = payment_env.search([
                    ('state', '!=', 'cancelled'),
                    ('payment_type', '=', 'inbound'),
                    ('partner_type', '=', 'customer')])
                vals = {
                    'user_id': inv.invoice_user_id.name,
                    'type': 'invoice',
                    'number': inv.name,
                    'customer_name': inv.partner_id.name,
                    'date': invoice_date,
                    'month': month,
                    'year': year
                }

                if all_payments:
                    payments_dt = all_payments.filtered(
                        lambda i: inv.id in i.invoice_ids.ids).mapped(
                        'payment_date')

                    if payments_dt:
                        close_date = max(payments_dt)
                        closing_date = close_date.strftime("%m/%d/%Y")
                        # current_date =
                        diff_days = close_date - inv.date
                        vals.update({'close_date': closing_date,
                                     'close_month': close_date.month,
                                     'close_year': close_date.year,
                                     'diff_days': diff_days.days})
                    else:
                        curr_date = datetime.today().date()
                        diff_days = curr_date - inv.date
                        vals.update({'diff_days': diff_days.days})




                data['closing_data'].append(vals)
            # Closing Data End
            # inv.type,
        if not data.get('invoice_data') and not data.get('aged_data') and \
                not data.get('closing_data'):
            raise UserError(_("No Record found on selected date."))
        return data

    def sales_rep_invoice_report_excel(self):
        data = self.invoice_report()
        return self.generate_xlsx_report(data)


    def sales_rep_invoice_aging_report_excel(self):
        data = self.invoice_report()
        return self.generate_xlsx_report(data)

    def sales_rep_invoice_closing_report_excel(self):
        data = self.invoice_report()
        data = {'closing_data': data.get('closing_data')}
        return self.generate_xlsx_report(data)
