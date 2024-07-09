# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import api, models

ALLOWED_MOVE_TYPES = ["in_invoice", "out_invoice", "in_refund", "out_refund"]


class AccountMove(models.Model):
    _inherit = "account.move"

    # todo: vals in onchange ?? needs to be checked
    @api.onchange("partner_id", "journal_id")
    def _check_account_created(self, vals=False):
        if not vals:
            vals = {}
        partner_obj = self.env["res.partner"]
        partner_id = (
            self.partner_id or partner_obj.browse(vals.get("partner_id")).exists()
        )
        journal_type = self.journal_id.type
        if not partner_id or self.journal_id.type not in ("sale", "purchase"):
            return
        types = {}
        partner = partner_id.commercial_partner_id
        default_account_id = self._get_partner_default_account_id(
            partner, journal_type=journal_type
        )
        types = self._prepare_account_types(journal_type=journal_type)
        company = self.company_id or self.env.company
        accounts = partner.create_accounts(company, types)
        if not accounts:
            return
        for line in self.line_ids:
            if line.account_id.id != int(default_account_id):
                continue
            if journal_type == "sale" and accounts.get(
                "property_account_receivable_id"
            ):
                line.account_id = accounts["property_account_receivable_id"].id
            if journal_type == "purchase" and accounts.get(
                "property_account_payable_id"
            ):
                line.account_id = accounts["property_account_payable_id"].id

    def write(self, vals):
        if vals.get("partner_id"):
            self._check_account_created(vals)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        partner_obj = self.env["res.partner"]
        for val in vals_list:
            if not val.get("partner_id"):
                continue
            partner = partner_obj.browse(val["partner_id"]).commercial_partner_id
            if val.get("move_type") not in ALLOWED_MOVE_TYPES or not partner:
                continue
            default_account_id = self._get_partner_default_account_id(
                partner, move_type=val["move_type"]
            )
            types = self._prepare_account_types(move_type=val["move_type"])
            if val.get("company_id"):
                company = self.env["res.company"].browse(val["company_id"])
            else:
                company = self.env.company
            accounts = partner.create_accounts(company, types)
            if not accounts:
                continue
            for _0, _1, line_vals in val.get("line_ids", []):
                if line_vals.get("account_id") != default_account_id.id:
                    continue
                if val["move_type"] in ["out_invoice", "out_refund"] and accounts.get(
                    "property_account_receivable_id"
                ):
                    account_receivable_id = accounts["property_account_receivable_id"]
                    line_vals["account_id"] = account_receivable_id.id
                if val["move_type"] in ["in_invoice", "in_refund"] and accounts.get(
                    "property_account_payable_id"
                ):
                    line_vals["account_id"] = accounts["property_account_payable_id"].id
        return super().create(vals_list)

    def _get_partner_default_account_id(
        self, partner, move_type=None, journal_type=None
    ):
        if move_type in ["out_invoice", "out_refund"] or journal_type in ("sale",):
            default_account_id = partner.property_account_receivable_id
        else:
            default_account_id = partner.property_account_payable_id
        return default_account_id

    def _prepare_account_types(self, move_type=None, journal_type=None):
        company = self.env.company
        create_accounts = [auto.code for auto in company.create_auto_account_on]
        types = {}
        if (
            move_type in ["out_invoice", "out_refund"] or journal_type in ("sale",)
        ) and "invoice_customer" in create_accounts:
            types.update(
                {
                    "asset_receivable": True,
                }
            )
        elif (
            move_type in ["in_invoice", "in_refund"] or journal_type in ("purchase",)
        ) and "invoice_supplier" in create_accounts:
            types.update(
                {
                    "liability_payable": True,
                }
            )
        if "asset_receivable" in types or "liability_payable" in types:
            types["use_separate"] = bool(company.use_separate_accounts)
        return types
