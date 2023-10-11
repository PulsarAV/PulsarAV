# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SyscoonFinanceinterfaceExport(models.TransientModel):
    _name = "syscoon.financeinterface.export"
    _description = "Export Wizard for the syscoon financeinterface"

    export_id = fields.Many2one("syscoon.financeinterface", "Export", readonly=True)
    type = fields.Selection(
        selection=[("date", "Date"), ("date_range", "Date Range")], string="Export Type"
    )
    date_from = fields.Date("Date From", default=lambda *a: time.strftime("%Y-%m-01"))
    date_to = fields.Date("Date To", default=lambda *a: time.strftime("%Y-%m-%d"))
    date = fields.Date("Date", default=lambda *a: time.strftime("%Y-%m-%d"))
    mode = fields.Selection(
        selection=[("none", "None")],
        string="Export Mode",
        required=True,
        default=lambda self: self._get_default_mode(),
    )

    def _get_default_mode(self):
        """Function to get the default selected journal ids from the company settings"""
        company_id = self.env.company
        if company_id.export_finance_interface:
            return company_id.export_finance_interface
        return

    @api.onchange("mode")
    def _onchange_mode(self):
        return

    def _get_action(self, name=None, record_id=None):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "syscoon_financeinterface.syscoon_financeinterface_action"
        )
        if name:
            action["name"] = name
        if record_id:
            action["res_id"] = record_id
        return action

    def action_start(self):
        """Start the export through the wizard"""
        if not self.mode:
            raise UserError(
                _(
                    "No Export-Method selected. Please select one or install further "
                    "Modules to provide an Export-Method!"
                )
            )
        return self._get_action()
