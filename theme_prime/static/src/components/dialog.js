/** @odoo-module **/

import { Dialog } from '@web/core/dialog/dialog';
import { TpRecordSelector } from './record_selection';
import { TpUiComponent } from './ui_component';
import { TpDropDown } from './search_input';
import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';
import { useCore } from '@droggol_theme_common/js/hooks';

import { Component, useEffect, useState, onWillStart, useRef, toRaw } from "@odoo/owl";

export const Components = {
    TpRecordSelector: {Component: TpRecordSelector},
    TpUiComponent: {Component: TpUiComponent},
    TpDropDown: {Component: TpDropDown},
};

export class TpConfigDialog extends Dialog {
    setup() {
        super.setup();
        useEffect(() => {
            this.modalRef.el.classList.add('tp-snippet-config-dialog');
            if (this.modalRef.el.querySelector('.modal-dialog').classList.contains('modal-xl')) {
                this.modalRef.el.querySelector('.modal-dialog').classList.remove('modal-xl');
                this.modalRef.el.querySelector('.modal-dialog').classList.add('modal-fullscreen', 'p-0');
            }
        }, () => []);
    }
}
TpConfigDialog.components = {...Dialog.components};
TpConfigDialog.props = {...Dialog.props};

// This code is so funny, it once made a browser laugh.
// If you can understand this, you're probably a JavaScript wizard.
// TODO: Write code that makes coffee. Priorities, you know?
// Abandon all hope, ye who enter here. This files are a jungle.
// Beware of dragons! No, seriously, this code has dragons in it.
// This comment is like a fortune cookie: sweet, mysterious, and often ignored.
// May the source be with you. Always.

// And one more thing do you know why dragons are so dangerous coz "dragons" has
// 7 characters reason behind it you probably know
// Thala for a reason :)

// Anyways, [TO-DO] for my self,
// I've spread some sh*t as last year there are several spike while rendering DOM.
// We have used useState at many places and in some places it is not even needed.
// Due to that rendering is having problems as VDOM. which is changing based on browser
// Perhaps we don't like the registry concept at all we might have our own implementation someday.
// the way the components are communicating with parents and children components
// is not quite right we will do something really different.
// Also, the way we are manipulating the history is really bad will do refactoring.
export class TpSnippetConfigDialog extends Component {
    setup() {
        super.setup();
        this.contentClass = 'tp_snippet_config_dialog';
        this.supportedComponents = useState({components: []});
        this.previewContainer = useRef('tp-preview-container');
        this.componentService = useService('shared_component_service');
        this.title = "Odoo";
        if (!this.isReadOnly) {
            this.tpWebsite = useService('website');
            let { metadata: { title }, name } = this.tpWebsite.currentWebsite;
            this.title = title || 'title';
        }
        this.videoURL = this.props.videoURL || 'https://youtu.be/raKo6vSpcR0';
        this.previewState = useState({templateID: this.props.snippetID,HasRecords: false,history: [],activeStep: 1});
        this.websiteName = name;
        this.prepareComponents();
        this._coreProps = {
            updateSelectionComponentValue: this.updateSelectionComponentValue.bind(this),
            updateUiComponentValue: this.updateUiComponentValue.bind(this),
            changeValue: this._onChangeComponentValue.bind(this),
        };
        onWillStart(async () => {
            if (this.registryToUse) {
                this.allSnippets = await this.componentService._fetchRecords({ model: 'ir.ui.view', extras: { templateIDs: this.templateIDs, registryToUse: this.registryToUse } });
                if (this.isReadOnly) {
                    this.allSnippets = this.allSnippets.filter((snippet) => {
                        return !['s_mega_menu_category_tabs_snippet', 's_tp_mega_menu_category_snippet'].includes(snippet.id);
                    });
                }
                this.allSnippets.forEach((snippet) => {
                    let { TpRecordSelector } = this._getSnippetConfig(snippet.id).widgets
                    snippet['resModel'] = TpRecordSelector ? TpRecordSelector.model : 'product.template';
                });
                let firstSnippet = this.allSnippets.filter((snippet) => { return snippet.id == this.snippetID })[0];
                this.previewState.templateID = firstSnippet && firstSnippet.id || false;
                this.body = firstSnippet && firstSnippet.html || false;
            }
            this.size = this.previewState.templateID ? 'xl' : 'md';
            this.footer = this.previewState.templateID ? false : true;
        });
        useCore({});
    }
    get isReadOnly() {
        return this.props.isReadOnly || false;
    }
    get snippetID() {
        return this.props.snippetID;
    }
    get hasUiComponent() {
        if (!this.previewState.templateID) {
            return false;
        }
        let { widgets } = this._getSnippetConfig(this.previewState.templateID);
        return 'TpUiComponent' in widgets;
    }
    get hasSelectionComponent() {
        return 'TpRecordSelector' in this.props.components;
    }
    get registryToUse() {
        return this.props.registryToUse;
    }
    get allSnippptsDropdown() {
        let buttonClasses = { menuClass: 'row ps-2 pe-0 g-0 tp-snippet-dropdown', menuItemClass: 'col-6 pe-2 position-relative', dropDownPlaceholder: 'theme_prime.tp_snippet_dropdown_placeholder', buttonClasses: "btn d-flex justify-content-between align-items-center btn-default shadow-sm fw-light w-100 mx-auto p-2 bg-white" };
        return { props: { ...buttonClasses, name: "snippet_dropdown", value: this.previewState.templateID, records: this.allSnippets }, component: Components.TpDropDown.Component };
    }
    _onChangeComponentValue(value, name) {
        this.previewState.templateID = value;
        let data = this._getConfigParameter(value);
        this._stateCleanup(data);
        this.prepareComponents(data);
        this.render(true);
        this._reloadPreview();
    }
    _getSnippetBody(snippet) {
        return this.allSnippets.filter((s) => { return s.id === snippet })[0];
    }
    _getSnippetConfig(snippet) {
        return registry.category(this.registryToUse).get(snippet);
    }
    get _isLazyLoad() {
        let { defaultValue } = this._getSnippetConfig(this.previewState.templateID);
        return defaultValue && defaultValue.lazy || false;
    }
    _getConfigParameter(snippet) {
        let snippetData = this._getSnippetBody(snippet);
        this.body = snippetData.html;
        this.$target = new DOMParser().parseFromString(snippetData.html, 'application/xhtml+xml').documentElement;
        let snippetConfig = this._getSnippetConfig(snippet);
        let defaultValue = snippetConfig.defaultValue || {};
        let params = { videoURL: defaultValue.videoURL, components: {}, snippetID: defaultValue.noSnippet ? false : snippet};

        for (let component in snippetConfig.widgets) {
            const value = snippetConfig.widgets[component];
            switch (component) {
                case 'TpRecordSelector':
                    params['components']['TpRecordSelector'] = Object.assign({}, value, defaultValue, { componentData: this._getValueFromAttr(this.$target, 'data-selection-info') });
                    break;
                case 'TpUiComponent':
                    params['components']['TpUiComponent'] = { ...value, ...defaultValue, componentData: { ...this._getValueFromAttr(this.$target, 'data-ui-config-info') }, $target: this.$target };
            }
        }
        return params;
    }
    _getValueFromAttr($target, attr) {
        let attrValue = $target.getAttribute(attr);
        return attrValue ? JSON.parse(attrValue) : false;
    }
    getRecordFromData(records, recordID) {
        return records.find((record) => record.id === recordID);
    }
    updateSelectionComponentValue(key, value, name) {
        if (key) {
            this.state.TpRecordSelector[key] = value;
        } else {
            Object.keys(value).forEach(comp => {
                this.state.TpRecordSelector[comp] = value[comp];
            })
        }
        if (this.hasUiComponent && this._isLazyLoad) {
            let records = [];
            let defaults = { style: "s_tp_hierarchical_category_style_1", productListing: "bestseller", child: 4, limit: 4, brand: false, label: false, count: false, background: false };
            let configData = toRaw(this.state.TpUiComponent.categoryTabsConfig.records);
            let activeRecordID = false;
            value.forEach(res_ID => {
                let data = this.getRecordFromData(configData, res_ID);
                if (data) {
                    records.push(data);
                } else {
                    records.push({ ...defaults, id: res_ID });
                }
                activeRecordID = value[0];
            });
            this.updateUiComponentValue('categoryTabsConfig', { activeRecordID: activeRecordID, records: records });
        }
        this.previewState.HasRecords = this.HasRecords;
        this._reloadPreview();
        this._updateHistoryState();
    }
    updateUiComponentValue(key, value) {
        this.state.TpUiComponent[key] = value;
        this._reloadPreview();
        this._updateHistoryState();
    }
    toggleViewPort(mode) {
        if (this.previewContainer.el) {
            this.previewContainer.el.src = this.previewContainer.el.src;
        }
        this.state.isMobile = mode === 'mobile' ? true : false;
    }
    _onClickCommand(command) {
        let currentStep = toRaw(this.previewState.activeStep);
        switch (command) {
            case 'undo':
                this.previewState.activeStep = currentStep - 1 <= 0 ? 1 : currentStep - 1;
                break;
            case 'redo':
                this.previewState.activeStep = currentStep + 1 >= this.previewState.history.length ? this.previewState.history.length : currentStep + 1;
                break;
        }
        // getCurrent state from history
        let state = this.previewState.history[this.previewState.activeStep-1];
        let {templateID} = state;
        // Prepare data compatible for prepareComponents method
        let defaultParams = this._getConfigParameter(templateID);
        Object.keys(defaultParams.components).forEach(comp => {
            let value = defaultParams.components[comp];
            value['componentData'] = this._replicateObject(state.state[comp]);
        });
        this.prepareComponents(this._replicateObject(defaultParams), true);
        this.previewState.templateID = templateID;
        this.render(true);
        this._reloadPreview();
    }
    _replicateObject(data) {
        // Just wanted to make sure that we don't mashed up the states
        return JSON.parse(JSON.stringify(data))
    }
    save() {
        let result = {...this.state};
        if (this.registryToUse && this.previewState.templateID) {
            let template = this.getRecordFromData(this.allSnippets, this.previewState.templateID)
            result = { ...result, $target: template.html, templateID: this.previewState.templateID };
        }
        this.props.save(result);
        this.props.close();
    }
    _onDiscardChange() {
        this.props.onDiscard();
        this.props.close();
    }
    _stateCleanup(data) {
        Object.keys(this.state).forEach(comp => {
            if (!(comp in data.components)) {
                delete this.state[comp];
            }
        });
    }
    _updateHistoryState() {
        if (!this.previewState.templateID) {
            return;
        }
        // Onchange UI or Records update history state
        let { history } = this.previewState;
        let lastStep = history[this.previewState.activeStep - 1];
        Object.assign(lastStep.state, this._replicateObject(this.state));
    }
    // hardRestore flag will be set when it calls from history buttons
    prepareComponents(snippetData, hardRestore) {
        let data = snippetData || this.props;
        let state = {isMobile: false};
        Object.keys(data.components).forEach(comp => {
            let value =  data.components[comp];
            this.forceVisible = value.forceVisible ? value.forceVisible : false;
            state[comp] = value && value.componentData && Object.keys(value.componentData).length ? value.componentData : {...value.defaultVal};
        });
        if (!this.state) {
            this.state = useState(state);
        } else {
            this._stateCleanup(data);
            Object.assign(this.state, state);
        }
        if (!hardRestore) {
            let historyState = this._replicateObject(state);
            // Flush the future history steps
            if (this.previewState.activeStep < this.previewState.history.length) {
                this.previewState.history.length = this.previewState.activeStep;
            }
            // Add history steps
            this.previewState.history.push({ state: historyState, templateID: this.previewState.templateID});
            this.previewState.activeStep = this.previewState.history.length;
        }
        this.supportedComponents.components = [];
        this.previewState.HasRecords = this.HasRecords;
        Object.keys(data.components).forEach(comp => {
            let value = this.state[comp];
            this.supportedComponents.components.push({ ...Components[comp], props: { extras: { ...data.components[comp], isReadOnly: this.isReadOnly, templateID: this.previewState.activeStep }, componentData: value, allData: this.state, HasRecords: this.previewState.HasRecords }, name: comp});
        });
    }
    _onPreviewLoaded(){
        this.previewContainer.el.contentWindow.addEventListener('TP_WRAPPER_READY', (event) => {
            this.previewContainer.el.classList.add('tp-preview-loaded');
            this._reloadPreview();
        });
    }
    toJSONstringify(data) {
        // just wanted to make sure no proxy objects are there
        return JSON.stringify(data);
    }
    _reloadPreview(){
        if (this.previewContainer.el && this.previewContainer.el.contentDocument && this.previewContainer.el.contentDocument.querySelector('#tp_wrap')) {
            let wrapper = this.previewContainer.el.contentDocument.querySelector('#tp_wrap');
            wrapper.innerHTML = this.body;
            this.target = wrapper.querySelector('.tp-droggol-builder-snippet');
            this._setStateToDOM();
            wrapper.dispatchEvent(new CustomEvent('tp-reload'));
        }
    }
    _setStateToDOM(){
        Object.keys(this.state).forEach(component => {
            let value = this.state[component];
            switch (component) {
                case 'TpRecordSelector':
                    this.target.setAttribute('data-selection-info', JSON.stringify(value));
                    break;
                case 'TpUiComponent':
                    this.target.setAttribute('data-ui-config-info', JSON.stringify(value));
                    break;
            }
        });
    }
    get templateIDs(){
        let SnippetRegistry = registry.category(this.registryToUse);
        let dbIDs = []
        Object.keys(SnippetRegistry.content).forEach(function (snippetID) {
            let prefix = snippetID.includes('mega_menu') ? 'droggol_theme_common.' : 'theme_prime.';
            dbIDs.push(prefix + snippetID);
        });
        return dbIDs;
    }
    get HasRecords(){
        let { TpRecordSelector } = this.state;
        if (this.forceVisible) {
            return true;
        }
        if (!TpRecordSelector) {
            return true;
        }
        let hasRec = TpRecordSelector.selectionType === 'advance' ? true : false;
        if (TpRecordSelector && TpRecordSelector.selectionType === 'manual' && TpRecordSelector.recordsIDs.length) {
            hasRec = true;
        }
        return hasRec;
    }
}
TpSnippetConfigDialog.template = 'theme_prime.snippetConfigDialog';
TpSnippetConfigDialog.components = { TpConfigDialog, TpRecordSelector, TpDropDown};
