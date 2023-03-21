/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { archParseBoolean } from "@web/views/utils";
import { browser } from "@web/core/browser/browser";
import { CharField } from "@web/views/fields/char/char_field";
import { checkBundleSecurity } from "@odoo_password_manager/views/dialogs/password_login_dialog/password_login_dialog";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { Tooltip } from "@web/core/tooltip/tooltip";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { useState } = owl;


export class PasswordCopyField extends CharField {
    /*
    * Re-write to add popopve
    */
    setup() {
        this.popover = useService("popover");
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.state = useState({ isPassword: this.props.isPassword });
        super.setup(...arguments);
    }
    /*
    * Getter for bundle id: we take that from the form
    */
    get bundleIds() {
        if (this.props.record.data.bundle_id && this.props.record.data.bundle_id.length != 0) {
            return [this.props.record.data.bundle_id[0]]
        }
        return false
    }
    /*
    * The method to wrap bundle security check with extra considerations
    */
    async _checkSecurityWrapper() {
        if (!this.props.logIn) {
            if (!this.bundleIds) {
                return false;
            };
            const valid = await checkBundleSecurity(this.bundleIds, this.orm, this.dialogService);
            return valid
        }
        return true
    }

    /*
    * The method to copy the value for clipboard
    */
    async _onCopyClipboard(event) {
        const valid = await this._checkSecurityWrapper();
        if (!valid) {
            return false;
        };
        const content2Copy = this.props.value;
        const popoverEl = $(event.target).closest("div");
        var popoverTooltip = _lt("Successfully copied!"),
            popoverClass = "text-success",
            popoverTimer = 800;
        try {
            await browser.navigator.clipboard.writeText(content2Copy)          
        } catch {
            popoverTooltip = _lt("Error! This browser doesn't allow to copy to clipboard");
            popoverClass = "text-danger";
            popoverTimer = 2500;
        };
        if (popoverEl.length != 0) {
            const closeTooltip = this.popover.add(
                popoverEl[0], 
                Tooltip, 
                { tooltip: popoverTooltip },
                { popoverClass: popoverClass, }
            );
            browser.setTimeout(() => { closeTooltip() }, popoverTimer);
        }
    }
    /*
    * The method to show the password
    */
    async _onShowPassword() {
        const valid = await this._checkSecurityWrapper();
        if (!valid) {
            return false;
        };
        Object.assign(this.state, { isPassword: !this.state.isPassword });
    }
    /*
    * The method to generate new password
    */
    async _onGeneratePassword() {
        const valid = await this._checkSecurityWrapper();
        if (!valid) {
            return false;
        };
        this.dialogService.add(FormViewDialog, {
            resModel: "password.generator",
            title: _lt("Password Generator"),
            onRecordSaved: async (formRecord) => { 
                const newPassword = await this.orm.call(
                    "password.key",
                    "action_generate_new_password",
                    [formRecord.data.pwlength, formRecord.data.pwcharset],
                );
                const changes = {
                    "password": newPassword,
                    "confirm_password": newPassword,
                }
                this.props.record.update(changes);
            },
        });
    }
    /*
    * The method to open external URL
    */
    async _onOpenLink() {
        const valid = await this._checkSecurityWrapper();
        if (!valid) {
            return false;
        };
        await checkBundleSecurity(this.bundleIds, this.orm, this.dialogService);
        window.open(this.props.value, "_blank");
    }
    /*
    * The method to log in if the 'Enter' key is pressed (applicable for bundle key log in dialog)
    */
    async _onKeydown(ev) {
        if (this.props.logIn && ev.keyCode === 13) {
            $(".o_form_button_save").click();            
        };
    }
};

PasswordCopyField.supportedTypes = ["char"];
PasswordCopyField.template = "odoo_password_manager.PasswordCopyField";
PasswordCopyField.props = {
    ...CharField.props,
    isExternalLink: { type: Boolean, optional: true },
    inputPadding: { type: Number, optional: true },
    logIn: { type: Boolean, optional: true },
};
PasswordCopyField.extractProps = ({ attrs, field }) => {
    var charExtraProps = CharField.extractProps({ attrs, field })
    return Object.assign( 
        charExtraProps, 
        { 
            isExternalLink: archParseBoolean(attrs.password_link),
            inputPadding: archParseBoolean(attrs.password_small) ? 25 : 70 ,
            logIn: archParseBoolean(attrs.log_in),
        },
    );
}

registry.category("fields").add("PasswordCopy", PasswordCopyField);
