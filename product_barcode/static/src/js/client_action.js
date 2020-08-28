odoo.define('product_barcode.ClientActionCustom', function (require) {
'use strict';

var client_action_custom = require('stock_barcode.ClientAction');
var utils = require('web.utils');

client_action_custom.include({

     _makePages: function () {
        var pages = [];
        var defaultPage = {};
        var self = this;
        if (this._getLines(this.currentState).length) {
            // from https://stackoverflow.com/a/25551041
            var groups = _.groupBy(this._getLines(this.currentState), function (line) {
                return _.map(self._getPageFields({line: true}), function (field) {
                    return utils.into(line, field[1]);
                }).join('#');
            });
            pages = _.map(groups, function (group) {
                var page = {};
                _.map(self._getPageFields({line: true}), function (field) {
                    page[field[0]] = utils.into(group[0], field[1]);
                });
                page.lines = group;
                return page;
            });
        } else {
            _.each(self._getPageFields(), function (field) {
                defaultPage[field[0]] = utils.into(self.currentState, field[1]);
            });
            defaultPage.lines = [];
        }
        pages = _.sortBy(pages, 'location_name').reverse();

        // Create a new page if the pair scanned location / default destination location doesn't
        // exist yet and the scanned location isn't the one of current page.
        var currentPage = this.pages[this.currentPageIndex];
        if (this.scanned_location && currentPage.location_id !== this.scanned_location.id) {
            var alreadyInPages = _.find(pages, function (page) {
                return page.location_id === self.scanned_location.id &&
                    (self.actionParams.model === 'stock.inventory' || page.location_dest_id === self.currentState.location_dest_id.id);
            });
            if (! alreadyInPages) {
                var pageValues = {
                    location_id: this.scanned_location.id,
                    location_name: this.scanned_location.display_name,
                    lines: [],
                };
                if (self.actionParams.model === 'stock.picking') {
                    pageValues.location_dest_id = this.currentState.location_dest_id.id;
                    pageValues.location_dest_name = this.currentState.location_dest_id.display_name;
                }
                pages.push(pageValues);
            }
        }

        if (pages.length === 0) {
            pages.push(defaultPage);
        }

        return pages;
    },
});
});