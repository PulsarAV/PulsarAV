# © 2023 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    auto_account_creation = fields.Boolean(compute="_compute_auto_account_creation")
    # todo: fields customer_number/supplier_number will need to be deleted as they've
    # been moved to syscoon_partner_customer_supplier_number
    customer_number = fields.Char(string='Customer Number', company_dependent=True)
    debitor_number = fields.Char(string='Debitor Number', company_dependent=True)
    supplier_number = fields.Char(string='Supplier Number', company_dependent=True)
    creditor_number = fields.Char(string='Creditor Number', company_dependent=True)

    def _compute_auto_account_creation(self):
        self.auto_account_creation = self.env.company.auto_account_creation

    def create_receivable_account(self):
        company = self.env.company
        types = {
            "asset_receivable": True,
            "use_separate": bool(company.use_separate_accounts),
            "add_number": bool(company.add_number_to_partner_number),
            "customer_number": bool(company.use_separate_partner_numbers),
        }
        return self.create_accounts(company, types)

    def create_payable_account(self):
        company = self.env.company
        types = {
            "liability_payable": True,
            "use_separate": bool(company.use_separate_accounts),
            "add_number": bool(company.add_number_to_partner_number),
            "supplier_number": bool(company.use_separate_partner_numbers),
        }
        return self.create_accounts(company, types)

    def create_customer_number(self):
        company = self.env.company
        types = {"customer_number": bool(company.use_separate_partner_numbers)}
        return self.create_accounts(company, types)

    def create_supplier_number(self):
        company = self.env.company
        types = {"supplier_number": bool(company.use_separate_partner_numbers)}
        return self.create_accounts(company, types)

    def create_accounts(self, company, types=None):
        if not self.auto_account_creation:
            return {}
        account_obj = self.env['account.account']
        partner = self
        if self.parent_id:
            partner = self.parent_id
        values = self.get_accounts(company, partner, types)
        receivable_account_id = payable_account_id = False
        receivable_account_vals = values.pop("receivable_account_vals")
        payable_account_vals = values.pop("payable_account_vals")
        if receivable_account_vals:
            receivable_account_id = account_obj.sudo().create(receivable_account_vals)
            values['property_account_receivable_id'] = receivable_account_id.id
        if payable_account_vals:
            payable_account_id = account_obj.sudo().create(payable_account_vals)
            values['property_account_payable_id'] = payable_account_id.id
        partner.write(values)
        return values

    def get_accounts(self, company, partner, types=None):
        if not types:
            types = {}
        debitor_vals = self._prepare_debitor_vals(company, types)
        creditor_vals = self._prepare_creditor_vals(company, types)
        values = {**debitor_vals, **creditor_vals}
        if company.add_number_to_partner_ref and not self.ref:
            values.update(
                {
                    "ref": debitor_vals["customer_number"]
                    or creditor_vals["supplier_number"]
                }
            )
        return values

    def _prepare_debitor_vals(self, company, types):
        values = {
            "debitor_number": self.debitor_number,
            "customer_number": self.customer_number,
            "receivable_account_vals": {},
        }
        if not values["debitor_number"] and types.get("asset_receivable"):
            values["debitor_number"] = self.env["ir.sequence"].next_by_code(
                "partner.auto.receivable"
            )
            if (
                types.get("use_separate")
                and "property_account_receivable_id" in self._fields
            ):
                values["receivable_account_vals"] = self._prepare_account_vals(
                    company=company,
                    template=company.receivable_template_id,
                    code=values["debitor_number"],
                )
        if (
            values["debitor_number"]
            and not values["customer_number"]
            and types.get("add_number")
        ):
            values["customer_number"] = values["debitor_number"]
        if not values["customer_number"] and types.get("customer_number"):
            sequence = company.customer_number_sequence_id
            if sequence:
                values["customer_number"] = sequence.next_by_id()
            else:
                values["customer_number"] = self.env["ir.sequence"].next_by_code(
                    "partner.auto.customer.number"
                )
        return values

    def _prepare_creditor_vals(self, company, types):
        values = {
            "creditor_number": self.creditor_number,
            "supplier_number": self.supplier_number,
            "payable_account_vals": {},
        }
        if not values["creditor_number"] and types.get("liability_payable"):
            values["creditor_number"] = self.env["ir.sequence"].next_by_code(
                "partner.auto.payable"
            )
            if (
                types.get("use_separate")
                and "property_account_payable_id" in self._fields
            ):
                values["payable_account_vals"] = self._prepare_account_vals(
                    company=company,
                    template=company.payable_template_id,
                    code=values["creditor_number"],
                )
        if (
            values["creditor_number"]
            and not values["supplier_number"]
            and types.get("add_number")
        ):
            values["supplier_number"] = values["creditor_number"]
        if not values["supplier_number"] and types.get("supplier_number"):
            sequence = company.supplier_number_sequence_id
            if sequence:
                values["supplier_number"] = sequence.next_by_id()
            else:
                values["supplier_number"] = self.env["ir.sequence"].next_by_code(
                    "partner.auto.supplier.number"
                )
        return values

    def _prepare_account_vals(self, company, template, code):
        company = self.env.company
        return {
            "name": self.name,
            "currency_id": template.currency_id.id,
            "code": code,
            "account_type": template.account_type,
            "reconcile": template.reconcile,
            "tax_ids": [(6, 0, template.tax_ids.ids)],
            "company_id": company.id,
            "tag_ids": [(6, 0, template.tag_ids.ids)],
            "group_id": template.group_id.id,
        }
