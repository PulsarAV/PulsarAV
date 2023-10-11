# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    datev_vatid_required = fields.Boolean(
        'DATEV VAT-ID',
        help='Is required when transferring a sales VAT-ID number from the partner (e.g. EU-Invoice)')
    datev_automatic_account = fields.Boolean('DATEV Automatic Account')
    datev_automatic_tax = fields.Many2many(
        'account.tax',
        string='DATEV Automatic Tax',
        domain=[('datev_tax_key', '!=', 0)]
    )
    datev_no_tax = fields.Boolean(
        'DATEV No Tax',
        help='Use bookingkey 40 if no tax is used in the move line.'
    )
    export_finance_interface_active = fields.Boolean(
        related="company_id.export_finance_interface_active"
    )


class AccountTax(models.Model):
    _inherit = 'account.tax'

    datev_tax_key = fields.Char('DATEV Tax Key', default=0, required=True)
    datev_tax_case = fields.Char('DATEV Tax Case')
    datev_country_id = fields.Many2one("res.country")
    export_finance_interface_active = fields.Boolean(
        related="company_id.export_finance_interface_active"
    )
