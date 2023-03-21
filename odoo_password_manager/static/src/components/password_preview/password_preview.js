/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { checkBundleSecurity } from "@odoo_password_manager/views/dialogs/password_login_dialog/password_login_dialog";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { Tooltip } from "@web/core/tooltip/tooltip";
import { useService } from "@web/core/utils/hooks";


const { Component, onWillStart, onMounted, useState } = owl;
const componentModel = "password.key";


export class PasswordPreview extends Component {
    /*
    * Re-write to import required services and update props on the component start
    */
    setup() {
        this.orm = useService("orm");
        this.state = useState({ massActions: null, duplicatesCount: null });
        this.dialogService = useService("dialog");
        this.popover = useService("popover");
        onWillStart(async () => {
            await this._loadPasswordMask(false);
        });
        onMounted(() => {
            this.passwordInput = $("#password_preview_input_" + this.record.id)[0];
        })
    }
    /*
    * The method to get record from props
    */
    get record() {
        return this.props.record;
    }
    /*
    * The method to get parent component (PasswordManager) from props
    */
    get passwordManager() {
        return this.props.passwordManager;
    }
    /*
    * The method to save password mask (its length) 
    * We purposefully do not keep real password for security purposes
    * We do load password when length is zero since migrated from previous versions passwords do not have length calced
    * Simultaneously, keys without a password (should be a rare case), the len will be -1
    */
    async _loadPasswordMask(needReload) {
        var passwordMask = false,
            passwordLen = this.record.password_len;
        if (needReload || !passwordLen || passwordLen == 0) {
            const password = await this._loadPassword();
            passwordLen = password.length;
        }
        if (passwordLen > 0) {
            passwordMask = "*".repeat(passwordLen);
        }        
        Object.assign(this.state, { password: passwordMask });
    }
    /*
    * The method to get the password since it is not present on kanban card (purposefully to avoid decryption)
    */
    async _loadPassword() {
        const passwordlist = await this.orm.read(
            componentModel,
            [this.record.id],
            ["password"],
        );
        const password = passwordlist[0].password;
        return password
    }   
    /*
    * The method to open the password full form
    */
    async _onOpenRecord() {
        await checkBundleSecurity(this.props.bundleIds, this.orm, this.dialogService);
        const modelContext = this.passwordManager.props.kanbanModel.rootParams.context;
        modelContext.needFormClose = true;
        this.dialogService.add(FormViewDialog, {
            resModel: componentModel,
            resId: this.record.id,
            context: modelContext,
            title: _lt("Edit Password"),
            preventEdit: !this.passwordManager.props.canUpdate,
            preventCreate: !this.passwordManager.props.canUpdate,
            onRecordSaved: async (formRecord) => { 
                const record = this.passwordManager.props.selection.find(rec => rec.id === this.record.id);
                // to update the select value itself
                Object.assign(record, this.passwordManager.props.kanbanModel.getSelectedData(formRecord.data));
                this._loadPasswordMask(true);
                await this.props.refreshAfterUpdate();
            },
        });
    }
    /*
    * The method to remove a record from selection
    */
    async _onRemoveFromSelection() {
        await checkBundleSecurity(this.props.bundleIds, this.orm, this.dialogService);
        const record = this.passwordManager.props.currentSelection.find(rec => rec.resId === this.record.id);
        if (record) {
            record.toggleSelection(false);
        }
        else {
            record = passwordManager.props.selection.find(rec => rec.id === this.record.id);
            this.passwordManager.props.kanbanModel._updateModelSelection(record, false);
            this.props.refreshAfterUpdate();
        }
    }
    /*
    * The method to get real password and show that to the field
    */
    async _onTogglePassword() {
        await checkBundleSecurity(this.props.bundleIds, this.orm, this.dialogService);
        if (this.passwordInput.type == "text") {
            this.passwordInput.value = this.state.password;
            this.passwordInput.type = "password";
        }
        else {
            this.passwordInput.value = await this._loadPassword();
            this.passwordInput.type = "text";
        }
    }
    /*
    * The method to copy a password for clipboard
    */
    async _onCopyPassword(event) {
        await checkBundleSecurity(this.props.bundleIds, this.orm, this.dialogService);
        const password = await this._loadPassword();
        await this._onCopyToClipBoard(event, password, true);
    }
    /*
    * The general method to copy any text to clipboard and show popover
    */
    async _onCopyToClipBoard(event, content2Copy, noExtraSecurityCheck) {
        if (!noExtraSecurityCheck) {
            // in if to avoid double check in _onCopyPassword
            await checkBundleSecurity(this.props.bundleIds, this.orm, this.dialogService);
        }
        const popoverEl = $(event.target).closest("tr");
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
    * The method to open the password link
    */
    async _onOpenUrl(linkURL) {
        await checkBundleSecurity(this.props.bundleIds, this.orm, this.dialogService);
        window.open(linkURL, "_blank");
    }
}

PasswordPreview.template = "odoo_password_manager.PasswordPreview";
