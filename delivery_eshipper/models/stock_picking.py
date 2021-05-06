# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    
    _inherit = 'stock.picking'
    
    eshipper_order_id = fields.Char(string="Order ID",readonly=True)
    eshipper_tracking_url = fields.Char(string="Tracking URL")
    
    def send_to_shipper(self):
        self.ensure_one()
        self = self.sudo()
        if self.carrier_id and self.carrier_id.delivery_type == 'eshipper':
            tracking_numbers = []
            res = self.carrier_id.send_shipping(self)
            for shipping in res:
                self.carrier_price = shipping['exact_price']
                tracking_numbers.append(shipping['tracking_number'])
                # create the new ir_attachment
                if shipping.get('label_data'):
                    attachment_value = {
                        'name': 'eShipper Label %s' % shipping['tracking_number'] + '.pdf',
                        'res_name': self.name,
                        'res_model': self._name,
                        'res_id': self.id,
                        'type': 'binary',
                        'name': 'eShipper Label %s' % shipping['eshipper_order_id'] + '.pdf',
                        'datas': shipping['label_data'],
                    }
                    self.env['ir.attachment'].create(attachment_value)
                self.write({
                    'eshipper_tracking_url':shipping['eshipper_tracking_url'],
                    'eshipper_order_id':shipping['eshipper_order_id']
                })
            self.update({'carrier_tracking_ref':','.join(map(str, tracking_numbers))})
            return True
        return super(StockPicking, self).send_to_shipper()
    
    def open_website_url(self):
        self.ensure_one()
        if self.eshipper_tracking_url and self.carrier_id.delivery_type == 'eshipper':
            client_action = {
                'type': 'ir.actions.act_url',
                'name': "Shipment Tracking Page",
                'target': 'new',
                'url': self.eshipper_tracking_url,
            }
            return client_action
        else:
            return super(StockPicking,self).open_website_url()
