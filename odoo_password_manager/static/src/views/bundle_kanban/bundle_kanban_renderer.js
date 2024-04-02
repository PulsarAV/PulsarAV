/** @odoo-module **/

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { BundleKanbanRecord } from "./bundle_kanban_record";

export class BundleKanbanRenderer extends KanbanRenderer {};

BundleKanbanRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: BundleKanbanRecord,
};

