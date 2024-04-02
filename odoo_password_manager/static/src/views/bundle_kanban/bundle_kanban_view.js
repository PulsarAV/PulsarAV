/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { BundleKanbanController } from "./bundle_kanban_controller";
import { BundleKanbanRenderer } from "./bundle_kanban_renderer";

export const BundleKanbanView = Object.assign({}, kanbanView, {
    Controller: BundleKanbanController,
    Renderer: BundleKanbanRenderer,
});

registry.category("views").add("bundle_kanban", BundleKanbanView);
