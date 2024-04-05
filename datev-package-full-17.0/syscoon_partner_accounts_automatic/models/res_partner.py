# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, vals_list):
        """Inherit to create accounts for partners"""
        records = super().create(vals_list)
        company = self.env.company
        for res in records:
            types = res._prepare_account_types()
            if not types:
                continue
            res.create_accounts(company, types)
        return records

    def _prepare_account_types(self):
        """Prepare the account types for the partner"""
        company = self.env.company
        create_accounts = [auto.code for auto in company.create_auto_account_on]
        types = {}
        if self.commercial_partner_id.id != self.id:
            return types
        if "partner_customer" in create_accounts:
            types.update(
                {
                    "asset_receivable": True,
                }
            )
        if "partner_supplier" in create_accounts:
            types.update(
                {
                    "liability_payable": True,
                }
            )
        if "asset_receivable" in types or "liability_payable" in types:
            types["use_separate"] = bool(company.use_separate_accounts)
        return types
