/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { BundleKanbanController } from "./bundle_kanban_controller";

export const BundleKanbanView = Object.assign({}, kanbanView, {
    Controller: BundleKanbanController,
});

registry.category("views").add("bundle_kanban", BundleKanbanView);
