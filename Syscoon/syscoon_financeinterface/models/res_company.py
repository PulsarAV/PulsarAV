# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    export_finance_interface = fields.Selection(
        selection=[("none", "None")], default="none"
    )
    export_finance_interface_active = fields.Boolean()
