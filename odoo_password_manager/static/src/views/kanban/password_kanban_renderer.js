/** @odoo-module **/

import { checkBundleSecurity } from "@odoo_password_manager/views/dialogs/password_login_dialog/password_login_dialog";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { PasswordKanbanRecord } from "./password_kanban_record";
import { PasswordManager } from "@odoo_password_manager/components/password_manager/password_manager";
import { PasswordNavigation } from "@odoo_password_manager/components/password_navigation/password_navigation";
import { useService } from "@web/core/utils/hooks";
const { onWillStart, useState, onWillRender } = owl;
const componentModel = "password.key";


export class PasswordKanbanRenderer extends KanbanRenderer {
    /*
    * Re-write to save update rights
    */
    setup(params) {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.state = useState({ canUpdate: null });
        this.bundles = []
        super.setup(...arguments);
        onWillStart(async () => {
            await this._getBundles(this.props);
            await checkBundleSecurity(this.bundles, this.orm, this.dialogService);
            await this._checkUpdateRight(this.props);
        });
        onWillRender(async () => {
            await checkBundleSecurity(this.bundles, this.orm, this.dialogService);
        });
    }
    /*
    * The method to find actively used bundle(s)
    */
    async _getBundles(props) {
        const localCtx = props.list.evalContext;
        if (localCtx.default_bundle_ids) {
            this.bundles = localCtx.default_bundle_ids;
        }
        else {
            // we are for all the passwords
            this.bundles = await this.orm.call("password.bundle", "action_return_all_active_bundles", []);
        };
    }
    /*
    * The method to check the access rights for bundle(s)
    */
    async _checkUpdateRight(props) {
        const canUpdate = await this.orm.call(componentModel, "action_check_bundle_edit_rights", [this.bundleIds]);
        Object.assign(this.state, { canUpdate: canUpdate });
    }
    /*
    * Getter for bundleIds
    */
    get bundleIds() {
        return this.bundles;
    }
    /*
    * The method to update the navigation panel
    */
    _reloadNavigation() {
        Object.assign(this.state, { "reloaded": !this.state.reloaded })
    }
    /*
    * Prepare props for the PasswordManager (right navigation & mass actions component)
    */
    getPasswordManagerProps() {
        return {
            currentSelection: this.props.list.selection,
            selection: this.props.list.model.selectedRecords,
            kanbanModel: this.props.list.model,
            canUpdate: this.state.canUpdate,
            bundleIds: this.bundleIds,
            reloadNavigation: this._reloadNavigation.bind(this),
        };
    }
    /*
    * The method to PasswordNavigation (left navigation)
    */
    getPasswordNavigationProps() {
        return {
            kanbanList: this.props.list,
            canUpdate: this.state.canUpdate,
            bundleIds: this.bundleIds,
        };
    }
};

PasswordKanbanRenderer.template = "odoo_password_manager.PasswordKanbanRenderer";
PasswordKanbanRenderer.components = Object.assign({}, KanbanRenderer.components, {
    PasswordManager,
    PasswordNavigation,
    KanbanRecord: PasswordKanbanRecord,
});
