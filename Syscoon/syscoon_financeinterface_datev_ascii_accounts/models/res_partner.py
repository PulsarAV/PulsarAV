# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    datev_exported = fields.Selection(
        selection=[("false", "False"), ("true", "True")],
        string="Exported to DATEV",
        default="false",
        company_dependent=True,
    )

    def write(self, values):
        if not values.get('datev_exported'):
            values['datev_exported'] = 'false'
        return super().write(values)
