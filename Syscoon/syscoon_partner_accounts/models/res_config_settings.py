# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_account_creation = fields.Boolean(
        related="company_id.auto_account_creation", readonly=False
    )
    receivable_sequence_id = fields.Many2one(
        "ir.sequence",
        "Receivable Sequence",
        related="company_id.receivable_sequence_id",
        readonly=False,
        domain=[("code", "=", "partner.auto.receivable")],
    )
    receivable_template_id = fields.Many2one(
        "account.account",
        "Receivable Account Template",
        related="company_id.receivable_template_id",
        readonly=False,
        domain=[("account_type", "=", "asset_receivable")],
    )
    payable_sequence_id = fields.Many2one(
        "ir.sequence",
        "Payable Sequence",
        related="company_id.payable_sequence_id",
        readonly=False,
        domain=[("code", "=", "partner.auto.payable")],
    )
    payable_template_id = fields.Many2one(
        "account.account",
        "Payable Account Template",
        related="company_id.payable_template_id",
        readonly=False,
        domain=[("account_type", "=", "liability_payable")],
    )
    use_separate_accounts = fields.Boolean(
        "Use Separate Accounts",
        related="company_id.use_separate_accounts",
        readonly=False,
    )

    def action_create_receivable_sequence(self):
        self.ensure_one()
        sequence = self._create_sequence("partner.auto.receivable", 10000)
        self.update({"receivable_sequence_id": sequence.id})

    def action_create_payable_sequence(self):
        self.ensure_one()
        sequence = self._create_sequence("partner.auto.payable", 70000)
        self.update({"payable_sequence_id": sequence.id})

    def _create_sequence(self, code, number_next):
        self.ensure_one()
        sequence = self.env["ir.sequence"].create(
            {
                "name": f"{self.env.company.name} {code}",
                "code": code,
                "number_next": number_next,
                "company_id": self.env.company.id,
            }
        )
        return sequence
