# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    datev_payment_conditons_id = fields.Integer("DATEV Payment Term ID", size=2)

    @api.constrains("datev_payment_conditons_id")
    def _check_value(self):
        if self.datev_payment_conditons_id > 99 or self.datev_payment_conditons_id < 1:
            raise ValidationError(_("Only a value between 1 and 99 is allowed."))
