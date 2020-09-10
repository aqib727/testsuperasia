from odoo import api, fields, models
import xlsxwriter, base64
from datetime import datetime
import tempfile
import itertools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WizVendorStockReport(models.TransientModel):
    _name = "wiz.vendor.stock.report"
    _description = "Vendor Stock Excel Report"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    report_data = fields.Binary()
    odoo_Forecast = fields.Boolean("Show Odoo Forecast Qty?")

    def generate_report(self):
        # purchase_order_obj = self.env['purchase.order']
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        tmp = tempfile.NamedTemporaryFile(prefix="xlsx", delete=False)
        # file_path = tmp.name
        file_name = 'Vendor Stock Report.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + file_name)
        sheet = workbook.add_worksheet("Vendor Stock Report")
        format = workbook.add_format({'align': 'center'})
        format.set_text_wrap()
        font_bold = workbook.add_format(
            {'align': 'center', 'bg_color': '#B8B8B8'})
        font_bold.set_bold()
        font_bold.set_text_wrap()
        row_frmt = workbook.add_format({'align': 'center'})
        row_frmt.set_font_size(10)
        # money_frmt = workbook.add_format({'num_format': '0.00',
        #                                   'align': 'right'})
        title_format = workbook.add_format({
            'bold': 1,
            # 'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            # 'fg_color': 'white'
        })
        total_format = workbook.add_format({
            'num_format': '0.00',
            'bold': 1,
            # 'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            # 'fg_color': 'white'
        })
        right_format = workbook.add_format({'align': 'right'})
        value_format = workbook.add_format({'align': 'left', 'text_wrap': True})
        only_bold = workbook.add_format({'bold': True, 'align': 'left', 'text_wrap': True})
        #         sheet.freeze_panes(6, 3)

        # sheet.set_column('E:E', 18)
        # sheet.set_column('F:F', 40)
        # sheet.set_column('G:N', 18)
        # sheet.set_column('O:W', 35)

        rows = 0
        cols = 0
        # report_title = 'Vendor Stock Report'
        # sheet.merge_range(rows, cols, rows, cols + 6,
        #                   report_title, title_format)

        existing_product_list = []
        vendor_list = self.env['product.supplierinfo'].search([('product_tmpl_id.qty_available', '!=', 0.0)],
                                                              order='name').mapped('name')
        vendor_list += stock_obj.search([('partner_id', '!=', False),
                                         ('picking_type_code', '=', 'incoming'),
                                         ('state', 'not in', ('cancel', 'done'))],
                                        order='partner_id').mapped('partner_id')
        # vendor_list += purchase_order_obj.search([('partner_id', '!=', False),
        #                                           ('is_shipped', '!=', True),
        #                                           ('state', 'in', ('purchase', 'done'))],
        #                                          order='partner_id').mapped('partner_id')
        data = {}
        # rows += 2

        # vendor_list = self.env['res.partner'].search([('name','=','10689068 CANADA INC.')])
        po_move_ids = []
        for vendor in list(set(vendor_list)):
            data.update({vendor: {}})
            purchase_order = stock_obj.search([('partner_id', 'in', vendor.ids),
                                               ('picking_type_code', '=', 'incoming'),
                                               ('state', 'not in', ('cancel', 'done'))],
                                              order='partner_id')

            for pl in purchase_order.mapped('move_lines'):
                if pl.picking_id.purchase_id and not pl.origin_returned_move_id:
                    po_move_ids.append(pl.id)
                    existing_product_list.append(pl.product_id.id)
                    if pl.picking_id not in data.get(vendor).keys():
                        data.get(vendor).update({pl.picking_id: {pl.product_id: pl.product_uom_qty}})
                    else:
                        data.get(vendor).get(pl.picking_id).update({pl.product_id: pl.product_uom_qty})
            if not data.get(vendor):
                product_tmpl_ids = self.env['product.supplierinfo'].search([('name', '=', vendor.id),
                                                                            ('product_tmpl_id.qty_available', '!=',
                                                                             0.0)],
                                                                           order='name').mapped('product_tmpl_id')
                product_ids = self.env['product.product'].search([('product_tmpl_id', 'in', product_tmpl_ids.ids),
                                                                  ('product_tmpl_id.qty_available', '!=', 0.0)],
                                                                 order='name')
                data.get(vendor).update({stock_obj: {}})
                for prod in product_ids:
                    data.get(vendor).get(stock_obj).update({prod: 0.0})
                    existing_product_list.append(prod.id)

        for vendor, value in data.items():
            is_val = len(list([v for v in value.values() if v]))
            if not is_val:
                continue
            # sheet.write(rows, cols, 'Vendor', title_format)
            # sheet.merge_range(rows, cols, rows, cols + 5,
            #                   vendor.name, title_format)
            # sheet.write(rows, cols, vendor.name, title_format)
            sheet.write(rows, 0, vendor.name, title_format)
            rows += 1
            cols = 0
            sheet.write(rows, cols, "SKU", only_bold)
            sheet.write(rows, 1, "Barcode", only_bold)
            sheet.write(rows, 2, "Unit Barcode",only_bold)
            sheet.write(rows, 3, "Product", only_bold)
            cols = 3
            sheet.write(rows, cols + 1, "Stock in hand", only_bold)
            po_rows = rows
            po_cols = cols + 1
            pd = {}
            po_count = len([pick.purchase_id for pick in value.keys() if pick.purchase_id])
            po_len = po_count + po_cols
            sheet.write(rows, po_len + 1, "PO Subtotal", only_bold)
            sheet.write(rows, po_len + 2, "Total Sales / Outgoing", only_bold)
            sheet.write(rows, po_len + 3, "Incoming Return Qty", only_bold)
            sheet.write(rows, po_len + 4, "Total Forecast", only_bold)
            if self.odoo_Forecast:
                sheet.write(rows, po_len + 5, "Odoo Forecast", only_bold)
            rows += 1
            for po, val in value.items():
                if po:
                    po_cols += 1
                    sheet.write(po_rows, po_cols, po.purchase_id.name, value_format)
                    expected_date = datetime.strftime(po.scheduled_date.date(), '%m/%d/%Y')
                    sheet.write(po_rows + 1, po_cols, expected_date, value_format)
                else:
                    po_cols -= 1
                # sheet.write(po_rows + 1, po_cols - 1, 'Expected Date', only_bold)
                if pd:
                    remaining_prod = list(set(pd.keys()) - set(val.keys()))
                    for rem_pd in remaining_prod:
                        pd.get(rem_pd)['cols'] += 1
                for product, qty in val.items():
                    if product not in pd.keys():
                        rows += 1
                        outgoing_move = move_obj.search([('product_id', '=', product.id),
                                                         ('location_id.usage', 'in', ('internal', 'transit')),
                                                         ('location_dest_id.usage', 'not in', ('internal', 'transit')),
                                                         ('state', 'not in', ('cancel', 'done'))],
                                                        order='partner_id')
                        so_qty = sum(outgoing_move.mapped('product_uom_qty'))
                        # self.env.cr.execute("""select coalesce(sum(product_uom_qty), 0.0)
                        #                        from sale_order_line where state = 'draft'
                        #                        and product_id= %s""" % (product.id))
                        # so_qty = self.env.cr.fetchone()
                        incoming_move = move_obj.search([('product_id', '=', product.id),
                                                         # ('id', '=', 14569),
                                                         ('id', 'not in', tuple(po_move_ids)),
                                                         ('location_id.usage', 'not in', ('internal', 'transit')),
                                                         ('location_dest_id.usage', 'in', ('internal', 'transit')),
                                                         ('state', 'not in', ('cancel', 'done'))],
                                                        order='partner_id')
                        rtn_incoming_qty = sum(incoming_move.mapped('product_uom_qty'))
                        pd.update({product: {'rows': rows,
                                             'cols': po_cols,
                                             'subtotal': qty,
                                             'qty_available': product.qty_available,
                                             'virtual_available': product.virtual_available,
                                             'forecast_qty': qty + product.qty_available + rtn_incoming_qty - so_qty,
                                             'rtn_incoming_qty': rtn_incoming_qty,
                                             }})
                        sheet.write(pd.get(product).get('rows'), po_len + 2, so_qty or '', right_format)

                    else:
                        pd.get(product)['cols'] += 1
                        pd.get(product)['subtotal'] += qty
                        pd.get(product)['forecast_qty'] += qty

                    cols = 0

                    sheet.write(pd.get(product).get('rows'), cols, product.default_code, value_format)
                    sheet.write(pd.get(product).get('rows'), cols + 1, product.barcode or '', value_format)
                    sheet.write(pd.get(product).get('rows'), cols + 2, product.unit_barcode or '', value_format)
                    sheet.write(pd.get(product).get('rows'), cols + 3, product.name, value_format)
                    sheet.write(pd.get(product).get('rows'), cols + 4, product.qty_available, right_format)
                    if po:
                        sheet.write(pd.get(product).get('rows'), pd.get(product).get('cols'), qty, right_format)
                    sheet.write(pd.get(product).get('rows'), po_len + 1, pd.get(product).get('subtotal'),
                                total_format)
                    sheet.write(pd.get(product).get('rows'), po_len + 3, pd.get(product).get('rtn_incoming_qty') or '',
                                right_format)
                    sheet.write(pd.get(product).get('rows'), po_len + 4, pd.get(product).get('forecast_qty'),
                                right_format)
                    if self.odoo_Forecast:
                        sheet.write(pd.get(product).get('rows'), po_len + 5, pd.get(product).get('virtual_available'),
                                    right_format)
            po_rows += 1
            rows += 2
        sheet.write(rows, 0, 'No Vendor', title_format)
        rows += 1
        sheet.write(rows, cols, "SKU", only_bold)
        sheet.write(rows, cols + 1, "Barcode", only_bold)
        sheet.write(rows, cols + 2, "Unit Barcode", only_bold)
        sheet.write(rows, cols + 3, "Product", only_bold)
        sheet.write(rows, cols + 4, "Stock in hand", only_bold)
        sheet.write(rows, cols + 5, "Total Sales / Outgoing", only_bold)
        sheet.write(rows, cols + 6, "Incoming Return Qty", only_bold)
        sheet.write(rows, cols + 7, "Total Forecast", only_bold)
        sheet.write(rows, cols + 8, "Odoo Forecast", only_bold)
        cols = 3
        data.update({'no_vendor': {}})
        no_vendor_product = self.env['product.product'].search(
            [('id', 'not in', existing_product_list)])
        for pd in no_vendor_product:
            # if pd.qty_available:
            qty_available = pd.qty_available
            outgoing_move = move_obj.search(
                [('product_id', '=', pd.id),
                 ('location_id.usage', 'in', ('internal', 'transit')),
                 ('location_dest_id.usage', 'not in',
                  ('internal', 'transit')),
                 ('state', 'not in', ('cancel', 'done'))],
                order='partner_id')
            so_qty = sum(outgoing_move.mapped('product_uom_qty'))
            incoming_move = move_obj.search(
                [('product_id', '=', pd.id),
                 # ('id', '=', 14569),
                 ('id', 'not in', tuple(po_move_ids)),
                 ('location_id.usage', 'not in', ('internal', 'transit')),
                 ('location_dest_id.usage', 'in', ('internal', 'transit')),
                 ('state', 'not in', ('cancel', 'done'))],
                order='partner_id')
            rtn_incoming_qty = sum(incoming_move.mapped('product_uom_qty'))
            qty = pd.qty_available + rtn_incoming_qty - so_qty
            rows += 1
            cols = 0
            sheet.write(rows, cols, pd.product_tmpl_id.default_code or '', value_format)
            sheet.write(rows, cols + 1, pd.product_tmpl_id.barcode or '', value_format)
            sheet.write(rows, cols + 2, pd.product_tmpl_id.unit_barcode or '', value_format)
            sheet.write(rows, cols + 3, pd.product_tmpl_id.name, value_format)
            sheet.write(rows, cols + 4, pd.product_tmpl_id.qty_available, right_format)
            sheet.write(rows, cols + 5, so_qty, right_format)
            sheet.write(rows, cols + 6, rtn_incoming_qty, right_format)
            sheet.write(rows, cols + 7, qty, right_format)
            if self.odoo_Forecast:
                sheet.write(rows, cols + 8, pd.product_tmpl_id.virtual_available, right_format)

        sheet.set_column(0, 3, 25)
        sheet.set_column(4, 30, 14)

        workbook.close()
        vendorstock_file = base64.b64encode(open('/tmp/' +
                                                 file_name, 'rb').read())
        if vendorstock_file:
            self.write({'report_data': vendorstock_file})
        filename = 'Vendor Stock Report.xlsx'
        return {
            'name': 'Vendor Stock Report',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=wiz.vendor.stock.report&id=" + str(
                self.id) + "&filename_field=filename&field=report_data&download=true&filename=" + filename,
            'target': 'self',
        }
