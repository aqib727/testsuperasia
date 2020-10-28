odoo.define('product_barcode.PickingClientActionCustom', function (require) {
'use strict';
var picking_client_action_custom = require('stock_barcode.picking_client_action');
var utils = require('web.utils');
var core = require('web.core');
var ClientAction = require('stock_barcode.ClientAction');
var ViewsWidget = require('stock_barcode.ViewsWidget');
var _t = core._t;
picking_client_action_custom.include({
    custom_events: _.extend({}, ClientAction.prototype.custom_events, {
        'picking_print_delivery_slip': '_onPrintDeliverySlip',
        'picking_print_picking': '_onPrintPicking',
        'picking_check_availability': '_onCheckAvailability',
        'picking_unreserve': '_doUnreserve',
        'picking_print_barcodes_zpl': '_onPrintBarcodesZpl',
        'picking_print_barcodes_pdf': '_onPrintBarcodesPdf',
        'picking_scrap': '_onScrap',
        'validate': '_onValidate',
        'cancel': '_onCancel',
        'put_in_pack': '_onPutInPack',
        'open_package': '_onOpenPackage',
    }),
    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.context = action.context;
        this.commands['O-BTN.scrap'] = this._scrap.bind(this);
        this.commands['O-BTN.validate'] = this._validate.bind(this);
        this.commands['O-BTN.cancel'] = this._cancel.bind(this);
        this.commands['O-BTN.pack'] = this._putInPack.bind(this);
        this.commands['O-BTN.print-slip'] = this._printDeliverySlip.bind(this);
        this.commands['O-BTN.print-op'] = this._printPicking.bind(this);
        this.commands['O-BTN.check-availability'] = this._checkAvailability.bind(this);
        this.commands['O-BTN.do-unreserve'] = this._checkUnreserve.bind(this);
        if (! this.actionParams.pickingId) {
            this.actionParams.pickingId = action.context.active_id;
            this.actionParams.model = 'stock.picking';
        }
    },
    _checkAvailability: function () {
        console.log('--------------------_checkAvailability--------------');
        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                return self._rpc({
                    'model': 'stock.picking',
                    'method': 'action_assign',
                    'args': [[self.actionParams.pickingId]],
                })
            });
        });
    },
    _checkUnreserve: function () {
        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                return self._rpc({
                    'model': 'stock.picking',
                    'method': 'do_unreserve',
                    'args': [[self.actionParams.pickingId]],
                })
            });
        });
    },
    _onCheckAvailability: function (ev) {
        ev.stopPropagation();
        this._checkAvailability();
    },

    _doUnreserve: function (ev) {
        ev.stopPropagation();
        this._checkUnreserve();
    },


});
});