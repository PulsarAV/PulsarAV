# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SyscoonImportDatevConfig(models.Model):
    _name = 'syscoon.datev.import.config'
    _description = 'Configuration for the DATEV-Import'

    name = fields.Char('Name')
    import_config_row_ids = fields.Many2many(
        "syscoon.datev.import.config.rows",
        relation="syscoon_datev_import_crows",
        string="Config Rows",
    )
    delimiter = fields.Char("CSV Delimiter", default=";")
    encoding = fields.Char(default="iso-8859-1")
    locale = fields.Char(default="de_DE.utf8")
    quotechar = fields.Char(default='"')
    headerrow = fields.Integer()
    remove_datev_header = fields.Boolean(
        help="Mandatory if file is in DATEV ASCII format."
    )
    discount_account_income = fields.Many2one("account.account")
    discount_account_expenses = fields.Many2one("account.account")
    ref = fields.Char("Reference")
    ignore_incomplete_moves = fields.Boolean()
    post_moves = fields.Boolean()
    auto_reconcile = fields.Boolean()
    payment_difference_handling = fields.Selection(
        [("open", "Keep open"), ("reconcile", "Mark invoice as fully paid")]
    )


class SyscoonImportDatevConfigRows(models.Model):
    _name = 'syscoon.datev.import.config.rows'
    _description = 'DATEV Import Config Row'

    name = fields.Char('Name', help='Name of the field in CSV-file')
    import_datev_id = fields.Many2one(
        "syscoon.datev.import.config", string="Datev Config"
    )
    required = fields.Boolean(string="Required", default=False)
    assignment_type = fields.Many2one("syscoon.datev.import.assignment")
    skip = fields.Boolean(default=False)


class SyscoonImportDatevAssignmentTypes(models.Model):
    _name = 'syscoon.datev.import.assignment'
    _description = 'Assignment Type'

    name = fields.Char(translate=True)
    type = fields.Selection([
        ('amount', 'Amount'),
        ('move_sign', 'Move Sign'),
        ('account', 'Account'),
        ('counteraccount', 'Counterccount'),
        ('move_date', 'Accounting Date'),
        ('due_date', 'Due Date'),
        ('move_name', 'Move Name'),
        ('move_ref', 'Reference'),
        ('tax_key', 'Tax Key'),
        ('cost1', 'Cost-1'),
        ('cost2', 'Cost-2'),
        ('custom', 'Custom'),
        ('discount_amount', 'Discount Amount'),
        ('guid', 'GUID'),
        ('currency', 'Currency'),
        ('base_amount', 'Base Amount'),
        ('general_reversal', 'General Reversal'),
    ], default='custom', required=True)
    field_type = fields.Selection([
        ('string', 'String'),
        ('date', 'Date'),
        ('decimal', 'Decimal')
    ], required=True)
    object = fields.Char()
    field = fields.Char()
    domain = fields.Char()
    default = fields.Char()
    account_move_field = fields.Selection(
        [
            ("name", "Name"),
            ("ref", "Reference"),
            ("date", "Date"),
            ("partner_id", "Partner"),
            ("syscoon_datev_import_guid", "Move GUID"),
        ]
    )
    account_move_line_field = fields.Selection(
        [
            ("account_id", "Account"),
            ("amount", "Amount"),
            ("move_sign", "Move Sign"),
            ("name", "Label"),
            ("debit", "Debit"),
            ("credit", "Credit"),
            ("tax_ids", "Tax IDs"),
            ("analytic_distribution", "Analytic Distribution"),
            # ('analytic_account_id', 'Analytic Account'),
            # ('analytic_tag_ids', 'Analytic Tags'),
        ]
    )
    padding = fields.Integer(
        string="Sequence Size",
        default=0,
        help="Adds 0 to the left of the Value to fill up to necessary lenght",
    )
    date_format = fields.Char(string="Dateformat")
    decimal_sign = fields.Char(string="Decimalformat")
    skip_at = fields.Char()
