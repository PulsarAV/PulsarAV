/** @odoo-module **/

import SnippetsMenu from "@website/js/editor/snippets.editor";
import { _lt } from "@web/core/l10n/translation";

SnippetsMenu.SnippetsMenu.include({
    optionsTabStructure: [...SnippetsMenu.SnippetsMenu.prototype.optionsTabStructure, ["theme-prime-options", _lt("Theme Prime Options")]],
});
