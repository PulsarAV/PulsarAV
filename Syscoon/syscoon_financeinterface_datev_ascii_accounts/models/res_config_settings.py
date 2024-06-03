# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EcoserviceFinanceInterfaceConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_datev_ascii_accounts_kind = fields.Selection(
        related="company_id.datev_ascii_accounts_kind", readonly=False
    )
