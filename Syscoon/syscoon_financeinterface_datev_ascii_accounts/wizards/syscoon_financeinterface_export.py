# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SyscoonFinanceinterfaceExport(models.TransientModel):
    _inherit = 'syscoon.financeinterface.export'

    mode = fields.Selection(
        selection_add=[("datev_ascii_accounts", "DATEV ASCII Accounts")],
        ondelete={"datev_ascii_accounts": lambda recs: recs.write({"mode": "none"})},
    )
    type = fields.Selection(selection_add=[("date", "Single Date")])
    datev_ascii_accounts_kind = fields.Selection(
        [("rewe", "DATEV Standard (Rewe)"), ("duo", "DATEV Unternehmen Online")],
        string="Kind",
        default=lambda self: self.env.company.datev_ascii_accounts_kind,
    )
    datev_ascii_accounts_account_kind = fields.Selection(
        [("all", "All"), ("new", "Only New")], string="Accunts to export"
    )
    datev_ascii_accounts_account = fields.Selection(
        [("debit", "Debit Accounts"), ("credit", "Credit Accounts"), ("both", "Both")],
        string="Accounts",
    )

    @api.onchange('mode')
    def _onchange_mode(self):
        res = super()._onchange_mode()
        if self.mode and self.mode == 'datev_ascii_accounts':
            self.type = 'date'
        return res

    def action_start(self):
        """Inherit of the basic start function"""
        if self.mode == 'datev_ascii_accounts':
            if self.type != 'date':
                raise UserError(
                    _(
                        'For the DATEV ASCII account export you must select the type "Date" to do an export!'
                    )
                )
            args = [
                self.datev_ascii_accounts_kind,
                self.datev_ascii_accounts_account_kind,
                self.datev_ascii_accounts_account,
            ]
            export_id = self.env["syscoon.financeinterface"].export(
                self.mode, self.date, False, args
            )
            return self._get_action(
                name="Financial Export Accounts", record_id=export_id.id
            )
        return super().action_start()
