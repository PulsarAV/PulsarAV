# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        company = self.env.company
        for res in records:
            types = res._prepare_account_types()
            if not types:
                continue
            res.create_accounts(company, types)
        return records

    def _prepare_account_types(self):
        company = self.env.company
        create_accounts = [auto.code for auto in company.create_auto_account_on]
        types = {}
        if self.commercial_partner_id.id != self.id:
            return types
        if "partner_customer" in create_accounts:
            types.update(
                {
                    "asset_receivable": True,
                    "customer_number": bool(
                        company.use_separate_partner_numbers
                        and "partner_customer_numbers" in create_accounts
                    ),
                }
            )
        if "partner_supplier" in create_accounts:
            types.update(
                {
                    "liability_payable": True,
                    "supplier_number": bool(
                        company.use_separate_partner_numbers
                        and "partner_supplier_numbers" in create_accounts
                    ),
                }
            )
        if "asset_receivable" in types or "liability_payable" in types:
            types["use_separate"] = bool(company.use_separate_accounts)
            types["add_number"] = bool(company.add_number_to_partner_number)
        return types
