# © 2023 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_l10n_din5008_template_data(self):
        super()._compute_l10n_din5008_template_data()
        for record in self:
            if not record.company_id.allow_account_number_report:
                continue
            data = record.l10n_din5008_template_data
            if record.partner_id.customer_number:
                data.append((_("Customer No."), record.partner_id.customer_number))
