# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SyscoonFinanceinterfaceConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_export_finance_interface = fields.Selection(
        related="company_id.export_finance_interface", readonly=False
    )
    company_export_finance_interface_active = fields.Boolean(
        related="company_id.export_finance_interface_active", readonly=False
    )
