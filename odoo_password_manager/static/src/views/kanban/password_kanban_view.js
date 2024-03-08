/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { PasswordKanbanController } from "./password_kanban_controller";
import { PasswordKanbanModel } from "./password_kanban_model";
import { PasswordKanbanRenderer } from "./password_kanban_renderer";
import { PasswordSearchModel } from "../search/password_search_model";

export const PasswordKanbanView = {
    ...kanbanView,
    SearchModel: PasswordSearchModel,
    Controller: PasswordKanbanController,
    Model: PasswordKanbanModel,
    Renderer: PasswordKanbanRenderer,
    searchMenuTypes: ["filter", "favorite"],
};

registry.category("views").add("password_kanban", PasswordKanbanView);
