# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SyscoonAccountsAutomaticMode(models.Model):
    _name = "syscoon.accounts.automatic.mode"
    _description = "syscoon Accounts Automatic Mode"

    name = fields.Char(translate=True)
    code = fields.Char()
