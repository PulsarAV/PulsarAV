# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SyscoonAccountsAutomaticMode(models.Model):
    _name = 'syscoon.accounts.automatic.mode'
    _description = 'syscoon Accounts Automatic Mode'

    name = fields.Char('Name', translate=True)
    code = fields.Char('Code')
