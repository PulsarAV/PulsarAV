# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    datev_ascii_group_moves = fields.Boolean('Group Moves in DATEV ASCII Export')
    export_finance_interface_active = fields.Boolean(
        related="company_id.export_finance_interface_active"
    )
