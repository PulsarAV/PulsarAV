# © 2023 syscoon GmbH (<https://syscoon.com>)
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
    customer_number_sequence_id = fields.Many2one(
        "ir.sequence",
        "Customer Number Sequence",
        domain=[("code", "=", "partner.auto.customer.number")],
    )
    payable_sequence_id = fields.Many2one(
        "ir.sequence",
        "Payable Sequence",
        domain=[("code", "=", "partner.auto.payable")],
    )
    supplier_number_sequence_id = fields.Many2one(
        "ir.sequence",
        "Supplier Number Sequence",
        domain=[("code", "=", "partner.auto.supplier.number")],
    )
    receivable_template_id = fields.Many2one(
        "account.account", "Receivable Account Template"
    )
    payable_template_id = fields.Many2one(
        "account.account",
        "Payable Account Template",
        domain=[("type", "=", "liability_payable")],
    )
    add_number_to_partner_number = fields.Boolean(
        "Add Account Number to Partner Numbers"
    )
    add_number_to_partner_ref = fields.Boolean(
        "Add Customer or Supplier Number to Partner Reference"
    )
    use_separate_partner_numbers = fields.Boolean(
        "Use separate Customer- / Supplier-Numbers"
    )
    use_separate_accounts = fields.Boolean("Use Separate Accounts")
