odoo.define('bista_superasia_theme.feature_products', function (require) {
"use strict";
var ajax = require('web.ajax');
var core = require('web.core');
var qweb = core.qweb;
var publicWidget = require('web.public.widget');
var VariantMixin = require('sale.VariantMixin');
var WebsiteSaleMixin = require('website_sale.website_sale');
var wSaleUtils = require('website_sale.utils');

publicWidget.registry.websiteFeatureProducts = publicWidget.Widget.extend(VariantMixin, {
    selector: '.featured_products',
     events: _.extend({}, VariantMixin.events || {}, {
        "click .add_to_crt": '_onAddProduct',
        'click a.js_add_cart_json': '_onClickAddCartJSON',
        'mouseup form.js_add_cart_json label': '_onMouseupAddCartLabel',
        'touchend form.js_add_cart_json label': '_onMouseupAddCartLabel',
        'change .custom_js_quantity[data-product-id]': 'onChangeCartQuantity',
    }),

    /**
     * @constructor
     */
    init: function (parent, options) {
        var self = this;
        this._super.apply(this, arguments);
        },

    _onAddProduct: function (ev) {
        ev.preventDefault();
        $(ev.currentTarget).addClass('d-none')
        var find_vs_btn = $(ev.currentTarget).closest('.js_product').find('.css_quantity');
        find_vs_btn.removeClass('d-none');
        $(ev.currentTarget).closest('.js_product').find('a.js_add_cart_json').trigger('click');
    },

    _onClickAddCartJSON: function (ev){
        this.onClickAddCartJSON(ev);
    },
    onChangeCartQuantity: function (ev){
        this._onChangeCartQuantity(ev);
    },
    _onChangeCartQuantity: function (ev) {
        var $input = $(ev.currentTarget);
        if ($input.data('update_change')) {
            return;
        }
        var value = parseInt($input.val() || 0, 10);
        if (isNaN(value)) {
            value = 1;
        }
        var $dom = $input.closest('tr');
        // var default_price = parseFloat($dom.find('.text-danger > span.oe_currency_value').text());
        var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
        var line_id = parseInt($input.data('line-id'), 10);
        var productIDs = [parseInt($input.data('product-id'), 10)];
        this._changeCartQuantity($input, value, $dom_optional, line_id, productIDs);
    },
    _changeCartQuantity: function ($input, value, $dom_optional, line_id, productIDs) {
        _.each($dom_optional, function (elem) {
            $(elem).find('.js_quantity').text(value);
            productIDs.push($(elem).find('span[data-product-id]').data('product-id'));
        });
        $input.data('update_change', true);

        this._rpc({
            route: "/shop/cart/update_json",
            params: {
                line_id: line_id,
                product_id: parseInt($input.data('product-id'), 10),
                set_qty: value
            },
        }).then(function (data) {
            $input.data('update_change', false);
            var check_value = parseInt($input.val() || 0, 10);
            if (isNaN(check_value)) {
                check_value = 1;
            }
            if (value !== check_value) {
                $input.trigger('change');
                return;
            }
            if (!data.cart_quantity) {
                return window.location = '/shop/cart';
            }
            wSaleUtils.updateCartNavBar(data);
            $input.val(data.quantity);
            $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);

            if (data.warning) {
                var cart_alert = $('.oe_cart').parent().find('#data_warning');
                if (cart_alert.length === 0) {
                    $('.oe_cart').prepend('<div class="alert alert-danger alert-dismissable" role="alert" id="data_warning">'+
                            '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning + '</div>');
                }
                else {
                    cart_alert.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning);
                }
                $input.val(data.quantity);
            }
        });
    },

});


});
