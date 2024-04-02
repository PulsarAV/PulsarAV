/** @odoo-module **/

import { CANCEL_GLOBAL_CLICK, KanbanRecord } from "@web/views/kanban/kanban_record";


export class BundleKanbanRecord extends KanbanRecord {
    /*
    * The method to manage clicks on kanban record > add to selection always
    * This as well as bundle_kanban_renderer is introduced ONLY to change the context, since action of kanban loose ctx
    * To-do: control core changes
    */
    onGlobalClick(ev) {
        if (ev.target.closest(CANCEL_GLOBAL_CLICK)) {
            return;
        }
        else {
            const { archInfo, forceGlobalClick, openRecord, record } = this.props;
            const buttonContext = {};
            if (record.resModel == "password.bundle" && record.resIds) {
                Object.assign(buttonContext, {
                    with_bundle: 1,
                    default_bundle_ids: [...record.resIds],
                    default_bundle_id: record.resId,
                });
            };
            // IMPROTANT: record.context 'default_' and 'search_default_' will be cleared
            this.action.doActionButton({
                name: archInfo.openAction.action,
                type: archInfo.openAction.type,
                resModel: record.resModel,
                resId: record.resId,
                resIds: record.resIds,
                context: record.context,
                buttonContext: buttonContext,
                onClose: async () => {
                    await record.model.root.load();
                },
            });
        }
    }
};
