/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { archParseBoolean } from "@web/views/utils";
import { CharField, charField } from "@web/views/fields/char/char_field";
import {
    checkBundleSecurity,
    copy2ClipboardWithPopover,
} from "@odoo_password_manager/views/dialogs/password_login_dialog/password_login_dialog";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { useState } = owl;


export class PasswordCopyField extends CharField {
    static template = "odoo_password_manager.PasswordCopyField";
    static props = {
        ...CharField.props,
        isExternalLink: { type: Boolean, optional: true },
        inputPadding: { type: Number, optional: true },
        logIn: { type: Boolean, optional: true },
    };
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
    * Getter for value
    */
    get value() {
        return this.props.record.data[this.props.name];
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
        if (!valid) { return false };
        const content2Copy = this.value;
        const popoverEl = $(event.target).closest("div");
        copy2ClipboardWithPopover(this.popover, popoverEl, content2Copy);
    }
    /*
    * The method to show the password
    */
    async _onShowPassword() {
        const valid = await this._checkSecurityWrapper();
        if (!valid) { return false };
        Object.assign(this.state, { isPassword: !this.state.isPassword });
    }
    /*
    * The method to generate new password
    */
    async _onGeneratePassword() {
        const valid = await this._checkSecurityWrapper();
        if (!valid) { return false };
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
        if (!valid) { return false };
        await checkBundleSecurity(this.bundleIds, this.orm, this.dialogService);
        window.open(this.value, "_blank");
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

export const passwordCopyField = {
    ...charField,
    component: PasswordCopyField,
    supportedTypes: ["char"],
    extractProps(fieldInfo, dynamicInfo) {
        const charExtraProps = charField.extractProps(...arguments);
        return {
            ...charExtraProps,
            isExternalLink: archParseBoolean(fieldInfo.attrs.password_link),
            inputPadding: archParseBoolean(fieldInfo.attrs.password_small) ? 25 : 70 ,
            logIn: archParseBoolean(fieldInfo.attrs.log_in),
        }
    },
};

registry.category("fields").add("PasswordCopy", passwordCopyField);
