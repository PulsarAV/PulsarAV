# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SyscoonFinanceinterfaceExport(models.TransientModel):
    _inherit = "syscoon.financeinterface.export"

    mode = fields.Selection(
        selection_add=[("datev_xml", "DATEV XML")],
        ondelete={"datev_xml": lambda recs: recs.write({"mode": "none"})},
    )
    xml_mode = fields.Selection(
        [("standard", "Standard"), ("extended", "Extended"), ("bedi", "BEDI Link")],
        string="XML-Export Methode",
        help="Export Methode: Standard: without Accounts, Extended: with Accounts",
    )
    xml_invoices = fields.Selection(
        [
            ("customers", "Customer Invoices"),
            ("vendors", "Vendor Invoices"),
            ("both", "Both"),
        ],
        string="Invoices",
    )

    @api.onchange("mode")
    def _onchange_mode(self):
        """Inherits the basic onchange mode"""
        res = super()._onchange_mode()
        company_id = self.env.company
        if self.mode and self.mode == "datev_xml":
            self.xml_mode = company_id.export_xml_mode
            self.type = "date_range"
        return res

    def action_start(self):
        """Inherit of the basic start function"""
        if self.mode == "datev_xml":
            if self.type != "date_range":
                raise UserError(
                    _(
                        'For the DATEV XML export you must select the type "Date Range" to do an export!'
                    )
                )
            args = [self.xml_mode, self.xml_invoices]
            export_id = self.env["syscoon.financeinterface"].export(
                self.mode, self.date_from, self.date_to, args
            )
            return self._get_action(
                name="Financial Export Invoices", record_id=export_id.id
            )
        return super().action_start()
