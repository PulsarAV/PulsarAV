# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    create_auto_account_on = fields.Many2many(
        "syscoon.accounts.automatic.mode",
        help="Select where the Accounts should be created. If on creating an invoice "
        "no account exists, it will created it then.",
    )
