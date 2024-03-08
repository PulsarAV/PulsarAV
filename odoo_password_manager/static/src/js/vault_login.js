/** @odoo-module **/

import { mount } from "@odoo/owl";
import { makeEnv } from "@web/env";
import publicWidget from "@web/legacy/js/public/public_widget";
import { PortalPassword } from "@odoo_password_manager/components/portal_password/portal_password";
import { templates } from "@web/core/assets";

/*
* Initiate the widget to enter the portal password vault
*/
publicWidget.registry.vaultLogin = publicWidget.Widget.extend({
    selector: "#portal_vault_container",
    events: {
        "click #portal_vault_login": "_onLogin",
        "click #portal_vault_info": "_onShowInfo",
    },
    /*
    * Re-write to bind services
    */
    init: function (parent, obj, placeholder) {
        this._super.apply(this, arguments);
        this.orm = this.bindService("orm");
    },
    /*
    * The method to check the entered password an update session correspondingly
    */
    async _onLogin(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const passwordInput = $("#portal_vault_password")[0];
        const loggedIn = await this.orm.call(
            "portal.password.bundle",
            "action_check_entered_password",
            [[parseInt(passwordInput.dataset.id)], passwordInput.value],
        );
        if (loggedIn) { window.location.reload() };
    },
});
/*
* Initiate the widgets to enter the portal password vault
*/
publicWidget.registry.portalPasswordMask = publicWidget.Widget.extend({
    selector: ".portal_vault_mask",
    /*
    * Re-write to bind services
    */
    init: function (parent, obj, placeholder) {
        this._super.apply(this, arguments);
        this.orm = this.bindService("orm");
    },
    /*
    * Re-write to initiate password mask component
    */
    async start() {
        const passwordSpan = this.$el[0];
        const props = {
            passwordId: parseInt(passwordSpan.dataset.id),
            passwordLen: parseInt(passwordSpan.dataset.pw_len),
            showPopover: this._showPopover.bind(this),
            decryptPassword: this.decryptPassword.bind(this),
        }
        const env = makeEnv();
        await mount(PortalPassword, passwordSpan, { env, templates, props });
    },
    /*
    * The method to decrypt the password
    */
    async decryptPassword(passwordId) {
        const decryptedPassword = await this.orm.call(
            "portal.password.key", "action_return_decrypted_password", [[passwordId]],
        );
        if (decryptedPassword === null || decryptedPassword === undefined) {
            window.location.reload();
        };
        return decryptedPassword
    },
    /*
    * The method to show/hide a popopver for copy to the clipboard
    */
    _showPopover(notification) {
        const copyButton = this.$el.find(".fa-paste");
        copyButton.popover({
            content: notification,
            placement: "bottom",
            container: this.$el,
            html: true,
            trigger: "manual",
            animation: true,
        }).popover("show");
        setTimeout(function () { copyButton.popover("dispose") }, 1000);
    }
});
