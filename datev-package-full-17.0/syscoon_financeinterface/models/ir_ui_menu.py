# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.http import request


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.returns("self")
    def _filter_visible_menus(self):
        cids = request.httprequest.cookies.get(
            "cids", str(request.env.user.company_id.id)
        )
        active_company = self.env["res.company"].browse(
            [int(cid) for cid in cids.split(",")]
        )[:1]
        visible_ids = super()._filter_visible_menus()
        if not active_company.export_finance_interface_active:
            finance_interface_menu = self.env.ref(
                "syscoon_financeinterface.menu_finance_interface"
            )
            if finance_interface_menu.id in visible_ids.ids:
                visible_ids.filtered(lambda m: m.id != finance_interface_menu.id)
        return visible_ids
