# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

import base64
import csv
import logging
import re
from io import StringIO

import dateutil.relativedelta
from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_repr
from pytz import timezone

_logger = logging.getLogger(__name__)


HEADER_TEMPLATE = {
    "Kennzeichen": "EXTF",
    "Versionsnummer": "",
    "Formatkategorie": "21",
    "Formatname": "Buchungsstapel",
    "Formatversion": "4",
    "Erzeugtam": "",
    "Reserviert1": "",
    "Reserviert2": "",
    "Reserviert3": "",
    "Reserviert4": "",
    "Beraternummer": "",
    "Mandantennummer": "",
    "WJ-Beginn": "",
    "Sachkontenlänge": "",
    "Datum von": "",
    "Datum bis": "",
    "Bezeichnung": "Odoo-Export Buchungen",
    "Diktatkürzel": "",
    "Buchungstyp": "1",
    "Rechnungslegungszweck": "0",
    "Festschreibung": "",
    "WKZ": "EUR",
    "Reserviert5": "",
    "Derivatskennzeichen": "",
    "Reserviert6": "",
    "Reserviert7": "",
    "Sachkontenrahmen": "",
    "ID der Branchenlösung": "",
    "Reserviert8": "",
    "Reserviert9": "",
    "Anwendungsinformationen": "",
}

EXPORT_TEMPLATE = {
    "Umsatz (ohne Soll/Haben-Kz)": "",
    "Soll/Haben-Kennzeichen": "",
    "WKZ Umsatz": "",
    "Kurs": "",
    "Basis-Umsatz": "",
    "WKZ Basis-Umsatz": "",
    "Konto": "",
    "Gegenkonto (ohne BU-Schlüssel)": "",
    "BU-Schlüssel": "",
    "Belegdatum": "",
    "Belegfeld 1": "",
    "Belegfeld 2": "",
    "Skonto": "",
    "Buchungstext": "",
    "Postensperre": "",
    "Diverse Adressnummer": "",
    "Geschäftspartnerbank": "",
    "Sachverhalt": "",
    "Zinssperre": "",
    "Beleglink": "",
    "Beleginfo - Art 1": "",
    "Beleginfo - Inhalt 1": "",
    "Beleginfo - Art 2": "",
    "Beleginfo - Inhalt 2": "",
    "Beleginfo - Art 3": "",
    "Beleginfo - Inhalt 3": "",
    "Beleginfo - Art 4": "",
    "Beleginfo - Inhalt 4": "",
    "Beleginfo - Art 5": "",
    "Beleginfo - Inhalt 5": "",
    "Beleginfo - Art 6": "",
    "Beleginfo - Inhalt 6": "",
    "Beleginfo - Art 7": "",
    "Beleginfo - Inhalt 7": "",
    "Beleginfo - Art 8": "",
    "Beleginfo - Inhalt 8": "",
    "KOST1 - Kostenstelle": "",
    "KOST2 - Kostenstelle": "",
    "Kost-Menge": "",
    "EU-Land u. UStID (Bestimmung)": "",
    "EU-Steuersatz (Bestimmung)": "",
    "Abw. Versteuerungsart": "",
    "Sachverhalt L+L": "",
    "Funktionsergänzung L+L": "",
    "BU 49 Hauptfunktionstype": "",
    "BU 49 Hauptfunktionsnummer": "",
    "BU 49 Funktionsergänzung": "",
    "Zusatzinformation - Art 1": "",
    "Zusatzinformation- Inhalt 1": "",
    "Zusatzinformation - Art 2": "",
    "Zusatzinformation- Inhalt 2": "",
    "Zusatzinformation - Art 3": "",
    "Zusatzinformation- Inhalt 3": "",
    "Zusatzinformation - Art 4": "",
    "Zusatzinformation- Inhalt 4": "",
    "Zusatzinformation - Art 5": "",
    "Zusatzinformation- Inhalt 5": "",
    "Zusatzinformation - Art 6": "",
    "Zusatzinformation- Inhalt 6": "",
    "Zusatzinformation - Art 7": "",
    "Zusatzinformation- Inhalt 7": "",
    "Zusatzinformation - Art 8": "",
    "Zusatzinformation- Inhalt 8": "",
    "Zusatzinformation - Art 9": "",
    "Zusatzinformation- Inhalt 9": "",
    "Zusatzinformation - Art 10": "",
    "Zusatzinformation- Inhalt 10": "",
    "Zusatzinformation - Art 11": "",
    "Zusatzinformation- Inhalt 11": "",
    "Zusatzinformation - Art 12": "",
    "Zusatzinformation- Inhalt 12": "",
    "Zusatzinformation - Art 13": "",
    "Zusatzinformation- Inhalt 13": "",
    "Zusatzinformation - Art 14": "",
    "Zusatzinformation- Inhalt 14": "",
    "Zusatzinformation - Art 15": "",
    "Zusatzinformation- Inhalt 15": "",
    "Zusatzinformation - Art 16": "",
    "Zusatzinformation- Inhalt 16": "",
    "Zusatzinformation - Art 17": "",
    "Zusatzinformation- Inhalt 17": "",
    "Zusatzinformation - Art 18": "",
    "Zusatzinformation- Inhalt 18": "",
    "Zusatzinformation - Art 19": "",
    "Zusatzinformation- Inhalt 19": "",
    "Zusatzinformation - Art 20": "",
    "usatzinformation- Inhalt 20": "",
    "Stück": "",
    "Gewicht": "",
    "Zahlweise": "",
    "Forderungsart": "",
    "Veranlagungsjahr": "",
    "Zugeordnete Fälligkeit": "",
    "Skontotyp": "",
    "Auftragsnummer": "",
    "Buchungstyp": "",
    "USt-Schlüssel (Anzahlungen)": "",
    "EU-Land (Anzahlungen)": "",
    "Sachverhalt L+L (Anzahlungen)": "",
    "EU-Steuersatz (Anzahlungen)": "",
    "Erlöskonto (Anzahlungen)": "",
    "Herkunft-Kz": "",
    "Buchungs GUID": "",
    "KOST-Datum": "",
    "SEPA-Mandatsreferenz": "",
    "Skontosperre": "",
    "Gesellschaftername": "",
    "Beteiligtennummer": "",
    "Identifikationsnummer": "",
    "Zeichnernummer": "",
    "Postensperre bis": "",
    "Bezeichnung SoBil-Sachverhalt": "",
    "Kennzeichen SoBil-Buchung": "",
    "Festschreibung": "",
    "Leistungsdatum": "",
    "Datum Zuord. Steuerperiode": "",
    "Fälligkeit": "",
    "Generalumkehr (GU)": "",
    "Steuersatz": "",
    "Land": "",
    "Abrechnungsreferenz": "",
    "BVV-Position": "",
    "EU-Land u. UStID (Ursprung)": "",
    "EU-Steuersatz (Ursprung)": "",
}


class SyscoonFinanceinterface(models.Model):
    """Inherits the basic class to provide the export for DATEV ASCII"""

    _inherit = "syscoon.financeinterface"

    mode = fields.Selection(
        selection_add=[("datev_ascii", "DATEV ASCII")],
        ondelete={"datev_ascii": lambda recs: recs.write({"mode": "none"})},
    )

    def export(self, mode=False, date_from=False, date_to=False, args=False):
        """Method that generates the csv export by the given parameters"""
        csv_file = False
        export_id = super().export(mode, date_from, date_to, args)
        if mode != "datev_ascii":
            return export_id
        journal_ids = args[0]
        export_id.write({"journal_ids": journal_ids})
        moves = self.env["account.move"].search(
            [
                ("date", ">=", date_from),
                ("date", "<=", date_to),
                ("journal_id", "in", journal_ids),
                ("export_id", "=", False),
                ("state", "=", "posted"),
            ]
        )
        if not moves:
            raise UserError(
                _(
                    "There are no moves to export in the selected date "
                    "range and journals!"
                )
            )
        export_moves = self.generate_export_moves(moves)
        export_header = self.generate_export_header(
            HEADER_TEMPLATE.copy(), date_from, date_to
        )
        csv_file = self.generate_csv_file(
            EXPORT_TEMPLATE.copy(), export_header, export_moves
        )
        if not csv_file:
            raise UserError(
                _("Something went wrong, because a export file could not generated!")
            )
        self.env["ir.attachment"].create(
            {
                "name": f"{export_id.name}.csv",
                "res_model": "syscoon.financeinterface",
                "res_id": export_id.id,
                "type": "binary",
                "datas": csv_file,
            }
        )
        moves.write({"export_id": export_id.id})
        return export_id

    def generate_export_moves(self, moves):
        """Generates a list of dicts which have all the exportlines to datev"""
        lines = []
        # date_range = []
        for move in moves:
            # date_range.append(move.date)
            converted_lines = self.generate_export_lines(move)
            lines += converted_lines
        return lines

    def generate_export_lines(self, move):
        """Checks if lines are exportable and inits the generation of the export line"""
        export_lines = []
        group = False
        amount_check = amount_real = 0.0
        for line in move.line_ids:
            if (
                self.env.company.datev_export_method == "gross"
                and line.tax_repartition_line_id
            ):
                continue
            if line.account_id.id == move.export_account_counterpart.id:
                if (
                    line.currency_id
                    and line.currency_id != self.env.company.currency_id
                    and line.amount_currency != 0.0
                ):
                    amount_real += line.amount_currency
                else:
                    amount_real += line.debit - line.credit
                continue
            if not line.debit and not line.credit:
                continue
            converted_line, group = self.generate_export_line(
                EXPORT_TEMPLATE.copy(), line
            )
            if converted_line["Soll/Haben-Kennzeichen"] == "S":
                amount_check -= converted_line["Umsatz (ohne Soll/Haben-Kz)"]
            else:
                amount_check += converted_line["Umsatz (ohne Soll/Haben-Kz)"]
            export_lines.append(converted_line)
        if export_lines and float_repr(amount_check, 2) != float_repr(
            float(float_repr(amount_real, 3)), 2
        ):
            export_lines = self.correct_amount(export_lines, amount_check, amount_real)
        group_journal = (
            move.journal_id.id in self.env.company.datev_group_lines.ids or False
        )
        export_lines = self.group_converted_move_lines(
            export_lines, group_journal, group
        )
        return export_lines

    def correct_amount(self, export_lines, amount_check, amount_real):
        line_count = 0
        line_to_correct = 0
        for line in export_lines:
            account_id = self.env["account.account"].search(
                [("code", "=", line["Konto"])]
            )
            counteraccount_id = self.env["account.account"].search(
                [("code", "=", line["Gegenkonto (ohne BU-Schlüssel)"])]
            )
            if not (
                account_id.account_type in ["asset_cash", "liability_credit_card"]
                or counteraccount_id.account_type
                in ["asset_cash", "liability_credit_card"]
            ):
                line_to_correct = line_count
            line_count += 1
        if export_lines[line_to_correct]["Soll/Haben-Kennzeichen"] == "H":
            difference = amount_real - amount_check
        else:
            difference = amount_check - amount_real
        new_amount = (
            export_lines[line_to_correct]["Umsatz (ohne Soll/Haben-Kz)"] + difference
        )
        export_lines[line_to_correct]["Umsatz (ohne Soll/Haben-Kz)"] = new_amount
        return export_lines

    def generate_export_line(self, export_line, line):  # noqa: C901
        """Generates the amount, the sign, the tax key and the tax case of the move line
        Computes currencies and exchange rates"""
        group = True
        if line.debit:
            total = line.debit
            export_line["Soll/Haben-Kennzeichen"] = "S"
        if line.credit:
            total = line.credit
            export_line["Soll/Haben-Kennzeichen"] = "H"
        if (
            line.currency_id
            and line.currency_id != self.env.company.currency_id
            and line.amount_currency != 0.0
        ):
            total = (
                -line.amount_currency
                if line.amount_currency < 0
                else line.amount_currency
            )
        if self.env.company.datev_export_method == "gross":
            if line.tax_ids:
                tax_id = line.tax_ids[0]
                taxes_computed = tax_id.compute_all(
                    total, line.currency_id, handle_price_include=False
                )
                total = self.compute_total_if_taxes(taxes_computed)
                if not line.account_id.datev_automatic_account:
                    if tax_id.datev_tax_key:
                        export_line["BU-Schlüssel"] = tax_id.datev_tax_key
                    if tax_id.datev_tax_case:
                        export_line["Sachverhalt"] = tax_id.datev_tax_case
                if tax_id.datev_country_id:
                    country_code = tax_id.datev_country_id.code
                    export_line["EU-Mitgliedstaat u. UStIdNr"] = country_code
                    export_line["EU-Steuersatz"] = tax_id.amount
            else:
                if (
                    line.account_id.datev_automatic_account
                    and line.account_id.datev_no_tax
                ) or line.move_id.export_account_counterpart.datev_no_tax:
                    export_line["BU-Schlüssel"] = "40"
        if (
            line.currency_id
            and line.currency_id != self.env.company.currency_id
            and line.amount_currency != 0.0
        ):
            base_total = -line.balance if line.balance < 0 else line.balance
            if self.env.company.datev_export_method == "gross" and line.tax_ids:
                base_tax_id = line.tax_ids[0]
                base_taxes_computed = base_tax_id.compute_all(
                    base_total, self.env.company.currency_id, handle_price_include=False
                )
                base_total = self.compute_total_if_taxes(base_taxes_computed)
            export_line["WKZ Umsatz"] = line.currency_id.name
            export_line["Basis-Umsatz"] = self.currency_round(
                base_total, self.env.company.currency_id
            )
            export_line["WKZ Basis-Umsatz"] = self.env.company.currency_id.name
            export_line["Kurs"] = (
                float_repr(line.amount_currency / line.balance, 4) + "00"
            )
        export_line["Umsatz (ohne Soll/Haben-Kz)"] = self.currency_round(
            total, line.currency_id
        )
        if line.partner_id:
            partner = line.partner_id.commercial_partner_id
            if (
                line.account_id.account_type == "liability_payable"
                and partner.creditor_number
            ):
                export_line["Konto"] = self.remove_leading_zero(partner.creditor_number)
            if (
                line.account_id.account_type == "asset_receivable"
                and partner.debitor_number
            ):
                export_line["Konto"] = self.remove_leading_zero(partner.debitor_number)
            if (
                line.move_id.export_account_counterpart.account_type
                == "liability_payable"
                and partner.creditor_number
            ):
                export_line[
                    "Gegenkonto (ohne BU-Schlüssel)"
                ] = self.remove_leading_zero(partner.creditor_number)
            if (
                line.move_id.export_account_counterpart.account_type
                == "asset_receivable"
                and partner.debitor_number
            ):
                export_line[
                    "Gegenkonto (ohne BU-Schlüssel)"
                ] = self.remove_leading_zero(partner.debitor_number)
        if not export_line["Konto"]:
            export_line["Konto"] = self.remove_leading_zero(line.account_id.code)
        if not export_line["Gegenkonto (ohne BU-Schlüssel)"]:
            export_line["Gegenkonto (ohne BU-Schlüssel)"] = self.remove_leading_zero(
                line.move_id.export_account_counterpart.code
            )
        export_line["Belegdatum"] = self.convert_date(
            line.move_id.date, self.env.company.datev_voucher_date_format
        )
        if line.move_id.invoice_date and line.move_id.date != line.move_id.invoice_date:
            export_line["Belegdatum"] = self.convert_date(
                line.move_id.invoice_date, self.env.company.datev_voucher_date_format
            )
            export_line["Leistungsdatum"] = self.convert_date(
                line.move_id.invoice_date, "%d%m%Y"
            )
        export_line["Belegfeld 1"], group = self.create_doc_field(line, group)
        if line.move_id.invoice_date_due:
            export_line["Belegfeld 2"] = self.convert_date(
                line.move_id.invoice_date_due, "%d%m%y"
            )
        payment_term = line.move_id.invoice_payment_term_id
        if payment_term.datev_payment_conditons_id:
            export_line["Belegfeld 2"] = payment_term.datev_payment_conditons_id
        export_line["Buchungstext"] = self.create_label(line)
        if line.company_id.datev_use_bedi:
            export_line["Beleglink"] = 'BEDI "%s"' % line.move_id.datev_bedi or ""
        if line.analytic_distribution:
            for key in line.analytic_distribution:
                analytic_account_id = self.env["account.analytic.account"].search(
                    [("id", "=", int(key))]
                )
                if analytic_account_id:
                    if analytic_account_id.plan_id.datev_cost_center == "add_to_kost1":
                        export_line["KOST1 - Kostenstelle"] = analytic_account_id.code
                    if analytic_account_id.plan_id.datev_cost_center == "add_to_kost2":
                        export_line["KOST2 - Kostenstelle"] = analytic_account_id.code
        if line.account_id.datev_vatid_required:
            vat = line.move_id.partner_shipping_id.vat or line.move_id.partner_id.vat
            export_line["EU-Mitgliedstaat u. UStIdNr"] = vat
        sdd_module = (
            self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", "account_sepa_direct_debit")])
        )
        if sdd_module and sdd_module.state == "installed":
            export_line["SEPA-Mandatsreferenz"] = line.move_id.sdd_mandate_id.name or ""
        export_line["Auftragsnummer"] = line.move_id.invoice_origin or ""
        export_line["Festschreibung"] = int(self.env.company.datev_enable_fixing)
        return export_line, group

    def get_doc_field_from_move(self, move):
        return move.datev_ref

    def get_doc_field_from_original_move(self, line):
        if not line.move_id.payment_id:
            return False
        payment = line.move_id.payment_id
        reconciled = payment.reconciled_bill_ids | payment.reconciled_invoice_ids
        return reconciled[:1].datev_ref

    def create_doc_field(self, line, group):
        """Creates the values for Belegfeld 1"""
        doc_field = False
        if line.move_id.has_reconciled_entries:
            reconciled_lines = self.env["account.move.line"].browse(
                line._reconciled_lines()
            )
            for ml in reconciled_lines:
                if (
                    ml.move_id.is_invoice() or ml.move_id.is_purchase_document()
                ) and ml.move_id.datev_ref:
                    doc_field = ml.move_id.datev_ref
                    break
        if not doc_field and self.env["ir.module.module"].sudo().search(
            [("name", "=", "account_asset"), ("state", "=", "installed")]
        ):
            if line.move_id.asset_id and line.move_id.asset_id.original_move_line_ids:
                doc_field = self.get_doc_field_from_move(
                    line.move_id.asset_id.original_move_line_ids[0].move_id
                )
            elif self.get_doc_field_from_original_move(line):
                doc_field = self.get_doc_field_from_original_move(line)
            else:
                doc_field = line.move_id.name
        if not doc_field:
            doc_field = self.get_doc_field_from_move(line.move_id) or line.move_name
        doc_field = re.sub(r"[\W_]+", "", doc_field[:36])
        return doc_field, group

    def create_label(self, line):
        """Creates the value for Buchungstext"""
        labels = (
            self.env["syscoon.financeinterface.bookingtext.config"]
            .sudo()
            .search([("journal_id", "=", line.journal_id.id)], order="sequence asc")
        )
        if not labels:
            labels = (
                self.env["syscoon.financeinterface.bookingtext.config"]
                .sudo()
                .search([], order="sequence asc")
            )
        bookingtext = []
        for label in labels:
            value = False
            if label:
                value = self.get_field(line, label.field)
            if value:
                bookingtext.append(value)
        bookingtext = ", ".join(bookingtext) if bookingtext else line.name
        if not bookingtext:
            bookingtext = line.move_id.name
        if bookingtext:
            return bookingtext[:60]

    def get_field(self, model, field_name):
        """Get the fields for creating the Buchungstext"""
        for part in field_name.split("."):
            if part in ["move_id", "partner_id"]:
                model = getattr(model, part)
            else:
                value = getattr(model, part)
        return value

    def group_converted_move_lines(self, move_lines, group_journal, group):
        """Groups the converted move lines if the group_journal is set"""
        grouped_lines = []
        checked_keys = [
            "Konto",
            "WKZ Umsatz",
            "BU-Schlüssel",
            "KOST1 - Kostenstelle",
            "KOST2 - Kostenstelle",
            "Soll/Haben-Kennzeichen",
            "Gegenkonto (ohne BU-Schlüssel)",
        ]

        def is_matching(move_val, group_val):
            return all(group_val[key] == move_val[key] for key in checked_keys)

        for ml in move_lines:
            if group_journal and group:
                if not any(is_matching(gl, ml) for gl in grouped_lines):
                    grouped_lines.append(ml)
                else:
                    for gl in grouped_lines:
                        if is_matching(gl, ml):
                            basis = "Basis-Umsatz"
                            umsatz = "Umsatz (ohne Soll/Haben-Kz)"
                            if gl[basis] or gl[basis] == 0.0 and ml[basis]:
                                gl[basis] += ml[basis]
                            if gl[umsatz] or gl[umsatz] == 0.0 and ml[umsatz]:
                                gl[umsatz] += ml[umsatz]
                            break
            else:
                grouped_lines.append(ml)
        new_lines = []
        for line in grouped_lines:
            new_lines.append(self.convert_line_float_to_char(line))
        return new_lines

    def remove_leading_zero(self, account):
        """Removes leading zeros from account codes"""
        if self.env.company.datev_remove_leading_zeros and account:
            account = account.lstrip("0")
        return account

    def generate_export_header(self, header, date_from, date_to):
        """Generates the header for the export file"""
        if int(self.env.company.fiscalyear_last_month) == 12:
            fy_start = date_from.strftime("%Y") + f"{1:02d}" + "01"
        else:
            year_from = date_from - dateutil.relativedelta.relativedelta(months=11)
            fy_start = (
                year_from.strftime("%Y")
                + f"{int(self.env.company.fiscalyear_last_month) + 1:02d}"
                + "01"
            )
        header["Erzeugt am"] = fields.datetime.now(
            timezone(self.env.context.get("tz") or self.env.user.tz or "UTC")
        ).strftime("%Y%m%d%H%M%S%f")[:-3]
        header["Beraternummer"] = self.env.company.datev_accountant_number or "10000"
        header["Mandantennummer"] = self.env.company.datev_client_number or "10000"
        header["WJBeginn"] = fy_start
        header["Sachkontenlänge"] = self.env.company.datev_account_code_digits
        header["Datumvon"] = date_from.strftime("%Y%m%d")
        header["Datumbis"] = date_to.strftime("%Y%m%d")
        header["Diktatkürzel"] = self.env.user.partner_id.name[:1]
        header["Festschreibung"] = int(self.env.company.datev_enable_fixing)
        return header

    def generate_csv_file(self, template, header, lines):
        """Generates the CSV file as in memory with StringIO"""
        buf = StringIO()
        export_csv = csv.writer(
            buf, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL
        )
        if header:
            export_csv.writerow(header.values())
        export_csv.writerow(template.keys())
        for line in lines:
            export_csv.writerow(line.values())
        output = base64.b64encode(buf.getvalue().encode("iso-8859-1", "ignore"))
        return output
