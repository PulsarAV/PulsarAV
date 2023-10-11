# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, tools


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    @tools.ormcache("frozenset(self.env.user.groups_id.ids)", "debug")
    def _visible_menu_ids(self, debug=False):
        visible = super()._visible_menu_ids(debug=debug)
        if not self.env.company.export_finance_interface_active:
            finance_interface_menu = self.env.ref(
                "syscoon_financeinterface.menu_finance_interface"
            )
            if finance_interface_menu.id in visible:
                visible.remove(finance_interface_menu.id)
        return visible
