# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    """ Inherits the res.company class and adds several fields for the finance interface"""
    _inherit = 'res.company'

    export_finance_interface = fields.Selection(
        selection_add=[("datev_ascii_accounts", "DATEV ASCII Account Export")]
    )
    datev_ascii_accounts_kind = fields.Selection(
        [("rewe", "DATEV Standard (Rewe)"), ("duo", "DATEV Unternehmen Online")],
        string="DATEV ASCII Export Kind",
    )
