/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.AssigneeSelect2 = publicWidget.Widget.extend({
    selector: '#assignees_selection',
    events:{'change':'onChange'},
    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },
    start: function () {
        this.$target.select2({
            placeholder: "Add Assignees",
            allowClear: true
        });
        this.$target.removeClass("d-none");

    },
    onChange(ev) {
        var task_id = this.$target.data('task_id');
        var is_added = false;
        var user_id = false;
        if (ev.added){
            is_added = true;
            user_id = ev.added.element[0].id;
        }
        else if (ev.removed){
            is_added = false;
            user_id = ev.removed.element[0].id;
        }
        this.rpc("/assignees/update",{ is_added:is_added,
            user_id:user_id, task_id:task_id,
        }).then(function (data){
            window.location.reload();
        })
    }
});

export default publicWidget.registry.PortalTaskAssigneesSelection;