/** @odoo-module **/

import { checkBundleSecurity } from "@odoo_password_manager/views/dialogs/password_login_dialog/password_login_dialog";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { useService } from "@web/core/utils/hooks";


export class BundleKanbanController extends KanbanController {
    /*
    * Overwrite to add required services
    */
    setup() {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        super.setup(...arguments);
    }
    /*
    * Overwrite to check security
    */
    async openRecord(record, mode) {
        await checkBundleSecurity([record.data.id], this.orm, this.dialogService);
        super.openRecord(...arguments);
    }
};
