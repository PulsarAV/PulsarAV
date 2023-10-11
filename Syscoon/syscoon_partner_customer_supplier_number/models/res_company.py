# © 2023 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    allow_account_number_report = fields.Boolean(
        string="Allow In Reports", default=False
    )
