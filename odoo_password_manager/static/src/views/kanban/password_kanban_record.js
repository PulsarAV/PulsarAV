/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
const notGlobalActions = ["a", ".dropdown", ".oe_kanban_action", ".jstr-kanban-copy"].join(",");


export class PasswordKanbanRecord extends KanbanRecord {
    /*
    * Re-write to add its own classes for selected kanban record
    */
    getRecordClasses() {
        let result = super.getRecordClasses();
        if (this.props.record.selected) { result += " jstr-kanban-selected" };
        return result;
    }
    /*
    * The method to manage clicks on kanban record > add to selection always
    */
    onGlobalClick(ev) {
        if (ev.target.closest(notGlobalActions)) {
            if (ev.target.closest(".jstr-kanban-copy")) {
                this.props.record.onCopyData(ev, ev.target.closest(".jstr-kanban-copy").id);
            }
            else { return }
        }
        else { this.props.record.onRecordClick(ev, {}) };
    }
    /*
    * The method to get a record to change its values
    */
    onDragStart(event) {
        event.preventDefault(); // to avoid standard drag&drop
        if (!this.props.record.selected) {
           this.props.record.toggleSelection(true)
        };
        const selectedRecords = this.props.record.model.selectedRecords.map(function(record) {
            return { id: "nodex_" + record.id, text: record.name, icon: "nodex_update" }
        });
        const draggableElement = document.createElement("div");
        draggableElement.classList.add("jstree-default");
        draggableElement.id = "jstree-dnd";
        const draggableIcon = document.createElement("i");
        draggableIcon.classList.add("jstree-icon", "jstree-er");
        $(draggableIcon).appendTo(draggableElement);
        const dragText = selectedRecords.length == 1 ? selectedRecords[0].text : selectedRecords.length + _t(" key(s)");
        draggableElement.append(dragText);
        $.vakata.dnd.start(event, {
            jstree: true,
            obj: $("<a>", { id: "dnd_anchor", class: "jstree-anchor", href: "#" }),
            nodes: selectedRecords,
        }, draggableElement);
    }
};

PasswordKanbanRecord.template = "odoo_password_manager.PasswordKanbanRecord";
