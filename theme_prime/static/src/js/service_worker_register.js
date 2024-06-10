/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { sprintf } from "@web/core/utils/strings";
import { cookie } from "@web/core/browser/cookie";
import { isIOS, isDisplayStandalone } from "@web/core/browser/feature_detection";

const html = document.documentElement;
const websiteID = html.getAttribute("data-website-id") || 0;

const PWAInstallBanner = publicWidget.Widget.extend({
    template: "theme_prime.pwa_popup",
    events: {
        "click .close": "_onClickClose",
    },
    init() {
        this._super(...arguments);
        this.isIos = isIOS();
        this.appName = odoo.dr_theme_config.pwa_name;
        this.websiteID = websiteID;
    },
    _onClickClose: function () {
        this.trigger_up("close_via_prompt");
    },
});

publicWidget.registry.PWAActivationEvents = publicWidget.Widget.extend({
    selector: "#wrapwrap",
    custom_events: {
        close_via_prompt: "_onPromptClose",
    },
    async start() {
        const superResult = await this._super(...arguments);
        if (odoo.dr_theme_config.pwa_active) {
            this.activateServiceWorker();
        } else {
            this.deactivateServiceWorker();
        }
        return superResult;
    },
    showInstallBanner() {
        if (isIOS()) {
            if (!isDisplayStandalone()) {
                if (!cookie.get(sprintf("tp-pwa-popup-%s", websiteID))) {
                    this.installBanner = new PWAInstallBanner(this);
                    this.installBanner.appendTo(document.body);
                }
            }
        }
    },
    activateServiceWorker () {
        if (navigator.serviceWorker) {
            navigator.serviceWorker.register("/service_worker.js").then((registration) => {
                console.log("ServiceWorker registration successful with scope:", registration.scope);
                this.showInstallBanner();
            }).catch(function (error) {
                console.log("ServiceWorker registration failed:", error);
            });
        }
    },
    deactivateServiceWorker () {
        if (navigator.serviceWorker) {
            navigator.serviceWorker.getRegistrations().then(function (registrations) {
                registrations.forEach(r => {
                    r.unregister();
                    console.log("ServiceWorker removed successfully");
                });
            }).catch(function (err) {
                console.log("Service worker unregistration failed: ", err);
            });
        }
    },
    _hideInstallBanner: function () {
        cookie.set(sprintf("tp-pwa-popup-%s", websiteID), true);
        if (this.installBanner) {
            this.installBanner.destroy();
        }
    },
    _onPromptClose: function () {
        this._hideInstallBanner();
    },
});
