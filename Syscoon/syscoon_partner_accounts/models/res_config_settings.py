# © 2023 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_account_creation = fields.Boolean(
        related="company_id.auto_account_creation", readonly=False
    )
    receivable_sequence_id = fields.Many2one(
        'ir.sequence', 'Receivable Sequence',
        related="company_id.receivable_sequence_id",
        readonly=False,
        domain=[('code', '=', 'partner.auto.receivable')])
    customer_number_sequence_id = fields.Many2one(
        'ir.sequence', 'Customer Number Sequence',
        related="company_id.customer_number_sequence_id",
        readonly=False,
        domain=[('code', '=', 'partner.auto.customer.number')])
    receivable_template_id = fields.Many2one(
        'account.account',
        'Receivable Account Template',
        related="company_id.receivable_template_id",
        readonly=False,
        domain=[('account_type', '=', 'asset_receivable')])
    payable_sequence_id = fields.Many2one(
        'ir.sequence',
        'Payable Sequence',
        related="company_id.payable_sequence_id",
        readonly=False,
        domain=[('code', '=', 'partner.auto.payable')])
    supplier_number_sequence_id = fields.Many2one(
        'ir.sequence',
        'Supplier Number Sequence',
        related="company_id.supplier_number_sequence_id",
        readonly=False,
        domain=[('code', '=', 'partner.auto.supplier.number')])
    payable_template_id = fields.Many2one(
        'account.account',
        'Payable Account Template',
        related="company_id.payable_template_id",
        readonly=False,
        domain=[('account_type', '=', 'liability_payable')])
    add_number_to_partner_number = fields.Boolean(
        'Add Account Number as Customer- / Supplier-Numbers',
        related="company_id.add_number_to_partner_number",
        readonly=False)
    add_number_to_partner_ref = fields.Boolean(
        'Add Customer or Supplier Number to Partner Reference',
        related="company_id.add_number_to_partner_ref",
        readonly=False)
    use_separate_partner_numbers = fields.Boolean(
        'Use separate Customer- / Supplier-Numbers',
        related="company_id.use_separate_partner_numbers",
        readonly=False)
    use_separate_accounts = fields.Boolean(
        'Use Separate Accounts',
        related="company_id.use_separate_accounts",
        readonly=False)
