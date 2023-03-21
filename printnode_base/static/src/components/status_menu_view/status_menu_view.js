/** @odoo-module **/
import { useComponentToModel } from '@mail/component_hooks/use_component_to_model';
import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class PrintnodeStatusMenu extends Component {
    /**
    * @override
    */
    async setup() {
        super.setup();

        useComponentToModel({ fieldName: 'component' });
    }

    get printnodeStatusMenu() {
        return this.props.record;
    }
}

Object.assign(PrintnodeStatusMenu, {
    props: { record: Object },
    template: 'printnode_base.StatusMenu',
});

registerMessagingComponent(PrintnodeStatusMenu);
