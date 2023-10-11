# © 2023 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_account_number_report = fields.Boolean(
        related="company_id.allow_account_number_report", readonly=False
    )
