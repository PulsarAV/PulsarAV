# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import uuid

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """Adds the posibility to check the move line if they are compatible for
    the DATEV export"""
    _inherit = 'account.move'

    datev_checks_enabled = fields.Boolean(
        "Perform Datev Checks", compute="_compute_datev_checks_enabled", store=True
    )
    datev_ref = fields.Char('DATEV Ref', compute='_compute_datev_ref')
    datev_bedi = fields.Char('DATEV BEDI', copy=False)

    @api.depends("company_id")
    def _compute_datev_checks_enabled(self):
        for rec in self:
            rec.datev_checks_enabled = (
                rec.company_id.export_finance_interface_active
                and rec.company_id.datev_checks_enabled
            )

    def action_post(self):
        """Inherits the post method to provide the DATEV checks"""
        for move in self:
            if move.datev_checks_enabled:
                move.make_datev_checks()
            if move.move_type in [
                "out_invoice",
                "out_refund",
                "in_invoice",
                "in_refund",
            ]:
                move.write({'datev_bedi': str(uuid.uuid4())})
        return super().action_post()

    def write(self, vals):
        for rec in self:
            if vals.get('state') == 'posted':
                if rec.journal_id.type == 'purchase' and rec.ref:
                    vals['datev_ref'] = re.sub(r'[\W_]+', '', rec.ref)
                elif rec.name:
                    vals['datev_ref'] = re.sub(r'[\W_]+', '', rec.name)
        return super().write(vals)

    def make_datev_checks(self):
        """Checks the move and the move lines if the counter account is set and
        if the account_id is an automatic account in DATEV. Checks also if the
        taxes are set correctly and if a VAT-ID is required if it is set in the
        partner."""
        errors = self.line_ids._prepare_datev_errors()
        if errors:
            raise UserError('\n'.join(errors))
        return errors

    @api.depends('name', 'ref')
    def _compute_datev_ref(self):
        for move in self:
            if move.journal_id.type == 'purchase' and move.ref:
                move.datev_ref = re.sub(r'[\W_]+', '', move.ref)
            elif move.name:
                move.datev_ref = re.sub(r'[\W_]+', '', move.name)
            else:
                move.datev_ref = False

    def create_new_bedi_uuid(self):
        for rec in self:
            rec.write({"datev_bedi": str(uuid.uuid4())})


class AccountMoveLine(models.Model):
    """Adds the possibility to check the move line if they are compatible for
    the DATEV export"""

    _inherit = "account.move.line"

    def _prepare_datev_errors(self):
        errors = []
        for line in self:
            if line.display_type == "tax":
                continue
            line_name = f"{line.account_id.display_name} with Label ({line.name})"
            if len(line.tax_ids) > 1:
                errors.append(
                    _(
                        f"{line_name} has more than one tax "
                        "account, but allowed is only one."
                    )
                )
            if line.account_id.datev_automatic_account:
                if not line.account_id.datev_no_tax and not line.tax_ids:
                    errors.append(
                        _(
                            f"{line_name} has an automatic account, but "
                            "there is no tax set."
                        )
                    )
                else:
                    for tax in line.tax_ids:
                        if tax.id not in line.account_id.datev_automatic_tax.ids:
                            errors.append(
                                _(
                                    f"{line_name} has an automatic account, "
                                    f"but the tax {tax.name} is not in the "
                                    "list of the allowed taxes!"
                                )
                            )
            if (
                not line.account_id.datev_automatic_account
                and line.tax_ids
                and not line.tax_ids[  # should be related to not invoice lines
                    :1
                ].datev_tax_key
            ):
                errors.append(
                    _(
                        f"{line_name} has taxes applied, but "
                        "the tax has no DATEV Tax Key"
                    )
                )
            if line.account_id.datev_vatid_required and not line.partner_id.vat:
                errors.append(
                    _(
                        f"{line_name} needs the VAT-ID, "
                        f"but in the Partner {line.partner_id.name} it is not set"
                    )
                )
        return errors
