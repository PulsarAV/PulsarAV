/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";

const { Component, onWillStart, useState } = owl;


export class PortalPassword extends Component {
    static template = "odoo_password_manager.PortalPassword";
    static props = {
        passwordId: { type: Number },
        passwordLen: { type: Number },
        showPopover: { type: Function },
        decryptPassword: { type: Function },
    };
    /*
    * Re-write to import required services and update props on the component start
    */
    setup() {
        this.mask = true;
        this.state = useState({ password: null });
        onWillStart(async () => { await this._loadPasswordMask(false) });
    }
    /*
    * The method to save password mask (its length)
    * We purposefully do not keep real password for security purposes
    * We do load password when length is zero since migrated from previous versions passwords do not have length calced
    */
    async _loadPasswordMask() {
        var passwordMask = false,
            passwordLen = this.props.passwordLen;
        if (!passwordLen || passwordLen == 0) {
            const password = await this.props.decryptPassword(this.props.passwordId)
            passwordLen = password.length;
        };
        if (passwordLen > 0) {
            passwordMask = "*".repeat(passwordLen);
        };
        Object.assign(this.state, { password: passwordMask });
    }
    /*
    * The method to show/hide the password
    */
    async _onTogglePassword(event) {
        if (this.mask) {
            const password = await this.props.decryptPassword(this.props.passwordId);
            Object.assign(this.state, { password: password });
        }
        else {
            await this._loadPasswordMask()
        };
        this.mask = !this.mask;
    }
    /*
    * The method to copy a password for clipboard
    */
    async _onCopyPassword(event) {
        const password = await this.props.decryptPassword(this.props.passwordId);
        var popoverTooltip = _lt("Successfully copied!");
        try {
            await browser.navigator.clipboard.writeText(password);
        } catch {
            popoverTooltip = _lt("Error! This browser doesn't allow to copy to clipboard");
        };
        this.props.showPopover(popoverTooltip);
    }
};
