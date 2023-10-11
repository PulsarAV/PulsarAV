# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    datev_exported = fields.Boolean('Exported')
    datev_diverse_account = fields.Boolean('Diverse Account')

    # todo: why ??
    def write(self, vals):
        res = super().write(vals)
        if 'datev_exported' not in vals:
            vals['datev_exported'] = False
        return res
