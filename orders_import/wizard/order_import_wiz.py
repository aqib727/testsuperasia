# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2017 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields, api, _
import base64
import io
from odoo.exceptions import Warning
from odoo.tools import pycompat, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import logging

logger = logging.getLogger('Import Log')

try:
    import xlrd

    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None


class OrdersImport(models.TransientModel):
    _name = 'orders.import'
    _description = "Import Orders from files"

    def _get_default_date_format(self):
        date_format = self.env['ir.config_parameter'].sudo().get_param('date_format')
        if not date_format:
            date_format = '%y-%m-%d'
        return date_format

    import_file = fields.Binary('File', help="Select file for import orders.")
    import_file_name = fields.Char('File Name')
    is_paid_invoice = fields.Boolean("Is historical invoices?")
    date_format = fields.Char('Date Format', default=_get_default_date_format)

    def import_orders(self):
        """
        Upload csv file data into multiple objects.
        :return:
        """
        payment_term_obj = self.env['account.payment.term']
        product_obj = self.env['product.product']
        partner_obj = self.env['res.partner']
        sale_obj = self.env['sale.order']
        user_obj = self.env['res.users']
        if not self.import_file:
            raise Warning(_("Please attach file then Upload"))
        if not self.import_file_name.endswith('.csv'):
            raise Warning(_("Please upload file only of '.csv' format!"))
        header_seq = ['customer', 'order_date', 'orderID', 'customer_po', 'start_ship_date', 'bill_street',
                      'bill_street2', 'bill_city', 'bill_state', 'bill_postcode', 'bill_country', 'ship_street',
                      'ship_street2', 'ship_city', 'ship_state', 'ship_postcode', 'ship_country', 'phone', 'fax',
                      'email', 'contact', 'rep', 'cancel_date', 'ship_method', 'notes', 'sku', 'qty', 'description',
                      'unit_price', 'unit_discount', 'customer_id', 'payment_terms', 'source', 'externalOrderID',
                      'original_unit_price']
        try:
            csv_data = self.import_file or b''
            csv_data = base64.b64decode(csv_data)
            file_data = pycompat.csv_reader(io.BytesIO(csv_data), delimiter=',')
            i = 1
            data_lst = []
            order_lst = []
            product_lst = []
            for row in file_data:
                if i > 1 and row:
                    if row[2] not in order_lst:
                        order_lst.append(row[2])
                    if row[25] not in product_lst:
                        product_lst.append(row[25])
                    data_lst.append({'customer': row[0], 'order_date': row[1], 'orderID': row[2], 'customer_po': row[3],
                                     'start_ship_date': row[4], 'bill_street': row[5], 'bill_street2': row[6],
                                     'bill_city': row[7], 'bill_state': row[8], 'bill_postcode': row[9],
                                     'bill_country': row[10], 'ship_street': row[11], 'ship_street2': row[12],
                                     'ship_city': row[13], 'ship_state': row[14], 'ship_postcode': row[15],
                                     'ship_country': row[16], 'phone': row[17], 'fax': row[18], 'email': row[19],
                                     'contact': row[20], 'rep': row[21], 'cancel_date': row[22], 'ship_method': row[23],
                                     'notes': row[24], 'sku': row[25], 'qty': float(row[26]), 'description': row[27],
                                     'unit_price': float(row[28]), 'unit_discount': float(row[29]),
                                     'customer_id': row[30],
                                     'payment_terms': row[31], 'source': row[32], 'externalOrderID': row[33],
                                     'original_unit_price': float(row[34])
                                     })
                if i == 1 and row:
                    header = [cell.strip() for cell in row]
                    if header != header_seq:
                        raise Warning(_("Please upload same header sequence as below\n%s" % header_seq))
                i += 1
            existing_order = sale_obj.search([('import_order_id', 'in', order_lst)])
            if existing_order:
                raise Warning(_("Order already exists:\n%s" % existing_order.mapped('import_order_id')))
            existing_product = product_obj.search([])
            existing_product_lst = []
            if existing_product:
                existing_product_lst = existing_product.mapped('default_code')
            nonexisting_product = list(set(product_lst) - set(existing_product_lst))
            if nonexisting_product:
                raise Warning(_("Products not exists:\n%s" % nonexisting_product))
        except Exception as e:
            raise Warning(_(e))

        sale_order_dict = {}
        for val in data_lst:
            partner_id = False
            try:
                if val.get('customer'):
                    # if val.get('email'):
                    #     partner_id = partner_obj.search([('email', '=', val.get('email'))], limit=1)
                    partner_id = partner_obj.search([('name', '=', val.get('customer'))], limit=1)
                    if not partner_id:
                        country_id = self.env['res.country'].search([('name', '=', val.get('bill_country'))], limit=1)
                        state_id = self.env['res.country.state'].search([('code', '=', val.get('bill_state')),
                                                                         ('country_id', '=', country_id.id)], limit=1)
                        partner_id = partner_obj.create({'name': val.get('customer'),
                                                         'street': val.get('bill_street'),
                                                         'street2': val.get('bill_street2'),
                                                         'city': val.get('bill_city'),
                                                         'state_id': state_id and state_id.id or False,
                                                         'country_id': country_id and country_id.id or False,
                                                         'zip': val.get('bill_postcode'),
                                                         'type': 'contact',
                                                         'customer_rank': 1,
                                                         'phone': val.get('phone'),
                                                         # 'fax': val.get('fax'),
                                                         'email': val.get('email')})
                if val.get('orderID'):
                    if val.get('sku'):
                        product_code = val.get('sku').strip()
                        product_data = product_obj.search_read([('default_code', '=', product_code)],
                                                               ['id', 'uom_id'], limit=1)
                        qty = float(val.get('qty'))
                        uom_id = product_data[0].get('uom_id')[0] if product_data \
                            else False
                        unit_price = float(val.get('unit_price', 0.0))
                        product_id = product_data[0].get('id')
                        display_name = val.get('description')
                        order_lines = (0, 0, {'product_id': product_id,
                                              'name': display_name,
                                              'product_uom_qty': qty,
                                              'note': val.get('notes'),
                                              'tax_id': [],
                                              'price_unit': unit_price,
                                              'product_uom': uom_id,
                                              'discount': float(val.get('unit_discount', 0.0))})

                    if val.get('orderID') in sale_order_dict.keys():
                        sale_order_dict.get(val.get('orderID')).get('order_line').append(order_lines)
                    else:
                        payment_term_id = payment_term_obj.search([('name', '=', val.get('payment_terms'))], limit=1)
                        user_id = user_obj.search([('name', '=', val.get('rep'))], limit=1)
                        date_order = datetime.strptime(val.get('order_date'), self.date_format)
                        sale_order_dict.update(
                            {val.get('orderID'): {'partner_id': partner_id and partner_id.id or False,
                                                  'date_order': date_order,
                                                  'note': val.get('notes'),
                                                  'payment_term_id': payment_term_id and payment_term_id.id or False,
                                                  'order_line': [order_lines],
                                                  'import_order_id': val.get('orderID'),
                                                  'client_order_ref': val.get('customer_po'),
                                                  'user_id': user_id and user_id.id or False
                                                  }
                             })
            except Exception as e:
                raise Warning(_(e))

        for order in sale_order_dict.values():
            sale_obj.create(order)
        logger.info("Import Order Done!")
        return True

    def import_invoice(self):
        """
        Upload xlsx file data into objects.
        :return:
        """
        logger.info("Invoice Import Start!")
        partner_obj = self.env['res.partner']
        invoice_obj = self.env['account.move']
        journal_obj = self.env['account.journal']
        account_obj = self.env['account.account']
        if not self.import_file:
            raise Warning(_("Please attach file then Upload"))
        if not self.import_file_name.endswith('.xlsx'):
            raise Warning(_("Please upload file only of '.csv' format!"))
        try:
            excel_sheet_file = self.import_file
            decoded_data = base64.b64decode(excel_sheet_file)
            book = xlrd.open_workbook(file_contents=decoded_data or b'')
            sheet = book.sheet_by_index(0)
            inv_dict = {}
            for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
                if rowx != 1:
                    values = []
                    for colx, cell in enumerate(row, 1):
                        if cell.ctype is xlrd.XL_CELL_NUMBER:
                            is_float = cell.value % 1 != 0.0
                            values.append(
                                str(cell.value)
                                if is_float
                                else str(int(cell.value))
                            )
                        elif cell.ctype is xlrd.XL_CELL_DATE:
                            is_datetime = cell.value % 1 != 0.0
                            # emulate xldate_as_datetime for pre-0.9.3
                            dt = datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                            values.append(
                                dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                if is_datetime
                                else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                            )
                        elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                            values.append(u'True' if cell.value else u'False')
                        elif cell.ctype is xlrd.XL_CELL_ERROR:
                            raise ValueError(
                                _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s") % {
                                    'row': rowx,
                                    'col': colx,
                                    'cell_value': xlrd.error_text_from_code.get(cell.value,
                                                                                _("unknown error code %s") % cell.value)
                                }
                            )
                        else:
                            values.append(cell.value)
                    if values[5] and float(values[7]):
                        inv_lines = []
                        if values[8]:
                            acc_code = values[8].split(' ')[0]
                            account_id = account_obj.search([('code', '=', acc_code)], limit=1)
                            if account_id.user_type_id.type not in ('receivable', 'payable'):
                                inv_lines = (0, 0, {'account_id': account_id and account_id.id or False,
                                                    'name': values[9],
                                                    'quantity': 1,
                                                    'tax_ids': [],
                                                    'price_unit': values[7],
                                                    })
                        if values[5] not in inv_dict.keys():
                            partner_id = partner_obj.search([('name', '=', values[2])], limit=1)
                            if not partner_id:
                                partner_id = partner_obj.create({'name': values[2],
                                                                 'type': 'contact',
                                                                 'customer_rank': 1})
                            if values[0]:
                                journal = values[0]
                            else:
                                journal = 'Customer Invoices'
                            journal_id = journal_obj.search(
                                [('name', '=', journal), ('type', '=', 'sale')], limit=1)
                            inv_type = False
                            if values[3] == 'Invoice':
                                inv_type = 'out_invoice'
                            elif values[3] == 'Credit Memo':
                                inv_type = 'out_refund'
                            elif values[3] == 'Vendor Bill':
                                inv_type = 'in_invoice'
                            elif values[3] == 'Vendor Credit Note':
                                inv_type = 'in_refund'
                            elif values[3] == 'Sales Receipt':
                                inv_type = 'out_receipt'
                            elif values[3] == 'Purchase Receipt':
                                inv_type = 'in_receipt'
                            inv_dict.update(
                                {values[5]: {'partner_id': partner_id and partner_id.id or False,
                                             'invoice_date': values[4],
                                             'invoice_date_due': values[6],
                                             'ref': values[5],
                                             'invoice_line_ids': inv_lines and [inv_lines] or inv_lines,
                                             'type': inv_type,
                                             'journal_id': journal_id and journal_id.id or False,
                                             'state': 'draft',
                                             'invoice_payment_state': 'not_paid',
                                             'name': values[5] if self.is_paid_invoice else '/'
                                             }
                                 })
                        else:
                            if inv_lines:
                                inv_dict.get(values[5]).get('invoice_line_ids').append(inv_lines)
        except Exception as e:
            raise Warning(_(e))
        total_inv = len(inv_dict.keys())
        inv_ids = []
        for vals in inv_dict.values():
            logger.info("INV Count ! %s" % total_inv)
            inv_id = invoice_obj.create(vals)
            inv_ids.append(inv_id.id)
            total_inv -= 1
        if self.is_paid_invoice:
            self._cr.execute("UPDATE account_move set state='posted',invoice_payment_state='paid' where id in %s" % str(
                tuple(inv_ids)))
        logger.info("Import Done!")
        return True
