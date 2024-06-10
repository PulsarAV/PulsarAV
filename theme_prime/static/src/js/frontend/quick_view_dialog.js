/** @odoo-module **/

import '@website_sale_comparison/js/website_sale_comparison';
import { jsonrpc } from "@web/core/network/rpc_service";
import Dialog from '@web/legacy/js/core/dialog';
import publicWidget from "@web/legacy/js/public/public_widget";
import { ProductCarouselMixins } from "@theme_prime/js/core/mixins";
// const OwlDialog = require('web.OwlDialog');

export const QuickViewDialog = Dialog.extend(ProductCarouselMixins, {
    events: Object.assign({}, Dialog.prototype.events, {
        'click .tp-close': 'close',
        'dr_close_dialog': 'close',
    }),
    /**
     * @constructor
     */
    init: function (parent, options) {
        this.productID = options.productID;
        this.variantID = options.variantID || false;
        this.isVariantSelectorDialog = options.mini || false;
        options.size = this.isVariantSelectorDialog ? 'small' : 'extra-large';
        this._super(parent, Object.assign({ renderHeader: false, renderFooter: false, technical: false }, options || {}));
    },
    willStart: async function () {
        await this._super(...arguments);
        const result = await jsonrpc('/theme_prime/get_quick_view_html', {
            options: {productID: this.productID, variantID: this.variantID, variant_selector: this.isVariantSelectorDialog}
        });
        if (result) {
            this.$content = $(result);
            this.autoAddProduct = this.isVariantSelectorDialog && this.$content.hasClass('auto-add-product'); // We will not open the dialog for the single varint in mini view
            if (this.autoAddProduct) {
                this.trigger('tp_auto_add_product');
            }
        }
    },
    /**
     * @override
     */
    start: function () {
        if (this.isVariantSelectorDialog) {
            this.$modal.find(".modal-dialog").addClass("tp-product-variant-selector-modal-dialog");
        }
        $(this.$content).appendTo(this.$el);
        this._bindEvents(this.$el);
        this.trigger_up("widgets_start_request", {
            $target: this.$el,
        });
        return this._super.apply(this, arguments);
    },
    open: function (options) {
        $('.tooltip').remove(); // remove open tooltip if any to prevent them staying when modal is opened

        var self = this;
        this.appendTo($('<div/>')).then(function () {
            if (!self.autoAddProduct) {
                self.$modal.find(".modal-body").replaceWith(self.$el);
                self.$modal.attr('open', true);
                self.$modal.appendTo(self.container);
                const modal = new Modal(self.$modal[0], {
                    focus: true,
                });
                modal.show();
                self._openedResolver();

                // Notifies OwlDialog to adjust focus/active properties on owl dialogs
                // TODO: Migrate
                // OwlDialog.display(self);
            }
        });
        if (options && options.shouldFocusButtons) {
            self._onFocusControlButton();
        }

        return self;
    },
});

publicWidget.registry.d_product_quick_view = publicWidget.Widget.extend({
    selector: '.tp-product-quick-view-action, .tp_hotspot[data-on-hotspot-click="modal"]',
    read_events: {
        'click': 'async _onClick',
    },
    /**
     * @private
     * @param  {Event} ev
     */
    _onClick: function (ev) {
        return this.QuickViewDialog = new QuickViewDialog(this, {
            productID: parseInt($(ev.currentTarget).attr('data-product-id'))
        }).open();
    },
});
