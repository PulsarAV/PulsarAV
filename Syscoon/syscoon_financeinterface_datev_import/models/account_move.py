# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    syscoon_datev_import_id = fields.Many2one(
        "syscoon.datev.import", "DATEV Import", readonly=True
    )
    syscoon_datev_import_guid = fields.Char("DATEV Move GUID")
