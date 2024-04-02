/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { checkBundleSecurity } from "@odoo_password_manager/views/dialogs/password_login_dialog/password_login_dialog";
import { Domain } from "@web/core/domain";
import { loadCSS, loadJS } from "@web/core/assets";
import { PwmJsTreeContainer } from "@odoo_password_manager/components/pwm_jstree_container/pwm_jstree_container";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart } = owl;

const componentModel = "password.key";
const searchSections = {
    "password_tags": _lt("Tags"),
    "password_types": _lt("Types"),
    "portal_vaults": _lt("Portal Vaults"),
}


export class PasswordNavigation extends Component {
    static template = "odoo_password_manager.PasswordNavigation";
    static components = { PwmJsTreeContainer };
    static props = {
        kanbanList: { type: Object },
        bundleIds: { type: Array },
        canUpdate: { type: Boolean },
    };
    /*
    * Re-write to import required services and update props on the component start
    */
    setup() {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.kanbanOrder = "name"; // this is default order
        this.asc = false;
        this.jsTreeDomain = [];
        this.jsTreeDomains = {};
        onWillStart(async () => {
            const proms = [
                loadJS("/odoo_password_manager/static/lib/jstree/jstree.min.js"),
                loadCSS("/odoo_password_manager/static/lib/jstree/themes/default/style.css"),
            ]
            return Promise.all(proms);
        });
    }
    /*
    * The method to prepare jstreecontainer props
    */
    getJsTreeProps(key) {
        return {
            jstreeTitle: searchSections[key],
            jstreeId: key,
            onUpdateSearch: this.onUpdateSearch.bind(this),
            kanbanModel: this.props.kanbanList.model,
            bundleIds: this.props.bundleIds,
            canUpdate: this.props.canUpdate,
        }
    }
    /*
    * The method to prepare the domain by all JScontainers and notify searchmodel
    */
    onUpdateSearch(jstreeId, domain) {
        var jsTreeDomain = this._prepareJsTreeDomain(jstreeId, domain)
        if (this.jsTreeDomain != jsTreeDomain) {
            this.jsTreeDomain = jsTreeDomain;
            this.env.searchModel.toggleJSTreeDomain(this.jsTreeDomain, {name: this.kanbanOrder, asc: !this.asc});
        }
    }
    /*
    * The method to prepare domain based on all jstree components
    */
    _prepareJsTreeDomain(jstreeId, domain) {
        var jsTreeDomain = [];
        this.jsTreeDomains[jstreeId] = domain;
        Object.values(this.jsTreeDomains).forEach(function (val_domain) {
            jsTreeDomain = Domain.and([jsTreeDomain, val_domain])
        });
        return jsTreeDomain
    }
    /*
    * The method to select all records that satisfy search criteria
    * It requires orm call since not all records are shown on the view
    * Security check is done on the kanban rendering
    */
    async _onSelectAll() {
        const kanbanModel = this.props.kanbanList.model;
        var fullDomain = this.env.searchModel._getDomain();
        if (fullDomain.length != 0) {
            const selectedRecords = kanbanModel.selectedRecords.map((rec) => rec.id);
            fullDomain = Domain.or([fullDomain, [["id", "in", selectedRecords]]]).toList();
        }
        kanbanModel.selectedRecords = await this.orm.searchRead(
            componentModel, fullDomain, ["name", "user_name", "link_url", "password_len"]
        );
        await kanbanModel.root.load();
        kanbanModel.notify();
    }
    /*
    * The method to reseqeunce kanban list
    * We clear orderBy each time since the UI assumes sorting only by a single criteria
    */
    async _applySorting() {
        this.props.kanbanList.config.orderBy = [];
        this.props.kanbanList.config.orderBy.push({name: this.kanbanOrder, asc: this.asc});
        this.props.kanbanList.config.orderBy.push({name: "id"});
        this.env.searchModel.updateOrderBy({name: this.kanbanOrder, asc: !this.asc});
        await this.props.kanbanList.sortBy(this.kanbanOrder);
    }
    /*
    * The method to sort records by specific field (always in desc order)
    */
    async _onApplySorting(event) {
        this.kanbanOrder = event.currentTarget.value;
        this.asc = false;
        await this._applySorting();
    }
    /*
    * The method to sort records by previously chosen field in the reverse (to the previously adapted) order
    */
    async _onApplyReverseSorting() {
        this.asc = !this.asc;
        await this._applySorting();
    }
};
