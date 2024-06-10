/** @odoo-module **/

import "@website_sale_product_configurator/js/website_sale_options";
import publicWidget from "@web/legacy/js/public/public_widget";
import {CartManagerMixin} from "@theme_prime/js/core/mixins";
import { QuickViewDialog } from "@theme_prime/js/frontend/quick_view_dialog";

publicWidget.registry.WebsiteSale.include(Object.assign({}, CartManagerMixin, {
    init() {
        this._super(...arguments);
        this.notification = this.bindService("notification");
    },
    _onProductReady: function () {
        if (this._isB2bModeEnabled()) {
            this._loggedInNotification();
            return Promise.resolve();
        }
        if (this._isDefaultCartFLow() || this.isBuyNow) {
            return this._super.apply(this, arguments);
        }

        /*  We assume is qty selector is not present the it will not have the
            variant selector so `variantSelectorNeeded` variable used to indicate
            that should we open custom selector or not.
        */
        var variantSelectorNeeded = !this.$form.find('.js_add_cart_variants').length;
        if (variantSelectorNeeded) {
            var dialogOptions = {mini: true, size: 'small'};
            var productID = this.$form.find('.product_template_id').val();
            if (productID) {
                dialogOptions['productID'] = parseInt(productID);
            } else {
                dialogOptions['variantID'] = this.rootProduct.product_id;
            }
            this.QuickViewDialog = new QuickViewDialog(this, dialogOptions);
            this.QuickViewDialog.open();
            this.QuickViewDialog.on('tp_auto_add_product', null, this._submitForm.bind(this));
            return this.QuickViewDialog.opened();
        }
        return this._submitForm();
    },
    _submitForm() {
        if (this.QuickViewDialog) {
            this.QuickViewDialog._openedResolver();
        }
        return this._super(...arguments);
    },
    _isDefaultCartFLow: function () {
        return !['side_cart', 'dialog', 'notification'].includes(odoo.dr_theme_config.cart_flow);
    },
    addToCart(params) {
        if (this.isBuyNow || this._isDefaultCartFLow()) {
            return this._super.apply(this, arguments);
        } else {
            return this._customCartSubmit(params);
        }
    },
}));
