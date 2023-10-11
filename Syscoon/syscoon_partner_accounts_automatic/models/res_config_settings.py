# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    create_auto_account_on = fields.Many2many(
        "syscoon.accounts.automatic.mode",
        related="company_id.create_auto_account_on",
        readonly=False,
        help="Select where the Accounts should be created. Please notice, "
        "without a selection no accounts will be created automatically.",
    )
