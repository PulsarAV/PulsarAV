# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_account_creation = fields.Boolean(default=True)
    receivable_sequence_id = fields.Many2one(
        "ir.sequence",
        "Receivable Sequence",
        domain=[("code", "=", "partner.auto.receivable")],
    )
    payable_sequence_id = fields.Many2one(
        "ir.sequence",
        "Payable Sequence",
        domain=[("code", "=", "partner.auto.payable")],
    )
    receivable_template_id = fields.Many2one(
        "account.account", "Receivable Account Template"
    )
    payable_template_id = fields.Many2one(
        "account.account",
        "Payable Account Template",
        domain=[("type", "=", "liability_payable")],
    )
    use_separate_accounts = fields.Boolean()
