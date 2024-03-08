/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { Component, onMounted, onWillUnmount } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { Tooltip } from "@web/core/tooltip/tooltip";
import { useChildRef } from "@web/core/utils/hooks";
import { useService } from "@web/core/utils/hooks";
import { View } from "@web/views/view";


export class PasswordLoginDialog extends Component {
    static template = "odoo_password_manager.PasswordLoginDialog";
    static components = { Dialog, View };
    static props = {
        close: Function,
        resModel: String,
        context: { type: Object, optional: true },
        mode: {
            optional: true,
            validate: (m) => ["edit", "readonly"].includes(m),
        },
        onRecordSaved: { type: Function, optional: true },
        resId: { type: [Number, Boolean], optional: true },
        title: { type: String, optional: true },
        viewId: { type: [Number, Boolean], optional: true },
        size: Dialog.props.size,
    };
    static defaultProps = { onRecordSaved: () => {} };
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.modalRef = useChildRef();
        this.unSuccessFullLogin = true;
        const buttonTemplate = "odoo_password_manager.FormViewDialog.buttons";
        this.viewProps = {
            type: "form",
            buttonTemplate: buttonTemplate,
            context: this.props.context || {},
            display: { controlPanel: false },
            mode: "edit",
            resId: this.props.resId || false,
            resModel: this.props.resModel,
            viewId: this.props.viewId || false,
            preventCreate: false,
            preventEdit: false,
            discardRecord: () => {
                this.props.close();
            },
            saveRecord: async (record, { saveAndNew }) => {
                const saved = await record.save({ stayInEdition: true, noReload: true });
                if (saved) {
                    await this.props.onRecordSaved(record);
                    this.unSuccessFullLogin = false;
                    this.props.close();
                }
            },
        };
        onMounted(() => {
            // Hide excess buttons
            if (this.modalRef.el.querySelector(".modal-footer").childElementCount > 1) {
                const defaultButton = this.modalRef.el.querySelector(
                    ".modal-footer button.o-default-button"
                );
                if (defaultButton) {
                    defaultButton.classList.add("d-none");
                }
            }
        });
        onWillUnmount(() => {
            // Returns to bundles overview
            if (this.unSuccessFullLogin) {
                this.actionService.doAction("odoo_password_manager.password_bundle_action", { clearBreadcrumbs: true });
            }
        });
    }
}
/*
* The method to check security for specific bundles and trigger the Log in dialog if needed
* @param bundleIds - list of ints
* @param ormService - component orm service
* @param dialogService - component dialog service
*/
export async function checkBundleSecurity(bundleIds, ormService, dialogService) {
    var successfullLogin = $.Deferred();
    const failed_bundle_ids = await ormService.call("password.bundle", "action_check_bundle_key", [bundleIds]);
    if (failed_bundle_ids.length == 0) { successfullLogin.resolve(true) }
    else {
        for (const bundleId of failed_bundle_ids) {
            var thisBundleSuccessfullLogin = $.Deferred();
            dialogService.add(PasswordLoginDialog, {
                resModel: "bundle.login",
                title: _lt("Log in"),
                context: {"default_bundle_id": bundleId, "need_password_check": true},
                onRecordSaved: async (formRecord) => {
                    thisBundleSuccessfullLogin.resolve(true)
                },
            });
            await thisBundleSuccessfullLogin;
        }
        successfullLogin.resolve(true);
    }
    return successfullLogin
};
/*
* The method to copy a value to the clipboard
*/
export async function copy2ClipboardWithPopover(popoverService, popoverEl, value) {
    var popoverTooltip = _lt("Successfully copied!"),
        popoverClass = "text-success",
        popoverTimer = 800;
    try {
        browser.navigator.clipboard.writeText(value);
    }
    catch {
        popoverTooltip = _lt("Error! This browser doesn't allow to copy to clipboard");
        popoverClass = "text-danger";
        popoverTimer = 2500;
    };
    if (popoverEl && popoverEl.length != 0) {
        const closeTooltip = popoverService.add(
            popoverEl[0], Tooltip, { tooltip: popoverTooltip }, { popoverClass: popoverClass },
        );
        browser.setTimeout(() => { closeTooltip() }, popoverTimer);
    };
};
