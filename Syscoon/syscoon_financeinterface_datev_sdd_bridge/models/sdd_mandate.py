# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class SDDMandate(models.Model):
    _inherit = 'sdd.mandate'

    def write(self, values):
        if self.partner_id:
            self.partner_id.datev_exported = 'false'
        return super().write(values)
