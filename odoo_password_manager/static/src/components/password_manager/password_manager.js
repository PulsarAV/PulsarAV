/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { checkBundleSecurity } from "@odoo_password_manager/views/dialogs/password_login_dialog/password_login_dialog";
import { download } from "@web/core/network/download";
import { PasswordExportDataDialog } from "@odoo_password_manager/views/dialogs/password_export_dialog/password_export_dialog";
import { PasswordPreview } from "@odoo_password_manager/components/password_preview/password_preview";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, useState } = owl;
const componentModel = "password.key";


export class PasswordManager extends Component {
    static template = "odoo_password_manager.PasswordManager";
    static components = { PasswordPreview };
    static props = {
        currentSelection: { type: Array },
        selection: { type: Array },
        kanbanModel: { type: Object },
        canUpdate: { type: Boolean },
        bundleIds: { type: Array },
        reloadNavigation: { type: Function },
    };
    /*
    * Re-write to import required services and update props on the component start
    */
    setup() {
        this.orm = useService("orm");
        this.state = useState({ massActions: null });
        this.dialogService = useService("dialog");
        this.actionService = useService("action");
        this.rpc = useService("rpc");
        onWillStart(async () => {
            await this._loadMassActions(this.props);
            await this._loadExportConf(this.props);
        });
    }
    /*
    * Getter for records from selection
    */
    get records() {
        var result = null;
        if (this.props.selection && this.props.selection.length != 0) { result = this.props.selection };
        return result
    }
    /*
    * The method to get configured mass actions
    */
    async _loadMassActions(props) {
        var massActions = await this.orm.call(componentModel, "action_return_mass_actions", [this.props.canUpdate]);
        if (massActions.length === 0) { massActions = null };
        Object.assign(this.state, { massActions: massActions });
    }
    /*
    * The method to define whether the export mass action is turned on
    */
    async _loadExportConf(props) {
        const exportConf = await this.orm.call(componentModel, "action_return_export_conf", []);
        Object.assign(this.state, { exportConf: exportConf });
    }
    /*
    * Prepare props for the PasswordManager (right navigation & mass actions component)
    */
    getPasswordPreviewProps() {
        return {
            passwordManager: this,
            refreshAfterUpdate: this.refreshAfterUpdate.bind(this),
            bundleIds: this.props.bundleIds,
        };
    }
    /*
    * The method to load updated records after mass update
    */
    async refreshAfterUpdate() {
        await this.props.kanbanModel.root.load();
        this.props.kanbanModel.notify();
    }
    /*
    * The method to update selected records after update (e.g. when record was deleted)
    */
    async _updateRootSelection(recordIds) {
        const context = { active_test: false };
        this.props.kanbanModel.selectedRecords = await this.orm.searchRead(
            componentModel, [["id", "in", recordIds]], ["name", "user_name", "link_url", "password_len"], { context }
        );
    }
    /*
    * Remove all previously chosen records from selection
    */
    _onClearSelection() {
        const kanbanModel = this.props.kanbanModel;
        const needReload = this.props.currentSelection.length === 0;
        this.props.currentSelection.forEach(function (record) {
            record.toggleSelection(false);
        });
        this.props.selection.forEach(function (record) {
            kanbanModel._updateModelSelection(record, false);
        });
        if (needReload) {
            this.refreshAfterUpdate();
        };
    }
    /*
    * The method to execute clicked mass action
    */
    async _onProceedMassAction(massActionID) {
        await checkBundleSecurity(this.props.bundleIds, this.orm, this.dialogService)
        const recordIds = this.props.selection.map((rec) => rec.id);
        const actionResult = await this.orm.call(componentModel, "action_proceed_mass_action", [recordIds, massActionID]);
        if (actionResult.type) {
            this.actionService.doAction(actionResult,  { onClose: async () => {
                await this._updateRootSelection(recordIds);
                this.refreshAfterUpdate();
                if (actionResult.context && actionResult.context.need_navigation_reload) {
                    this.props.reloadNavigation();
                }
            }})
        }
        else {
            await this._updateRootSelection(recordIds);
            this.refreshAfterUpdate();
        }
    }
    /*
    * The method to export selected records
    */
    async _onProceedExport() {
        await checkBundleSecurity(this.props.bundleIds, this.orm, this.dialogService)
        const recordIds = this.props.selection.map((rec) => rec.id);
        const dialogProps = {
            download: this.downloadExport.bind(this),
            defaultExportList: [],
            getExportedFields: this.getExportedFields.bind(this),
            root: this.props.kanbanModel.root,
        };
        this.dialogService.add(PasswordExportDataDialog, dialogProps);
    }
    /*
    * The method used in the export dialog to finalize export (@see views/list/list_controller.js)
    */
    async downloadExport(fields, import_compat, format) {
        const recordIds = this.props.selection.map((rec) => rec.id);
        const exportedFields = fields.map((field) => ({
            name: field.name || field.id,
            label: field.label || field.string,
            store: field.store,
            type: field.field_type || field.type,
        }));
        if (import_compat) {
            exportedFields.unshift({ name: "id", label: _lt("External ID") });
        }
        await download({
            data: {
                data: JSON.stringify({
                    import_compat,
                    domain: this.props.kanbanModel.root.domain,
                    fields: exportedFields,
                    groupby: this.props.kanbanModel.root.groupBy,
                    ids: recordIds.length > 0 && recordIds,
                    model: this.props.kanbanModel.root.resModel,
                }),
            },
            url: `/web/export/${format}`,
        });
    }
    /*
    * The method used in the export dialog to finalize export (@see views/list/list_controller.js)
    */
    async getExportedFields(model, import_compat, parentParams) {
        const fields = await this.rpc("/web/export/get_fields", {...parentParams, model, import_compat });
        return fields
    }
};
