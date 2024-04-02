/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";

const { Component } = owl;


export class PasswordDuplicatesField extends Component {
    static props = { ...standardFieldProps };
    static template = "odoo_password_manager.PasswordDuplicates";
    /*
    * Import required services
    */
    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
    }
    /*
    * Getter for value
    */
    get value() {
        return this.props.record.data[this.props.name];
    }
    /*
    * The getter method to get formDialog (mainly to know what to close)
    */
    get recordDialog() {
        var parentRef = this.__owl__.parent.component;
        while (parentRef && parentRef.__owl__.parent && parentRef.__owl__.parent.component && !(parentRef instanceof FormViewDialog)) {
            parentRef = parentRef.__owl__.parent.component;
        };
        return parentRef
    }
    /*
    * The method to return bundle or all passwords interface with a set filter by this password duplicates
    * We the formViewDialog (needFormClose in ctx), we also should save the record, close it, and then do action
    */
    async _onShowDuplicates() {
        const additionalContext = this.env.model.root.context;
        const passwordId = this.props.record.data.id;
        const action = await this.orm.call(
            "password.key",
            "action_return_duplicates_action",
            [passwordId],
            { context: this.env.model.root.context },
        );
        var saved = true;
        additionalContext.search_default_duplicates_count = passwordId;
        if (additionalContext.needFormClose) {
            saved = await this.props.record.save({ reload: true });
            if (saved) {
                const recordDialog = this.recordDialog;
                if (recordDialog) {
                    recordDialog.props.close();
                };
            };
            additionalContext.needFormClose = false;
        };
        if (saved) {
            this.actionService.doAction(action, {
                "additionalContext": this.env.model.root.context, "clearBreadcrumbs": true,
            });
        };
    }
};

export const passwordDuplicatesField = {
    component: PasswordDuplicatesField,
    supportedTypes: ["integer"],
};

registry.category("fields").add("PasswordDuplicates", passwordDuplicatesField);
