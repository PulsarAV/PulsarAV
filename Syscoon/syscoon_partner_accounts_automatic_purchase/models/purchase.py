# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model_create_multi
    def create(self, vals_list):
        company = self.env.company
        types = {}
        records = super().create(vals_list)
        for record in records:
            partner = record.partner_id.commercial_partner_id
            if types:
                partner.create_accounts(company, types)
        return records

    def button_confirm(self):
        company = self.env.company
        create_accounts = [auto.code for auto in company.create_auto_account_on]
        types = {}
        partner = self.partner_id.commercial_partner_id
        if "purchase_order_supplier" in create_accounts:
            types["liability_payable"] = True
        if company.use_separate_accounts:
            types["use_separate"] = True
        if types:
            partner.create_accounts(company, types)
        return super().button_confirm()
