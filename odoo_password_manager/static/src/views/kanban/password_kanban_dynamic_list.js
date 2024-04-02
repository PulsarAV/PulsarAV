/** @odoo-module **/

import { DynamicRecordList } from "@web/model/relational_model/dynamic_record_list";


export class PasswordKanbanDynamicRecordList extends DynamicRecordList {
    /*
    * Re-write to trigger toggle selection for the old selection
    */
    setup(config, data) {
        super.setup(...arguments);
        this.reSelect();
    }
    /*
    * Re-write to trigger toggle selection for the old selection
    */
    async _load(offset, limit, orderBy, domain) {
        await super._load(...arguments);
        this.reSelect();
    }
    /*
    * The method to trigger toggle selection for the old selection
    */
    reSelect() {
        if (this.records.length) {
            const selectedRecords = this.model.selectedRecords;
            this.records.forEach(function (record) {
                if (selectedRecords.find(rec => rec.id === record.resId)) {
                    record.selected = true;
                };
            });
        };
    }
};
