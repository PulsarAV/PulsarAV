# See LICENSE file for full copyright and licensing details.

import base64
import csv
import logging
import time
from datetime import datetime
from io import StringIO

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

ACCOUNT_TYPES = [
    "asset_receivable",
    "asset_cash",
    "asset_current",
    "asset_non_current",
    "asset_prepayments",
    "asset_fixed",
    "liability_payable",
    "liability_credit_card",
    "liability_current",
    "liability_non_current",
    "equity",
    "equity_unaffected",
    "off_balance",
]

COST_ACCOUNT_TYPES = [
    'income',
    'income_other',
    'expense',
    'expense_depreciation',
    'expense_direct_cost',
]

NO_TAX_ACCOUNT_TYPES = [
    "asset_receivable",
    "asset_cash",
    "liability_payable",
    "liability_credit_card",
    "liability_current",
    "liability_non_current",
    "equity",
    "equity_unaffected",
    "off_balance",
]


class ImportDatev(models.Model):
    """
    The class syscoon.datev.import is for the import of
    DATEV Buchungsstapel (account.moves)
    """

    _name = "syscoon.datev.import"
    _order = "name desc"
    _description = "DATEV ASCII-Import"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        "Name",
        readonly=True,
        default=lambda self: self.env["ir.sequence"].get(
            "syscoon.datev.import.sequence"
        )
        or "-",
    )
    description = fields.Char(required=True)
    template_id = fields.Many2one(
        "syscoon.datev.import.config", string="Import Template"
    )
    journal_id = fields.Many2one("account.journal", required=True)
    one_move = fields.Boolean("In one move?")
    start_date = fields.Date(required=True, default=fields.Date.today())
    end_date = fields.Date(required=True, default=fields.Date.today())
    log_line = fields.One2many("syscoon.datev.import.log", "parent_id", "Log")
    account_move_ids = fields.One2many(
        "account.move", "syscoon_datev_import_id", "Account Moves"
    )
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("error", "Error"),
            ("imported", "Imported"),
            ("booked", "Booked"),
        ],
        "Status",
        index=True,
        readonly=True,
        default="draft",
        tracking=True,
    )

    def start_import(self):
        """Initial function for manage the import of DATEV-moves"""
        # if self.account_move_ids:
        #    self.reset_import()
        self.env["syscoon.datev.import.log"].create(
            {"parent_id": self.id, "name": _("Import started"), "state": "info"}
        )
        move_values = {}
        log_error = False
        file = self.get_attachment()
        if self.get_import_config()['remove_datev_header']:
            file = self.remove_datev_header(file)
        import_list = self.convert_lines(file)
        logs = self.check_can_created(import_list)
        if logs:
            for log in logs:
                if log['state'] == 'error':
                    log_error = True
                self.env['syscoon.datev.import.log'].create({
                    'parent_id': log['parent_id'],
                    'line': log['line'],
                    'name': log['name'],
                    'state': log['state'],
                })
            if log_error:
                self.write({'state': 'error'})
        if not log_error:
            move_values = self.create_values(import_list)
        self._process_move_creation(move_values)
        self.env['syscoon.datev.import.log'].create({
            'parent_id': self.id,
            'name': _('Import done'),
            'state': 'info',
        })

    def _process_move_creation(self, move_values):
        if not move_values:
            return
        self.create_moves(move_values)
        self.write({"state": "imported"})
        if self.template_id.auto_reconcile or self.template_id.post_moves:
            self.confirm_moves()
        if self.template_id.auto_reconcile:
            if not self.template_id.discount_account_income:
                self.env["syscoon.datev.import.log"].create(
                    {
                        "parent_id": self.id,
                        "name": _("Income Discount Account not selected in Template!"),
                        "state": "error",
                    }
                )
                self.write({"state": "error"})
            elif not self.template_id.discount_account_expenses:
                self.env["syscoon.datev.import.log"].create(
                    {
                        "parent_id": self.id,
                        "name": _("Expense Discount Account not selected in Template!"),
                        "state": "error",
                    }
                )
                self.write({"state": "error"})
            else:
                self.reconcile_moves()

    def reset_import(self):
        for move in self.account_move_ids:
            move.line_ids.remove_move_reconcile()
        if self.account_move_ids:
            self.account_move_ids.unlink()
        if self.log_line:
            self.log_line.unlink()
        self.write({'state': 'draft'})

    def confirm_moves(self):
        if self.state == 'imported':
            if self.account_move_ids:
                self.account_move_ids.action_post()
                self.write({'state': 'booked'})
            self.env['syscoon.datev.import.log'].create({
                'parent_id': self.id,
                'name': _('Moves confirmed'),
                'state': 'info',
            })

    def _prepare_reconcile_lines(self, move):
        reconcile_lines = self.env["account.move"]
        for line in move.line_ids:
            if line.account_id.account_type not in [
                "liability_payable",
                "asset_receivable",
            ]:
                continue
            reconcile_lines |= line
        opposite_move = self.env["account.move"].search([("datev_ref", "=", move.ref)])
        for line in opposite_move.line_ids:
            if line.id in reconcile_lines.ids or line.account_id.account_type not in [
                "liability_payable",
                "asset_receivable",
            ]:
                continue
            reconcile_lines |= line
        return reconcile_lines

    def reconcile_moves(self):
        for move in self.account_move_ids:
            if not move.ref:
                continue
            reconcile_lines = self._prepare_reconcile_lines(move)
            if len(reconcile_lines) > 1 and not reconcile_lines.filtered(
                lambda l: l.reconciled
            ):
                reconcile_lines.reconcile()
            if reconcile_lines >= 1:
                self.env["syscoon.datev.import.log"].create(
                    {
                        "parent_id": self.id,
                        "name": _("Move %s not reconciled" % move.ref),
                        "state": "warning",
                    }
                )

    def get_attachment(self):
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'syscoon.datev.import'),
            ('res_id', '=', self.id),
        ])
        if not attachment:
            raise UserError(_('No Import File uploaded, please upload one!'))
        if len(attachment) == 1:
            file = base64.decodebytes(attachment.datas)
            file = file.decode(self.get_import_config()["encoding"])
            return file
        raise UserError(
            _(
                "There is more than one file attached to this record. "
                "Please make sure that there is only one attached CSV-file."
            )
        )

    def get_import_config(self):
        if not self.template_id:
            raise UserError(_("There is no Import Template for this company!"))
        return {
            "delimiter": str(self.template_id.delimiter),
            "encoding": self.template_id.encoding,
            "quotechar": str(self.template_id.quotechar),
            "headerrow": self.template_id.headerrow,
            "remove_datev_header": self.template_id.remove_datev_header,
            "journal_id": self.journal_id.id,
            "company_id": self.company_id.id,
            "company_currency_id": self.env.company.currency_id.id,
            "discount_account_income": self.template_id.discount_account_income,
            "discount_account_expenses": self.template_id.discount_account_expenses,
            "date": self.start_date,
            "ref": self.template_id.ref,
            "post": self.template_id.post_moves,
            "auto_reconcile": self.template_id.auto_reconcile,
            "payment_difference_handling": self.template_id.payment_difference_handling,
        }

    def get_import_struct(self):
        struct = {}
        for row in self.template_id.import_config_row_ids:
            struct[row.name] = {
                'type': row.assignment_type,
                'field_type': row.assignment_type.field_type,
                'object': row.assignment_type.object,
                'field': row.assignment_type.field,
                'domain': row.assignment_type.domain,
                'default': row.assignment_type.default,
                'account_move_field': row.assignment_type.account_move_field,
                'account_move_line_field': row.assignment_type.account_move_line_field,
                'padding': row.assignment_type.padding,
                'date_format': row.assignment_type.date_format,
                'decimal_sign': row.assignment_type.decimal_sign,
                'skip_at': row.assignment_type.skip_at,
                'required': row.required,
                'skip': row.skip,
                'import_value': False,
            }
        return struct

    def remove_datev_header(self, file):
        file = file[file.index('\n')+1:]
        return file

    def convert_lines(self, file):
        config = self.get_import_config()
        reader = csv.DictReader(
            StringIO(file),
            delimiter=config['delimiter'],
            quotechar=config['quotechar']
        )
        pre_import_list = []
        for row in reader:
            pre_import_list.append(dict(row))
        import_list = []
        struct = self.get_import_struct()
        for row in pre_import_list:
            new_row = {}
            for key, value in row.items():
                if key not in struct:
                    continue
                struct_values = struct[key].copy()
                struct_values["import_value"] = value
                new_row[key] = struct_values
            import_list.append(new_row)
        return import_list

    def check_can_created(self, vals_list):
        logs = []
        count = 1
        for values in vals_list:
            logs += self.check_required_fields(values, count)
            count += 1
        count = 1
        for values in vals_list:
            logs += self.check_values(values, count)
            count += 1
        return logs

    def check_required_fields(self, values, count):
        logs = []
        required_types = [
            "amount",
            "move_sign",
            "account",
            "counteraccount",
            "move_date",
        ]
        template_required = self.template_id.import_config_row_ids.search(
            [("required", "=", True)]
        )
        for template in template_required:
            if template.assignment_type.type not in required_types:
                required_types.append(template.assignment_type.type)
        for k, v in values.items():
            _logger.info(k, v)
            if (v["type"].type in required_types and v["import_value"]) or (
                v["type"].type == "tax_key"
                and v["type"].type in required_types
                and not v["import_value"]
            ):
                required_types.remove(v["type"].type)
        for required_type in required_types:
            field = dict(
                self.env["syscoon.datev.import.assignment"]
                ._fields["type"]
                ._description_selection(self.env)
            )[required_type]
            logs.append(
                {
                    "parent_id": self.id,
                    "line": count,
                    "name": _("Missing Required Field %s." % field),
                    "state": "error",
                }
            )
        return logs

    def check_values(self, values, count):  # noqa: C901
        logs = []
        for k, v in values.items():
            if v['field_type'] == 'decimal':
                try:
                    self.convert_to_float(v['import_value'])
                except Exception:
                    logs.append(
                        {
                            "parent_id": self.id,
                            "line": count,
                            "name": _(f"{k} cant be converted."),
                            "state": "error",
                        }
                    )
            if v["type"].type == "move_sign":
                try:
                    self.check_move_sign(v['import_value'])
                except Exception:
                    logs.append(
                        {
                            "parent_id": self.id,
                            "line": count,
                            "name": _(f"{k} does not exist. It must be S or H."),
                            "state": "error",
                        }
                    )
            if v["type"].object and v["import_value"]:
                try:
                    self.get_object(
                        v["type"].object,
                        v["type"].field,
                        v["import_value"],
                        v["padding"],
                    )
                except Exception:
                    logs.append(
                        {
                            "parent_id": self.id,
                            "line": count,
                            "name": _(f"{k} does not exist. Please Check."),
                            "state": "error",
                        }
                    )
            if v["type"].type == "account":
                partner = self.env["res.partner"]
                partner_check = False
                account_id = self.get_object(
                    v["type"].object, v["type"].field, v["import_value"], v["padding"]
                )
                if not account_id:
                    partner_debit_id = partner.search(
                        [("debitor_number", "=", v["import_value"])]
                    )
                    partner_credit_id = partner.search(
                        [("creditor_number", "=", v["import_value"])]
                    )
                    if partner_debit_id or partner_credit_id:
                        partner_check = True
                    if not partner_check:
                        logs.append(
                            {
                                "parent_id": self.id,
                                "line": count,
                                "name": _(
                                    f"{v['import_value']} does not exist. Please Check."
                                ),
                                "state": "error",
                            }
                        )
            if v["type"].type == "counteraccount":
                partner = self.env["res.partner"]
                partner_check = False
                account_id = self.get_object(
                    v["type"].object, v["type"].field, v["import_value"], v["padding"]
                )
                if not account_id:
                    partner_debit_id = partner.search(
                        [("debitor_number", "=", v["import_value"])]
                    )
                    partner_credit_id = partner.search(
                        [("creditor_number", "=", v["import_value"])]
                    )
                    if partner_debit_id or partner_credit_id:
                        partner_check = True
                    if not partner_check:
                        logs.append(
                            {
                                "parent_id": self.id,
                                "line": count,
                                "name": _(
                                    f"{v['import_value']} does not exist. Please Check."
                                ),
                                "state": "error",
                            }
                        )
            if v["type"].type == "move_date":
                try:
                    datetime.strptime(v["import_value"], v["date_format"])
                except Exception:
                    logs.append(
                        {
                            "parent_id": self.id,
                            "line": count,
                            "name": _(
                                f"{k} does not fit to {v['date_format']}. Please Check."
                            ),
                            "state": "error",
                        }
                    )
            if v["type"].type == "guid":
                created_guid = self.env["account.move"].search(
                    [("syscoon_datev_import_guid", "=", v["import_value"])]
                )
                if created_guid:
                    logs.append(
                        {
                            "parent_id": self.id,
                            "line": count,
                            "name": _(
                                f"{k} with GUID {v['import_value']} already exist and "
                                "can not be imported"
                            ),
                            "state": "warning",
                        }
                    )
        return logs

    def convert_to_float(self, value):
        if value == '':
            return True
        value = value.replace(".", "")
        value = value.replace(",", ".")
        return float(value)

    def check_move_sign(self, value):
        if value.lower() in ['s', 'h']:
            return value.lower()
        return False

    def get_date(self, dt_format, value):
        move_date = datetime.strptime(value, dt_format)
        if "%y" not in dt_format or "%Y" not in dt_format:
            move_date = move_date.replace(year=self.end_date.year)
        return move_date

    def get_object(self, model_obj, field, value, padding):
        return_object = False
        if model_obj == "account.tax":
            taxes = self.env[model_obj].search(
                [(field, "=", value), ("company_id", "=", self.company_id.id)]
            )
            for tax in taxes:
                if tax.price_include:
                    return_object = tax
        elif model_obj == "account.account":
            if padding:
                return_object = self.env[model_obj].search(
                    [
                        (field, "=", value.zfill(padding)),
                        ("company_id", "=", self.company_id.id),
                    ]
                )
            else:
                return_object = self.env[object].search(
                    [(field, "=", value), ("company_id", "=", self.company_id.id)]
                )
        elif padding:
            return_object = self.env[object].search(
                [(field, "=", value.zfill(padding))]
            )
        else:
            return_object = self.env[object].search([(field, "=", value)])
        return return_object

    def _prepare_default_move_values(self):
        move = {
            "ref": False,
            "date": False,
            "journal_id": self.journal_id.id,
            "line_ids": [(0, 0, [])],
            "move_type": "entry",
            "syscoon_datev_import_id": self.id,
        }
        debit_move_line = {
            "account_id": False,
            "partner_id": False,
            "name": False,
            "analytic_distribution": False,
            "tax_ids": [(6, 0, [])],
            "tax_line_id": False,
            "debit": 0.0,
            "credit": 0.0,
            "tax_tag_ids": False,
        }
        credit_move_line = {
            "account_id": False,
            "partner_id": False,
            "name": False,
            "analytic_distribution": False,
            "tax_ids": [(6, 0, [])],
            "tax_line_id": False,
            "debit": 0.0,
            "credit": 0.0,
            "tax_tag_ids": False,
        }
        discount_move_line = {
            "account_id": False,
            "partner_id": False,
            "name": False,
            "analytic_distribution": False,
            "tax_ids": [(6, 0, [])],
            "tax_line_id": False,
            "debit": 0.0,
            "credit": 0.0,
            "tax_tag_ids": False,
        }
        return {
            "move": move,
            "debit_move_line": debit_move_line,
            "credit_move_line": credit_move_line,
            "discount_move_line": discount_move_line,
        }

    def create_values(self, vals_list):  # noqa: C901
        moves = []
        partner = self.env["res.partner"]

        for values in vals_list:
            for _k, v in values.items():
                if v["type"].type == "move_sign":
                    sign = self.check_move_sign(v["import_value"])
            default_values = self._prepare_default_move_values()
            move = default_values["move"]
            debit_move_line = default_values["debit_move_line"]
            credit_move_line = default_values["credit_move_line"]
            discount_move_line = default_values["discount_move_line"]

            has_currency = False
            taxes = False
            tax_id = False
            tax_direction = False
            opposite_move = False

            for _k, v in values.items():
                if v["type"].type == "currency" and v["import_value"]:
                    has_currency = True
                if v["type"].type == "move_date":
                    move["date"] = self.get_date(v["date_format"], v["import_value"])
                if v["type"].type == "move_name":
                    move["ref"] = v["import_value"]
                if v["type"].type == "move_ref":
                    debit_move_line["name"] = v["import_value"]
                    credit_move_line["name"] = v["import_value"]
                if v["type"].type == "guid":
                    move["syscoon_datev_import_guid"] = v["import_value"]

            for _k, v in values.items():
                if has_currency:
                    if v["type"].type == "base_amount":
                        amount_value = self.convert_to_float(v["import_value"])
                        if sign == "s":
                            debit_move_line["debit"] = amount_value
                            credit_move_line["credit"] = amount_value
                        if sign == "h":
                            debit_move_line["credit"] = amount_value
                            credit_move_line["debit"] = amount_value
                else:
                    if v["type"].type == "amount":
                        amount_value = self.convert_to_float(v["import_value"])
                        if sign == "s":
                            debit_move_line["debit"] = amount_value
                            credit_move_line["credit"] = amount_value
                        if sign == "h":
                            debit_move_line["credit"] = amount_value
                            credit_move_line["debit"] = amount_value

            for _k, v in values.items():
                if v["type"].type == "account":
                    debit_move_line["account_id"] = self.get_object(
                        v["type"].object,
                        v["type"].field,
                        v["import_value"],
                        v["padding"],
                    )
                    if (
                        debit_move_line["account_id"]
                        and debit_move_line["account_id"].account_type
                        in COST_ACCOUNT_TYPES
                    ):
                        tax_direction = "debit_move_line"
                    if debit_move_line["account_id"].datev_automatic_tax:
                        tax_ids = debit_move_line["account_id"].datev_automatic_tax
                        for tax in tax_ids:
                            if tax.price_include:
                                tax_id = tax
                        if (
                            debit_move_line["account_id"].datev_vatid_required
                            and len(tax_ids) == 1
                        ):
                            tax_id = tax_ids[0]
                    if not debit_move_line["account_id"]:
                        partner_debit_id = partner.search(
                            [("debitor_number", "=", v["import_value"])]
                        )
                        partner_credit_id = partner.search(
                            [("creditor_number", "=", v["import_value"])]
                        )
                        if partner_debit_id:
                            debit_move_line[
                                "account_id"
                            ] = partner_debit_id.property_account_receivable_id
                            debit_move_line["partner_id"] = partner_debit_id.id
                            credit_move_line["partner_id"] = partner_debit_id.id
                        if partner_credit_id:
                            debit_move_line[
                                "account_id"
                            ] = partner_credit_id.property_account_payable_id
                            debit_move_line["partner_id"] = partner_credit_id.id
                            credit_move_line["partner_id"] = partner_credit_id.id
                if v["type"].type == "counteraccount":
                    credit_move_line["account_id"] = self.get_object(
                        v["type"].object,
                        v["type"].field,
                        v["import_value"],
                        v["padding"],
                    )
                    if (
                        credit_move_line["account_id"]
                        and credit_move_line["account_id"].account_type
                        in COST_ACCOUNT_TYPES
                    ):
                        tax_direction = 'credit_move_line'
                    if credit_move_line["account_id"].datev_automatic_tax:
                        tax_direction = "credit_move_line"
                        tax_ids = credit_move_line["account_id"].datev_automatic_tax
                        for tax in tax_ids:
                            if tax.price_include:
                                tax_id = tax
                        if (
                            credit_move_line["account_id"].datev_vatid_required
                            and len(tax_ids) == 1
                        ):
                            tax_id = tax_ids[0]
                    if not credit_move_line["account_id"]:
                        partner_debit_id = partner.search(
                            [("debitor_number", "=", v["import_value"])]
                        )
                        partner_credit_id = partner.search(
                            [("creditor_number", "=", v["import_value"])]
                        )
                        if len(partner_credit_id) > 1:
                            raise UserError(
                                _(
                                    "There are multiple partners with same creditor "
                                    "number %s.",
                                    v["import_value"],
                                )
                            )
                        if partner_credit_id:
                            credit_move_line[
                                "account_id"
                            ] = partner_credit_id.property_account_payable_id
                            credit_move_line["partner_id"] = partner_credit_id.id
                            debit_move_line["partner_id"] = partner_credit_id.id
                        if len(partner_debit_id) > 1:
                            raise UserError(
                                _(
                                    "There are multiple partners with same "
                                    "debitor number %s.",
                                    v["import_value"],
                                )
                            )
                        if partner_debit_id:
                            credit_move_line[
                                "account_id"
                            ] = partner_debit_id.property_account_receivable_id
                            credit_move_line["partner_id"] = partner_debit_id.id
                            debit_move_line["partner_id"] = partner_debit_id.id
                    if tax_id and not tax_direction:
                        tax_direction = "credit_move_line"

            for _k, v in values.items():
                if v["type"].type == "tax_key" and v["import_value"]:
                    if v["import_value"] != "40":
                        tax_id = self.get_object(
                            v["type"].object,
                            v["type"].field,
                            v["import_value"],
                            v["padding"],
                        )
                    else:
                        if (
                            debit_move_line["account_id"]
                            and tax_direction in ("debit_move_line", "credit_move_line")
                            and debit_move_line["account_id"].datev_automatic_tax
                            and debit_move_line["account_id"].datev_no_tax
                        ):
                            tax_id = False

                elif v["type"].type == "tax_key" and not v["import_value"]:
                    if (
                        debit_move_line["account_id"]
                        and tax_direction == "debit_move_line"
                    ) and (
                        debit_move_line["account_id"].datev_automatic_tax
                        and debit_move_line["account_id"].datev_automatic_tax
                        and not debit_move_line["account_id"].datev_no_tax
                    ):
                        tax_id = debit_move_line[
                            "account_id"
                        ].datev_automatic_tax.filtered(
                            lambda x: x.price_include is True
                        )
                    if (
                        credit_move_line["account_id"]
                        and tax_direction == "credit_move_line"
                    ) and (
                        credit_move_line["account_id"].datev_automatic_tax
                        and credit_move_line["account_id"].datev_automatic_tax
                        and not credit_move_line["account_id"].datev_no_tax
                    ):
                        tax_id = credit_move_line[
                            "account_id"
                        ].datev_automatic_tax.filtered(
                            lambda x: x.price_include is True
                        )

                if v["type"].type == "cost1" and v["import_value"]:
                    if debit_move_line["account_id"].account_type in COST_ACCOUNT_TYPES:
                        analytic_account_id = self.get_object(
                            v["type"].object,
                            v["type"].field,
                            v["import_value"],
                            v["padding"],
                        ).id
                        debit_move_line["analytic_distribution"] = {
                            analytic_account_id: 100
                        }
                    if (
                        credit_move_line["account_id"].account_type
                        in COST_ACCOUNT_TYPES
                    ):
                        analytic_account_id = self.get_object(
                            v["type"].object,
                            v["type"].field,
                            v["import_value"],
                            v["padding"],
                        ).id
                        debit_move_line["analytic_distribution"] = {
                            analytic_account_id: 100
                        }
                if v["type"].type == "cost2" and v["import_value"]:
                    if debit_move_line["account_id"].account_type in COST_ACCOUNT_TYPES:
                        analytic_account_id = self.get_object(
                            v["type"].object,
                            v["type"].field,
                            v["import_value"],
                            v["padding"],
                        ).id
                        debit_move_line["analytic_distribution"] = {
                            analytic_account_id: 100
                        }
                    if (
                        credit_move_line["account_id"].account_type
                        in COST_ACCOUNT_TYPES
                    ):
                        analytic_account_id = self.get_object(
                            v["type"].object,
                            v["type"].field,
                            v["import_value"],
                            v["padding"],
                        ).id
                        debit_move_line["analytic_distribution"] = {
                            analytic_account_id: 100
                        }

            account_with_tax = any(
                (
                    credit_move_line["account_id"].account_type
                    not in NO_TAX_ACCOUNT_TYPES,
                    debit_move_line["account_id"].account_type
                    not in NO_TAX_ACCOUNT_TYPES,
                )
            )
            if tax_id and account_with_tax:
                if (
                    debit_move_line["account_id"].account_type
                    not in NO_TAX_ACCOUNT_TYPES
                ):
                    tax_direction = "debit_move_line"
                if (
                    credit_move_line["account_id"].account_type
                    not in NO_TAX_ACCOUNT_TYPES
                ):
                    tax_direction = "credit_move_line"

                if not tax_direction:
                    if (
                        debit_move_line["account_id"].account_type
                        not in NO_TAX_ACCOUNT_TYPES
                    ):
                        tax_direction = "debit_move_line"
                    if (
                        credit_move_line["account_id"].account_type
                        not in NO_TAX_ACCOUNT_TYPES
                    ):
                        tax_direction = "credit_move_line"
                if (
                    debit_move_line["account_id"].account_type
                    not in NO_TAX_ACCOUNT_TYPES
                    and tax_direction == "debit_move_line"
                ):
                    if debit_move_line["debit"]:
                        taxes = tax_id.compute_all(debit_move_line["debit"])
                        debit_move_line["debit"] = taxes["total_excluded"]
                    if debit_move_line["credit"]:
                        taxes = tax_id.compute_all(debit_move_line["credit"])
                        debit_move_line["credit"] = taxes["total_excluded"]
                    debit_move_line["tax_ids"] = [(6, 0, tax_id.ids)]
                    debit_move_line["tax_tag_ids"] = [(6, 0, taxes["base_tags"])]
                if (
                        credit_move_line["account_id"].account_type
                        in COST_ACCOUNT_TYPES
                        and tax_direction == "credit_move_line"
                ):
                    if credit_move_line["debit"]:
                        taxes = tax_id.compute_all(credit_move_line["debit"])
                        credit_move_line["debit"] = taxes["total_excluded"]
                    if credit_move_line["credit"]:
                        taxes = tax_id.compute_all(credit_move_line["credit"])
                        credit_move_line["credit"] = taxes["total_excluded"]
                    credit_move_line["tax_ids"] = [(6, 0, tax_id.ids)]
                    credit_move_line["tax_tag_ids"] = [(6, 0, taxes["base_tags"])]

            for _k, v in values.items():
                if v["type"].type == "discount_amount" and v["import_value"]:
                    discount_move_line["name"] = _("Discount")
                    amount = self.convert_to_float(v["import_value"])
                    if move["ref"] != "0" or move["ref"] is not False:
                        opposite_move = self.env["account.move"].search(
                            [("datev_ref", "=", move["ref"])]
                        )
                    if opposite_move:
                        for line in opposite_move.line_ids:
                            if (
                                line.account_id.account_type in COST_ACCOUNT_TYPES
                                and line.tax_ids
                            ):
                                tax_id = line.tax_ids[0].with_context(
                                    force_price_include=True
                                )
                    if tax_id and tax_id.datev_discount_account:
                        for tax in tax_id.datev_discount_account.datev_automatic_tax:
                            if tax.price_include:
                                tax_id = tax
                    taxes = tax_id.compute_all(amount)
                    discount_move_line["account_id"] = tax_id.datev_discount_account.id
                    if debit_move_line["account_id"].user_type_id.type in [
                        "receivable",
                        "payable",
                    ]:
                        if debit_move_line["credit"]:
                            discount_move_line["debit"] = taxes["total_excluded"]
                            debit_move_line["credit"] += amount
                        if debit_move_line["debit"]:
                            discount_move_line["credit"] = taxes["total_excluded"]
                            debit_move_line["debit"] += amount
                    if credit_move_line["account_id"].user_type_id.type in [
                        "receivable",
                        "payable",
                    ]:
                        if credit_move_line["credit"]:
                            discount_move_line["debit"] = taxes["total_excluded"]
                            credit_move_line["credit"] += amount
                        if credit_move_line["debit"]:
                            discount_move_line["credit"] = taxes["total_excluded"]
                            credit_move_line["debit"] += amount
                    discount_move_line["tax_ids"] = [(6, 0, tax_id.ids)]
                    discount_move_line["tax_tag_ids"] = [(6, 0, taxes["base_tags"])]

            if not isinstance(debit_move_line["account_id"], int):
                debit_move_line["account_id"] = debit_move_line["account_id"].id
            if not isinstance(credit_move_line["account_id"], int):
                credit_move_line["account_id"] = credit_move_line["account_id"].id
            move["line_ids"] = [(0, 0, debit_move_line), (0, 0, credit_move_line)]

            if discount_move_line["name"]:
                move["line_ids"].append((0, 0, discount_move_line))

            if taxes:
                for tax in taxes["taxes"]:
                    if not tax["account_id"]:
                        continue
                    tax_move_line = {
                        "account_id": tax["account_id"],
                        "name": tax["name"],
                        "tax_base_amount": tax["base"],
                        "tax_tag_ids": [(6, 0, tax["tag_ids"])],
                        "tax_line_id": tax["id"],
                        "tax_group_id": tax_id.tax_group_id.id,
                        "tax_repartition_line_id": tax["tax_repartition_line_id"],
                    }

                    partner_debit_id = partner.search(
                        [
                            ("debitor_number", "!=", False),
                            ("debitor_number", "=", v["import_value"]),
                        ],
                        limit=1,
                    )
                    partner_credit_id = partner.search(
                        [
                            ("debitor_number", "!=", False),
                            ("creditor_number", "=", v["import_value"]),
                        ],
                        limit=1,
                    )

                    if partner_credit_id:
                        tax_move_line["partner_id"] = partner_credit_id.id
                    if partner_debit_id:
                        tax_move_line["partner_id"] = partner_debit_id.id
                    if debit_move_line["tax_tag_ids"]:
                        if debit_move_line["debit"]:
                            if tax["amount"] < 0.0:
                                tax_move_line["credit"] = -tax["amount"]
                            else:
                                tax_move_line["debit"] = tax["amount"]
                        if debit_move_line["credit"]:
                            if tax["amount"] < 0.0:
                                tax_move_line["debit"] = -tax["amount"]
                            else:
                                tax_move_line["credit"] = tax["amount"]
                    if credit_move_line["tax_tag_ids"]:
                        if credit_move_line["debit"]:
                            if tax["amount"] < 0.0:
                                tax_move_line["credit"] = -tax["amount"]
                            else:
                                tax_move_line["debit"] = tax["amount"]
                        if credit_move_line["credit"]:
                            if tax["amount"] < 0.0:
                                tax_move_line["debit"] = -tax["amount"]
                            else:
                                tax_move_line["credit"] = tax["amount"]
                    if discount_move_line["tax_tag_ids"]:
                        if discount_move_line["debit"]:
                            if tax["amount"] < 0.0:
                                tax_move_line["credit"] = -tax["amount"]
                            else:
                                tax_move_line["debit"] = tax["amount"]
                        if discount_move_line["credit"]:
                            if tax["amount"] < 0.0:
                                tax_move_line["debit"] = -tax["amount"]
                            else:
                                tax_move_line["credit"] = tax["amount"]
                    move["line_ids"].append((0, 0, tax_move_line))
            for ml in move["line_ids"]:
                line_vals = ml[2] if len(ml) == 3 else {}
                remove = False
                if (
                    not line_vals.get("account_id")
                    and self.template_id.ignore_incomplete_moves
                ):
                    remove = True
                    self.env["syscoon.datev.import.log"].create(
                        {
                            "parent_id": self.id,
                            "name": _("Move %s not imported" % move["ref"]),
                            "state": "warning",
                        }
                    )
            existing_guid = False
            if move.get("syscoon_datev_import_guid"):
                existing_guid = self.env["account.move"].search(
                    [
                        (
                            "syscoon_datev_import_guid",
                            "=",
                            move["syscoon_datev_import_guid"],
                        )
                    ]
                )
            if not remove and not existing_guid:
                moves.append(move)
        return moves

    def create_moves(self, moves):
        move_obj = self.env["account.move"].with_context(
            default_journal_id=self.journal_id.id
        )
        move_ids = move_obj.sudo().create(moves)
        for mv in move_ids:
            self.env["syscoon.datev.import.log"].create(
                {
                    "parent_id": self.id,
                    "name": _("Move %s imported" % mv["ref"]),
                    "state": "info",
                }
            )
        return move_ids


class ImportDatevLog(models.Model):
    """
    Log line object for import
    """

    _name = "syscoon.datev.import.log"
    _order = "id desc"
    _description = "Object for loggin the import"

    name = fields.Text()
    line = fields.Char()
    parent_id = fields.Many2one("syscoon.datev.import", "Import")
    date = fields.Datetime(
        "Time", readonly=True, default=lambda *a: time.strftime("%Y-%m-%d %H:%M:%S")
    )
    state = fields.Selection(
        [
            ("info", "Info"),
            ("error", "Error"),
            ("standard", "Ok"),
            ("warning", "Warning"),
        ],
        "State",
        index=True,
        readonly=True,
        default="info",
    )
