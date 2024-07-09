# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

import logging
import re

from lxml import etree, html
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_utils

_logger = logging.getLogger(__name__)


class SyscoonFinanceinterface(models.Model):
    """The class syscoon.financeinterface is the central object to generate
    exports for the selected moves that can be used to be imported in the
    different financial programms on different ways"""

    _name = "syscoon.financeinterface"
    _description = "syscoon Financial Interface"
    _order = "name desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, readonly=True)
    period = fields.Char("Date", required=True, readonly=True)
    account_moves_ids = fields.One2many("account.move", "export_id", readonly=True)
    mode = fields.Selection(
        selection=[("none", "None")], string="Export Mode", default="none"
    )
    log = fields.Text()
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    journal_ids = fields.Many2many("account.journal", string="Journals")

    def replace_characters(self, text, replacement=""):
        """replaces non ascii characters"""
        return re.sub(r"[^\x00-\x7F]+", replacement, text)

    def convert_line_float_to_char(self, line):
        """Converts all floats of a line to char for using in DATEV ASCII Export"""
        for key, val in line.items():
            if isinstance(val, float) and key != "Kurs":
                line[key] = str(float_utils.float_repr(val, 2)).replace(".", ",")
            if isinstance(val, float) and key == "Kurs":
                line[key] = str(float_utils.float_repr(val, 6)).replace(".", ",")
        return line

    def currency_round(self, value, currency=False):
        if not currency:
            currency = self.env.company.currency_id
        return currency.round(value)

    def compute_total_if_taxes(self, taxes_computed):
        """Compute the total include taxes"""
        total = taxes_computed["total_excluded"]
        for tax in taxes_computed["taxes"]:
            total += tax["amount"]
        return total

    def convert_date(self, date, date_format="%d%m%y"):
        """Converts the date to the needed format for the export:
        The format can be given free by using the known python formats"""
        return date.strftime(date_format)

    def copy(self, default=None):
        """Prevent the copy of the object"""
        if self._context.get("prevent_copy", True):
            raise UserError(_("Warning! Exports cannot be duplicated."))
        return super().copy(default=default)

    def pre_export(self):
        """Method to call before the Import starts and the moves to export
        are going to be browsed"""
        return True

    def export(self, mode=False, date_from=False, date_to=False, args=False):
        """Method that generates the csv export by the given parameters"""

        def dts(date_to_convert):
            if isinstance(date_to_convert, str):
                return date_to_convert
            return fields.Date.to_string(date_to_convert)
        if date_from and date_to:
            period = dts(date_from) + " - " + dts(date_to)
        elif date_from and not date_to:
            period = dts(date_from)
        else:
            period = ""
        sequence = self.env.company._check_existing_sequence()
        export = self.create(
            {
                "name": sequence.next_by_id(),
                "mode": mode,
                "period": period,
            }
        )
        return export

    def _get_report_base_filename(self):
        self.ensure_one()
        return self.name

    @api.model
    def text_from_html(
        self, html_content, max_words=None, max_chars=None, ellipsis="…", fail=False
    ):
        try:
            doc = html.fromstring(html_content)
        except (TypeError, etree.XMLSyntaxError, etree.ParserError):
            if fail:
                raise
            _logger.exception("Failure parsing this HTML:\n%s", html_content)
            return ""
        words = "".join(doc.xpath("//text()")).split()
        suffix = max_words and len(words) > max_words
        if max_words:
            words = words[:max_words]
        text = " ".join(words)
        suffix = suffix or max_chars and len(text) > max_chars
        if max_chars:
            text = text[: max_chars - (len(ellipsis) if suffix else 0)].strip()
        if suffix:
            text += ellipsis
        return text


class SyscoonFinanceinterfaceBookingtextConfig(models.Model):
    """This class provides parameters for the configuration of the creation of the bookingtext"""

    _name = "syscoon.financeinterface.bookingtext.config"
    _description = "syscoon Financial Interface Config for the Bookingtext"
    _order = "sequence asc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    sequence = fields.Integer(default=10)
    name = fields.Char(compute="_compute_name", store=True)
    journal_ids = fields.Many2many("account.journal")
    field = fields.Selection(
        [
            ("partner_id.display_name", "Partner Name"),
            ("move_id.name", "Move Name"),
            ("move_id.ref", "Move Reference"),
            ("name", "Move Line Name"),
        ],
        string="Fields",
    )

    @api.depends("field")
    def _compute_name(self):
        for rec in self:
            rec.name = dict(rec._fields["field"].selection).get(rec.field)
