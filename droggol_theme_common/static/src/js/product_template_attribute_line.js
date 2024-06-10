/** @odoo-module **/

import {
    ProductTemplateAttributeLine as PTAL
} from "@sale_product_configurator/js/product_template_attribute_line/product_template_attribute_line";
import { patch } from "@web/core/utils/patch";
import { Product } from "@sale_product_configurator/js/product/product";

PTAL.props['attribute'] = {
    type: Object,
    shape: {
        id: Number,
        name: String,
        display_type: {
            type: String,
            validate: type => ["color", "multi", "pills", "radio", "select", "radio_circle", "radio_square", "radio_image"].includes(type),
        },
    },
};
PTAL.props['extraInfo'] = {
    type: Object,
};

Product.props['extra_info'] = {
    type: Object
};
patch(PTAL.prototype, {
    getPTAVTemplate() {
        switch(this.props.attribute.display_type) {
            case 'radio_circle':
                return 'saleProductConfigurator.ptav-pills';
            case 'radio_square':
                return 'saleProductConfigurator.ptav-pills';
            case 'radio_image':
                return 'droggolSaleProductConfigurator.ptav-radio-image';
        }
        return super.getPTAVTemplate();
    }
})
