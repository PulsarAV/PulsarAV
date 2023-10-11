# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SyscoonFinanceinterfaceExport(models.TransientModel):
    _inherit = "syscoon.financeinterface.export"

    mode = fields.Selection(
        selection_add=[("datev_ascii", "DATEV ASCII")],
        ondelete={"datev_ascii": lambda recs: recs.write({"mode": "none"})},
    )
    journal_ids = fields.Many2many(
        "account.journal",
        string="Journals",
        default=lambda self: self._get_default_journal(),
        required=True,
    )

    @api.onchange("mode")
    def _onchange_mode(self):
        """Inherits the basic onchange mode"""
        res = super()._onchange_mode()
        if self.mode and self.mode == "datev_ascii":
            self.type = "date_range"
        return res

    def _get_default_journal(self):
        """Function to get the default selected journal ids from the company settings"""
        return self.env.company.datev_default_journal_ids.ids

    def action_start(self):
        """Inherit of the basic start function"""
        if self.mode == "datev_ascii":
            if self.type != "date_range":
                raise UserError(
                    _(
                        "For the DATEV ASCII move export you must select the type "
                        '"Date Range" to do an export!'
                    )
                )
            args = [self.journal_ids.ids]
            export_id = self.env["syscoon.financeinterface"].export(
                self.mode, self.date_from, self.date_to, args
            )
            return self._get_action(
                name="Financial Export Invoices", record_id=export_id.id
            )
        return super().action_start()
