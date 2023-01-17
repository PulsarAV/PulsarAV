/** @odoo-module **/

/*
This file includes few snippets related to storing/clearing information about workstation
printers/scales. A bit 'hacky' thing :)

The basic idea is to store the information about computer ID (generated in this script) in the
local storage and then use it to store the information about printers/scales in the database.
*/

import { browser } from '@web/core/browser/browser';
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { uuid } from "@web/views/utils";
import session from 'web.session';

const { xml, Component } = owl;


class DirectPrintMainComponent extends Component {
    /*
    This component manages workstation devices
    */
    setup() {
        super.setup();

        this.user = useService("user");

        if (session.printnode_enabled) {
            this._setOrCreateUUID();
        }
    }

    async _setOrCreateUUID() {
        // Check if UUID is already set
        let deviceUUID = browser.localStorage.getItem('printnode_base.uuid');

        if (!deviceUUID) {
            // Create new UUID
            deviceUUID = uuid();
            browser.localStorage.setItem('printnode_base.uuid', deviceUUID);
        }

        // Set UUID to context
        this.user.updateContext({ 'printnode_workstation_uuid': deviceUUID });
    }
};

Object.assign(DirectPrintMainComponent, {
    props: {},
    template: xml`<div/>`,
});

registry.category("main_components").add(
    "DirectPrintMainComponent",
    { Component: DirectPrintMainComponent, props: {} }
);
