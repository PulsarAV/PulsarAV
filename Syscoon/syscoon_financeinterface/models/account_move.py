# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    export_id = fields.Many2one("syscoon.financeinterface", "Export", copy=False)
    export_manual = fields.Boolean("Set Account Counterpart")
    export_account_counterpart_manual = fields.Many2one(
        "account.account", help="Set counterpart account manually"
    )
    export_account_counterpart = fields.Many2one(
        "account.account",
        compute="_get_export_datev_account",
        help="Technical field needed for move exports",
    )
    export_finance_interface_active = fields.Boolean(
        related="company_id.export_finance_interface_active"
    )
    show_export_to_draft_button = fields.Boolean(
        compute="_compute_export_reset_to_draft_button"
    )

    @api.depends('export_id')
    def _compute_export_reset_to_draft_button(self):
        for move in self:
            move.show_export_to_draft_button = move.export_id and move.state in (
                "posted",
                "cancel",
            )

    def check_module_installed(self, module_name):
        # Search for the module in the ir.module.module model
        module = self.env['ir.module.module'].search([('name', '=', module_name)])

        # Check if the module exists and is installed
        return bool(module and module.state == "installed")

    @api.depends("journal_id", "line_ids", "journal_id.default_account_id")
    def _get_export_datev_account(self):  # noqa: C901
        """
        Set the account counterpart for the move autmaticaly
        """
        for move in self:
            move.export_account_counterpart = False
            # If move has an invoice, return invoice's account_id
            default_account = move.journal_id.default_account_id
            if move.is_invoice(include_receipts=True):
                payment_term_lines = move.line_ids.filtered(
                    lambda line: line.account_id.account_type
                    in ("asset_receivable", "liability_payable")
                )
                check_hr_expense_installed = self.check_module_installed("hr_expense")
                if payment_term_lines[:1].account_id:
                    move.export_account_counterpart = payment_term_lines[:1].account_id
                    continue
                if check_hr_expense_installed and move.expense_sheet_id:
                    move.export_account_counterpart = default_account.id
                    continue
            # If move belongs to a bank journal, return the journal's account
            # (debit/credit should normally be the same)
            if move.journal_id.type == "bank" and default_account:
                move.export_account_counterpart = default_account.id
                continue
            # If the move is an automatic exchange rate entry, take the gain/loss account
            # set on the exchange journal
            if (
                move.journal_id.type == "general"
                and move.journal_id == self.env.company.currency_exchange_journal_id
            ):
                accounts = [
                    move.company_id.income_currency_exchange_account_id,
                    move.company_id.expense_currency_exchange_account_id,
                ]
                move_lines = move.line_ids.filtered(lambda r: r.account_id in accounts)
                if len(move_lines) == 1:
                    move.export_account_counterpart = move_lines.account_id
                    continue
            if move.journal_id.type == 'general':
                rp_accounts = move.line_ids.filtered(
                    lambda line: line.account_id.account_type
                    in ("asset_receivable", "liability_payable")
                )
                if rp_accounts and rp_accounts[0].account_id:
                    move.export_account_counterpart = rp_accounts[0].account_id
                    continue

            account_id = False
            # Look for an account used a single time in the move,
            # that has no originator tax
            aml_debit = self.env['account.move.line']
            aml_credit = self.env['account.move.line']
            for aml in move.line_ids:
                if aml.debit > 0:
                    aml_debit |= aml
                if aml.credit > 0:
                    aml_credit |= aml
            if len(aml_debit) == 1:
                account_id = aml_debit[:1].account_id
            elif len(aml_credit) == 1:
                account_id = aml_credit[:1].account_id
            else:
                aml_debit_wo_tax = [a for a in aml_debit if not a.tax_line_id]
                aml_credit_wo_tax = [a for a in aml_credit if not a.tax_line_id]
                if len(aml_debit_wo_tax) == 1:
                    account_id = aml_debit_wo_tax[0].account_id
                elif len(aml_credit_wo_tax) == 1:
                    account_id = aml_credit_wo_tax[0].account_id
            if not account_id:
                account_list = []
                for line in move.line_ids:
                    if line.account_id.account_type in (
                        "asset_receivable",
                        "liability_payable",
                    ):
                        account_list.append(line.account_id)
                if not account_list:
                    for line in move.line_ids:
                        account_list.append(line.account_id)
                if account_list:
                    counts = {
                        account_id: account_list.count(account_id)
                        for account_id in account_list
                    }
                    account_id = max(counts, key=counts.get)
                if move.export_account_counterpart_manual:
                    account_id = move.export_account_counterpart_manual.id
            move.export_account_counterpart = account_id
