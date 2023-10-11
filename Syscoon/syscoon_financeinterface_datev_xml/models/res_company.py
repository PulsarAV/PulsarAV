# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    export_finance_interface = fields.Selection(
        selection_add=[('datev_xml', 'DATEV XML Document Data')]
    )
    export_xml_mode = fields.Selection(
        [("standard", "Standard"), ("extended", "Extended")],
        string="XML-Export Methode",
        help="Export Methode: Standard: without Accounts, Extended: with " "Accounts",
        default="standard",
    )
    export_xml_group_lines = fields.Boolean(
        "Group Invoice Lines",
        help="Group invoice lines that have the same account, tax, analytic "
        "account and analytic tag.",
    )
    export_xml_analytic_accounts = fields.Boolean(
        'Export Analytic Accounts',
        help='If disabled no analytic account will be exported.',
        default=True,
    )
