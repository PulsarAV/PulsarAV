/** @odoo-module **/

import "@website/js/content/menu";
import { WebsiteRoot } from "@website/js/content/website_root";
import publicWidget from "@web/legacy/js/public/public_widget";
import { hasTouch } from "@web/core/browser/feature_detection";
import { SIZES, utils as uiUtils } from "@web/core/ui/ui_service";

const isMobileEnv = uiUtils.getSize() <= SIZES.LG && hasTouch();

// Enable bootstrap tooltip
$(document).ready(function () {
    $(document.body).tooltip({ selector: "[data-bs-toggle='tooltip']" });
});

// Back to top button
const backToTopButtonEl = document.querySelector(".tp-back-to-top");
if (backToTopButtonEl) {
    backToTopButtonEl.classList.add("d-none");
    if (!isMobileEnv) {
        const wrapwrapEl = document.getElementById("wrapwrap");
        wrapwrapEl.addEventListener("scroll", ev => {
            if (wrapwrapEl.scrollTop > 800) {
                backToTopButtonEl.classList.remove("d-none");
            } else {
                backToTopButtonEl.classList.add("d-none");
            }
        });
        backToTopButtonEl.addEventListener("click", ev => {
            ev.preventDefault();
            wrapwrapEl.scrollTo({ top: 0, behavior: "smooth" });
        });
    }
}

// Pricelist make selectable
WebsiteRoot.include({
    events: Object.assign({}, WebsiteRoot.prototype.events, {
        "click .dropdown-menu .tp-select-pricelist": "_onClickTpPricelist",
        "change .dropdown-menu .tp-select-pricelist": "_onChangeTpPricelist",
    }),
    _onClickTpPricelist: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
    },
    _onChangeTpPricelist: function (ev) {
        window.location = ev.currentTarget.value;
    },
});

// FIX: Affix header glitch on some devices having no footer pages(like checkout page).
publicWidget.registry.StandardAffixedHeader.include({
    _updateHeaderOnScroll: function (scroll) {
        if (!$("#wrapwrap footer").length) {
            this.destroy();
            return;
        }
        this._super(...arguments);
    }
});

publicWidget.registry.FixedHeader.include({
    _updateHeaderOnScroll: function (scroll) {
        if (!$("#wrapwrap footer").length) {
            this.destroy();
            return;
        }
        this._super(...arguments);
    }
});
