odoo.define('product_barcode.SettingsWidgetCustom', function (require) {
'use strict';

var settings_widget_custom = require('stock_barcode.SettingsWidget');
var utils = require('web.utils');
var Widget = require('web.Widget');
var rpc = require("web.rpc");
var core = require('web.core');
var _t = core._t;
settings_widget_custom.include({

    events: {
            'click .o_validate': '_onClickValidate',
            'click .o_cancel': '_onClickCancel',
            'click .o_print_picking': '_onClickPrintPicking',
            'click .o_check_availability': '_onClickCheckAvailability',
            'click .o_unreserve': '_onClickUnreserve',
            'click .o_print_delivery_slip': '_onClickPrintDeliverySlip',
            'click .o_print_barcodes_zpl': '_onClickPrintBarcodesZpl',
            'click .o_print_barcodes_pdf': '_onClickPrintBarcodesPdf',
            'click .o_print_inventory': '_onClickPrintInventory',
            'click .o_scrap': '_onClickScrap',
    },

    _onClickCheckAvailability: function (ev) {
        ev.stopPropagation();
        this.trigger_up('picking_check_availability');
    },

    _onClickUnreserve: function (ev) {
        ev.stopPropagation();
        this.trigger_up('picking_unreserve');
    },

});
});