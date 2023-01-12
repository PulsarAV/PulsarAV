/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component } = owl;


export class PasswordDuplicatesField extends Component {
    /*
    * Import required services
    */
    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
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
            { context: this.env.model.root.context }
        );
        var saved = true;
        additionalContext.search_default_duplicates_count = passwordId;
        if (additionalContext.needFormClose) {
            saved = await this.props.record.save({ stayInEdition: true, noReload: false });
            if (saved) {
                // this is a hack to close the formDialog without triggering onRecordSaved (values are saved above)
                this.env.model.__component.props.discardRecord();
            }
            additionalContext.needFormClose = false;
        }
        if (saved) {
            this.actionService.doAction(action, {
                "additionalContext": this.env.model.root.context, "clearBreadcrumbs": true,
            });
        }
    }
}

PasswordDuplicatesField.supportedTypes = ["integer"];
PasswordDuplicatesField.template = "odoo_password_manager.PasswordDuplicates";

registry.category("fields").add("PasswordDuplicates", PasswordDuplicatesField);

