/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { PasswordKanbanDynamicRecordList } from "./password_kanban_dynamic_list";
import { KanbanModel } from "@web/views/kanban/kanban_model";

export class PasswordKanbanModel extends KanbanModel {
    /*
    * Re-write to introduce selected records, so our list will be able to save previous selection
    */
    setup(params) {
        if (params.rootState) {
            // restore from previous list (used especially for switching between views)
            this.selectedRecords = params.rootState.selectedRecords || [];
        }
        else {
            this.selectedRecords = [];
        }
        super.setup(...arguments);
    }
    /*
    * The method to add/remove record from SelectedRecords
    */
    _updateModelSelection(record, selected, noReselection) {
        if (!noReselection) {
            if (selected) {
                this.selectedRecords.push(record)
            }
            else {
                this.selectedRecords = this.selectedRecords.filter(rec => rec.id != record.id)
            };
        }
    }
    /*
    * The method to save record data for selection
    */
    getSelectedData(recordData) {
        return {
            "id": recordData.id, 
            "name": recordData.name,
            "user_name": recordData.user_name,
            "link_url": recordData.link_url,
            "password_len": recordData.password_len,
        }
    }
};

export class PasswordKanbanRecord extends KanbanModel.Record {
    /**
    * The method to manage kanban records clicks: to add an item to selection
    */
    onRecordClick(ev, options = {}) {
        this.toggleSelection(!this.selected);
    }
    /*
    * Overwrite to save selection for model, not only in a record. The idea is to not update selection after each reload
    */
    toggleSelection(selected, noReselection) {
        super.toggleSelection(selected);
        this.model._updateModelSelection(this.model.getSelectedData(this.data), selected, noReselection);
        if (selected && !noReselection && this.data.user_name) {
            try {
                browser.navigator.clipboard.writeText(this.data.user_name);
            }
            catch {
                return browser.console.warn("Error! This browser doesn't allow to copy to clipboard");
            }
        };
    }
};

PasswordKanbanModel.Record = PasswordKanbanRecord;
PasswordKanbanModel.DynamicRecordList = PasswordKanbanDynamicRecordList;
