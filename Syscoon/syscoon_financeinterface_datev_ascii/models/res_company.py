# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    """Inherits the res.company class and adds several fields for the
    finance interface"""

    _inherit = "res.company"

    export_finance_interface = fields.Selection(
        selection_add=[('datev_ascii', 'DATEV ASCII Move Export')]
    )
    datev_default_journal_ids = fields.Many2many(
        'account.journal',
        string='Default Journals',
        domain="[('company_id', '=', company_id)]"
    )
    datev_export_method = fields.Selection(
        selection=[('net', 'Net'), ('gross', 'Gross')],
        string='Export Method'
    )
    datev_checks_enabled = fields.Boolean('Perform DATEV Checks', default=True)
    datev_enable_fixing = fields.Boolean(
        'Codify Moves',
        help='Sets marker in export to codify the moves when importing in DATEV.',
        default=False
    )
    datev_accountant_number = fields.Char('Tax Accountant Number', size=6)
    datev_client_number = fields.Char('Client Number', size=6)
    datev_voucher_date_format = fields.Selection(
        [("%d%m", "ddmm"), ("%d%m%y", "ddmmyy"), ("%d.%m.%y", "dd.mm.yy")],
        string="Voucher Date Format",
        help="Format:\nDay = dd\nMonth = mm\nYear= yyyy",
        default="%d%m",
    )
    datev_account_code_digits = fields.Integer(
        'Account Code Digits',
        help='Set the length of the account code digits in the export.',
        default=4
    )
    datev_remove_leading_zeros = fields.Boolean(
        'Remove Leading Zeros',
        help='Removes leading zeros on account-codes. E.g. 0670 becomes 670 in the export.'
    )
    datev_group_lines = fields.Boolean(
        'Group Lines',
        help='Group move lines with the same accounts, taxes, tax key and analytic accounts'
    )
    datev_auto_set_accounts = fields.Selection(
        selection=[],
        string='Set Accounts and Taxes'
    )
    datev_use_bedi = fields.Boolean('Use BEDI Beleglink')
