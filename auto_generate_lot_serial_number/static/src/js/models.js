odoo.define('auto_generate_lot_serial_number.models', function (require) {
"use strict";
    var core = require('web.core');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PopupWidget    = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var _t = core._t;
    var utils = require('web.utils');
    var QWeb = core.qweb;
    var _t = core._t;
    models.load_fields('res.company','auto_generate_lot_serial');

    models.Order = models.Order.extend({
        display_lot_popup: function() {
            if (!this.pos.company.auto_generate_lot_serial){
                var order_line = this.get_selected_orderline();
                if (order_line){
                    var pack_lot_lines =  order_line.compute_lot_lines();
                    this.pos.gui.show_popup('packlotline', {
                        'title': _t('Lot/Serial Number(s) Required'),
                        'pack_lot_lines': pack_lot_lines,
                        'order_line': order_line,
                        'order': this,
                    });
                }
            }
        },
    });

    screens.ActionpadWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    return line.has_valid_product_lot();
                });
                if(!has_valid_product_lot && !self.pos.company.auto_generate_lot_serial){
                    self.gui.show_popup('confirm',{
                        'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            self.gui.show_screen('payment');
                        },
                    });
                }else{
                    self.gui.show_screen('payment');
                }
            });
            this.$('.set-customer').click(function(){
                self.gui.show_screen('clientlist');
            });
        }

    });
});
