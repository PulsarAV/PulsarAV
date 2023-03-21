/** @odoo-module **/

import { SearchModel } from "@web/search/search_model";
import { Domain } from "@web/core/domain";

export class PasswordSearchModel extends SearchModel {
    /*
    * Overwrite to introduce jsTreeDomain
    */
    setup(services) {
        this.jsTreeDomain = [];
        this.kanbanOrder = {name: "name", asc: true}; // this is default order
        super.setup(...arguments);
    }
    /*
    * Overwrite to add our jsTree
    * Regretfully, none of child method can be triggered, so we have to redefine the whole return
    */
    _getDomain(params = {}) {
        var domain =  super._getDomain(...arguments);        
        try {
            domain = Domain.and([domain, this.jsTreeDomain]);
            return params.raw
                ? domain
                : domain.toList(Object.assign({}, this.globalContext, this.userService.context));
        } catch (error) {
            throw new Error(
                `${this.env._t("Failed to evaluate the domain")} ${domain.toString()}.\n${
                    error.message
                }`
            );
        };
    }
    /*
    * Overwrite to introduce our own kanban order
    */
    _getOrderBy() {
        return [this.kanbanOrder, {"name": "id"}];
    }
    /*
    * The method to save received jsTree domain
    */
    toggleJSTreeDomain(domain, kanbanOrder) {
        this.jsTreeDomain = domain;
        this.kanbanOrder = kanbanOrder;
        this._notify();
    }
    /*
    * The method to save the current kanban order
    */
    updateOrderBy(kanbanOrder) {
        this.kanbanOrder = kanbanOrder;
    }
}
