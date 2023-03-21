/** @odoo-module **/

import { KanbanDynamicRecordList } from "@web/views/kanban/kanban_model";
import { useService } from "@web/core/utils/hooks";


export class PasswordKanbanDynamicRecordList extends KanbanDynamicRecordList {
    /*
    * Re-write to trigger toggle selection for the old selection 
    */
    async load() {
        await super.load();
        const selectedRecords = this.model.selectedRecords;
        _.each(this.records, function (record) {
            if (selectedRecords.find(rec => rec.id === record.resId)) {
                record.toggleSelection(true, true);
            }
        });
    }
    /*
    * Overwrite to save selected records to state
    */
    exportState() {
        const state = {
            ...super.exportState(),
            selectedRecords: this.model.selectedRecords,
        };
        return state
    }
}
