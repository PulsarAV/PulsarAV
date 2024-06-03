# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

import dateutil.relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_repr
from pytz import timezone

_logger = logging.getLogger(__name__)


class SyscoonFinanceinterface(models.Model):
    """Inherits the basic class to provide the export for DATEV ASCII Accounts"""

    _inherit = "syscoon.financeinterface"

    mode = fields.Selection(
        selection_add=[("datev_ascii_accounts", "DATEV ASCII Accounts")],
        ondelete={"datev_ascii_accounts": lambda recs: recs.write({"mode": "none"})},
    )

    def header_template_accounts(self):
        """DATEV ASCII Header V700"""
        return {
            "DATEVFormatKZ": "EXTF",
            "Versionsnummer": 700,
            "Datenkategorie": 16,
            "Formatname": "Debitoren/Kreditoren",
            "Formatversion": 5,
            "Erzeugtam": "",
            "Importiert": "",
            "Herkunft": "OE",
            "Exportiertvon": "",
            "Importiertvon": "",
            "Berater": "",
            "Mandant": "",
            "WJBeginn": "",
            "Sachkontenlaenge": "",
            "Datumvon": "",
            "Datumbis": "",
            "Bezeichnung": "Odoo-Export",
            "Diktatkuerzel": "",
            "Buchungstyp": 1,
            "Rechnungslegungszweck": "",
            "Festschreibung": "",
            "WKZ": "",
            "res1": "",
            "Derivatskennzeichen": "",
            "res2": "",
            "res3": "",
            "SKR": "",
            "Branchenlösungs-Id": "",
            "res4": "",
            "res5": "",
            "Anwendungsinformationen": "",
        }

    def export_template_accounts(self):
        """DATEV ASCII Structure V700 for deibit and credit accounts"""
        return {
            "Konto": "",
            "Name (Adressattyp Unternehmen)": "",
            "Unternehmensgegenstand": "",
            "Name (Adressattyp natürl. Person)": "",
            "Vorname (Adressattyp natürl. Person)": "",
            "Name (Adressattyp keine Angabe)": "",
            "Adressattyp": "",
            "Kurzbezeichnung": "",
            "EU-Land": "",
            "EU-UStID": "",
            "Anrede": "",
            "Titel/Akad. Grad": "",
            "Adelstitel": "",
            "Namensvorsatz": "",
            "Adressart": "",
            "Straße": "",
            "Postfach": "",
            "Postleitzahl": "",
            "Ort": "",
            "Land": "",
            "Versandzusatz": "",
            "Adresszusatz": "",
            "Abweichende Anrede": "",
            "Abw. Zustellbezeichnung 1": "",
            "Abw. Zustellbezeichnung 2": "",
            "Kennz. Korrespondenzadresse": "",
            "Adresse Gültig von": "",
            "Adresse Gültig bis": "",
            "Telefon": "",
            "Bemerkung (Telefon)": "",
            "Telefon GL": "",
            "Bemerkung (Telefon GL)": "",
            "E-Mail": "",
            "Bemerkung (E-Mail)": "",
            "Internet": "",
            "Bemerkung (Internet)": "",
            "Fax": "",
            "Bemerkung (Fax)": "",
            "Sonstige": "",
            "Bemerkung (Sonstige)": "",
            "Bankleitzahl 1": "",
            "Bankbezeichnung 1": "",
            "Bank-Kontonummer 1": "",
            "Länderkennzeichen 1": "",
            "IBAN-Nr. 1": "",
            "Leerfeld 1": "",
            "SWIFT-Code 1": "",
            "Abw. Kontoinhaber 1": "",
            "Kennz. Hauptbankverb. 1": "",
            "Bankverb 1 Gültig von": "",
            "Bankverb 1 Gültig bis": "",
            "Bankleitzahl 2": "",
            "Bankbezeichnung 2": "",
            "Bank-Kontonummer 2": "",
            "Länderkennzeichen 2": "",
            "IBAN-Nr. 2": "",
            "Leerfeld 2": "",
            "SWIFT-Code 2": "",
            "Abw. Kontoinhaber 2": "",
            "Kennz. Hauptbankverb. 2": "",
            "Bankverb 2 Gültig von": "",
            "Bankverb 2 Gültig bis": "",
            "Bankleitzahl 3": "",
            "Bankbezeichnung 3": "",
            "Bank-Kontonummer 3": "",
            "Länderkennzeichen 3": "",
            "IBAN-Nr. 3": "",
            "Leerfeld 3": "",
            "SWIFT-Code 3": "",
            "Abw. Kontoinhaber 3": "",
            "Kennz. Hauptbankverb. 3": "",
            "Bankverb 3 Gültig von": "",
            "Bankverb 3 Gültig bis": "",
            "Bankleitzahl 4": "",
            "Bankbezeichnung 4": "",
            "Bank-Kontonummer 4": "",
            "Länderkennzeichen 4": "",
            "IBAN-Nr. 4": "",
            "Leerfeld 4": "",
            "SWIFT-Code 4": "",
            "Abw. Kontoinhaber 4": "",
            "Kennz. Hauptbankverb. 4": "",
            "Bankverb 4 Gültig von": "",
            "Bankverb 4 Gültig bis": "",
            "Bankleitzahl 5": "",
            "Bankbezeichnung 5": "",
            "Bank-Kontonummer 5": "",
            "Länderkennzeichen 5": "",
            "IBAN-Nr. 5": "",
            "Leerfeld 5": "",
            "SWIFT-Code 5": "",
            "Abw. Kontoinhaber 5": "",
            "Kennz. Hauptbankverb. 5": "",
            "Bankverb 5 Gültig von": "",
            "Bankverb 5 Gültig bis": "",
            "Leerfeld 6": "",
            "Briefanrede": "",
            "Grußformel": "",
            "Kunden-/Lief.-Nr.": "",
            "Steuernummer": "",
            "Sprache": "",
            "Ansprechpartner": "",
            "Vertreter": "",
            "Sachbearbeiter": "",
            "Diverse-Konto": "",
            "Ausgabeziel": "",
            "Währungssteuerung": "",
            "Kreditlimit (Debitor)": "",
            "Zahlungsbedingung": "",
            "Fälligkeit in Tagen (Debitor)": "",
            "Skonto in Prozent (Debitor)": "",
            "Kreditoren-Ziel 1 Tg.": "",
            "Kreditoren-Skonto 1 %": "",
            "Kreditoren-Ziel 2 Tg.": "",
            "Kreditoren-Skonto 2 %": "",
            "Kreditoren-Ziel 3 Brutto Tg.": "",
            "Kreditoren-Ziel 4 Tg.": "",
            "Kreditoren-Skonto 4 %": "",
            "Kreditoren-Ziel 5 Tg.": "",
            "Kreditoren-Skonto 5 %": "",
            "Mahnung": "",
            "Kontoauszug": "",
            "Mahntext 1": "",
            "Mahntext 2": "",
            "Mahntext 3": "",
            "Kontoauszugstext": "",
            "Mahnlimit Betrag": "",
            "Mahnlimit %": "",
            "Zinsberechnung": "",
            "Mahnzinssatz 1": "",
            "Mahnzinssatz 2": "",
            "Mahnzinssatz 3": "",
            "Lastschrift": "",
            "Leerfeld 7": "",
            "Mandantenbank": "",
            "Zahlungsträger": "",
            "Indiv. Feld 1": "",
            "Indiv. Feld 2": "",
            "Indiv. Feld 3": "",
            "Indiv. Feld 4": "",
            "Indiv. Feld 5": "",
            "Indiv. Feld 6": "",
            "Indiv. Feld 7": "",
            "Indiv. Feld 8": "",
            "Indiv. Feld 9": "",
            "Indiv. Feld 10": "",
            "Indiv. Feld 11": "",
            "Indiv. Feld 12": "",
            "Indiv. Feld 13": "",
            "Indiv. Feld 14": "",
            "Indiv. Feld 15": "",
            "Abweichende Anrede (Rechnungsadresse)": "",
            "Adressart (Rechnungsadresse)": "",
            "Straße (Rechnungsadresse)": "",
            "Postfach (Rechnungsadresse)": "",
            "Postleitzahl (Rechnungsadresse)": "",
            "Ort (Rechnungsadresse)": "",
            "Land (Rechnungsadresse)": "",
            "Versandzusatz (Rechnungsadresse)": "",
            "Adresszusatz (Rechnungsadresse)": "",
            "Abw. Zustellbezeichnung 1 (Rechnungsadresse)": "",
            "Abw. Zustellbezeichnung 2 (Rechnungsadresse)": "",
            "Adresse Gültig von (Rechnungsadresse)": "",
            "Adresse Gültig bis (Rechnungsadresse)": "",
            "Bankleitzahl 6": "",
            "Bankbezeichnung 6": "",
            "Bank-Kontonummer 6": "",
            "Länderkennzeichen 6": "",
            "IBAN-Nr. 6": "",
            "Leerfeld 8": "",
            "SWIFT-Code 6": "",
            "Abw. Kontoinhaber 6": "",
            "Kennz. Hauptbankverb. 6": "",
            "Bankverb 6 Gültig von": "",
            "Bankverb 6 Gültig bis": "",
            "Bankleitzahl 7": "",
            "Bankbezeichnung 7": "",
            "Bank-Kontonummer 7": "",
            "Länderkennzeichen 7": "",
            "IBAN-Nr. 7": "",
            "Leerfeld 9": "",
            "SWIFT-Code 7": "",
            "Abw. Kontoinhaber 7": "",
            "Kennz. Hauptbankverb. 7": "",
            "Bankverb 7 Gültig von": "",
            "Bankverb 7 Gültig bis": "",
            "Bankleitzahl 8": "",
            "Bankbezeichnung 8": "",
            "Bank-Kontonummer 8": "",
            "Länderkennzeichen 8": "",
            "IBAN-Nr. 8": "",
            "Leerfeld 10": "",
            "SWIFT-Code 8": "",
            "Abw. Kontoinhaber 8": "",
            "Kennz. Hauptbankverb. 8": "",
            "Bankverb 8 Gültig von": "",
            "Bankverb 8 Gültig bis": "",
            "Bankleitzahl 9": "",
            "Bankbezeichnung 9": "",
            "Bank-Kontonummer 9": "",
            "Länderkennzeichen 9": "",
            "IBAN-Nr. 9": "",
            "Leerfeld 11": "",
            "SWIFT-Code 9": "",
            "Abw. Kontoinhaber 9": "",
            "Kennz. Hauptbankverb. 9": "",
            "Bankverb 9 Gültig von": "",
            "Bankverb 9 Gültig bis": "",
            "Bankleitzahl 10": "",
            "Bankbezeichnung 10": "",
            "Bank-Kontonummer 10": "",
            "Länderkennzeichen 10": "",
            "IBAN-Nr. 10": "",
            "Leerfeld 12": "",
            "SWIFT-Code 10": "",
            "Abw. Kontoinhaber 10": "",
            "Kennz. Hauptbankverb. 10": "",
            "Bankverb 10 Gültig von": "",
            "Bankverb 10 Gültig bis": "",
            "Nummer Fremdsystem": "",
            "Insolvent": "",
            "SEPA-Mandatsreferenz 1": "",
            "SEPA-Mandatsreferenz 2": "",
            "SEPA-Mandatsreferenz 3": "",
            "SEPA-Mandatsreferenz 4": "",
            "SEPA-Mandatsreferenz 5": "",
            "SEPA-Mandatsreferenz 6": "",
            "SEPA-Mandatsreferenz 7": "",
            "SEPA-Mandatsreferenz 8": "",
            "SEPA-Mandatsreferenz 9": "",
            "SEPA-Mandatsreferenz 10": "",
            "Verknüpftes OPOS-Konto": "",
            "Mahnsperre bis": "",
            "Lastschriftsperre bis": "",
            "Zahlungssperre bis": "",
            "Gebührenberechnung": "",
            "Mahngebühr 1": "",
            "Mahngebühr 2": "",
            "Mahngebühr 3": "",
            "Pauschalenberechnung": "",
            "Verzugspauschale 1": "",
            "Verzugspauschale 2": "",
            "Verzugspauschale 3": "",
            "Alternativer Suchname": "",
            "Status": "",
            "Anschrift manuell geändert (Korrespondenzadresse)": "",
            "Anschrift individuell (Korrespondenzadresse)": "",
            "Anschrift manuell geändert (Rechnungsadresse)": "",
            "Anschrift individuell (Rechnungsadresse)": "",
            "Fristberechnung bei Debitor": "",
            "Mahnfrist 1": "",
            "Mahnfrist 2": "",
            "Mahnfrist 3": "",
            "Letzte Frist": "",
        }

    def export_template_accounts_duo(self):
        return {
            "Name": "",
            "Ort": "",
            "Kontonummer": "",
            "Kundennummer": "",
            "UStIdNr.": "",
            "Bankkonto": "",
            "BLZ": "",
            "BankName": "",
            "Länderkennzeichen": "",
            "IBAN": "",
            "BIC": "",
            "Anrede": "",
            "Adresszusatz": "",
            "Straße": "",
            "PLZ": "",
            "Steuernummer": "",
            "Ansprechpartner": "",
            "Telefonnummer": "",
            "E-Mail": "",
            "Faxnummer": "",
            "Internetadresse": "",
            "Land (2-stellig)": "",
            "UStEG-Land": "",
        }

    def _get_export_partners(self, account_kind, account):
        domain = []
        if account_kind == "all":
            if account == "debit":
                domain = [("parent_id", "=", False), ("debitor_number", "!=", False)]
            elif account == "credit":
                domain = [("parent_id", "=", False), ("creditor_number", "!=", False)]
            elif account == "both":
                domain = [
                    ("parent_id", "=", False),
                    "|",
                    ("debitor_number", "!=", False),
                    ("creditor_number", "!=", False),
                ]
        elif account_kind == "new":
            if account == "debit":
                domain = [
                    ("datev_exported", "=", "false"),
                    ("debitor_number", "!=", False),
                    ("parent_id", "=", False),
                ]
            elif account == "credit":
                domain = [
                    ("datev_exported", "=", "false"),
                    ("creditor_number", "!=", False),
                    ("parent_id", "=", False),
                ]
            elif account == "both":
                domain = [
                    ("datev_exported", "=", "false"),
                    "|",
                    ("debitor_number", "!=", False),
                    ("creditor_number", "!=", False),
                    ("parent_id", "=", False),
                ]
        partner_obj = self.env["res.partner"]
        return partner_obj.sudo().search(domain) if domain else partner_obj

    def export(self, mode=False, date_from=False, date_to=False, args=False):
        """Method that generates the csv export by the given parameters"""
        csv = False
        export_id = super().export(mode, date_from, date_to, args)
        if mode != "datev_ascii_accounts":
            return export_id
        if not args:
            raise UserError(_("There are not all parameters given, that are necessary"))
        kind, account_kind, account = args
        partner_ids = self._get_export_partners(account_kind, account)
        if not partner_ids:
            raise UserError(
                _(
                    "There are no accounts to export with your export-settings.\n"
                    "Please check them!"
                )
            )
        export_header = False
        export_lines = self.generate_export_partners(partner_ids, kind)
        if kind == "rewe":
            export_header = self.generate_partner_export_header(
                self.header_template_accounts(), date_from
            )
            template = self.export_template_accounts()
        else:
            template = self.export_template_accounts_duo()
        csv = self.generate_csv_file(template, export_header, export_lines)
        if not csv:
            raise UserError(
                _("Something went wrong, because a export file could not generated!")
            )
        self.env["ir.attachment"].create(
            {
                "name": "%s.csv" % (export_id.name),
                "res_model": "syscoon.financeinterface",
                "res_id": export_id.id,
                "type": "binary",
                "datas": csv,
            }
        )
        partner_ids.write({"datev_exported": "true"})
        return export_id

    def generate_export_partners(self, partner_ids, kind):
        """Generates a list of dicts which have all the exportlines to datev"""
        export_lines = []
        for partner_id in partner_ids:
            partner_numbers = []
            if partner_id.debitor_number:
                partner_numbers.append("D" + partner_id.debitor_number)
            if partner_id.creditor_number:
                partner_numbers.append("C" + partner_id.creditor_number)
            for number in partner_numbers:
                if not number:
                    continue
                if kind == "rewe":
                    converted_partner, _account_id = self.generate_rewe_partner(
                        partner_id, number, self.export_template_accounts()
                    )
                else:
                    converted_partner, _account_id = self.generate_duo_partner(
                        partner_id, number, self.export_template_accounts_duo()
                    )
                export_lines.append(converted_partner)
        return export_lines

    @api.model
    def _get_eu_vat_code(self):
        return (
            "BE",
            "BG",
            "DK",
            "DE",
            "EE",
            "FI",
            "FR",
            "GR",
            "GB",
            "IE",
            "IT",
            "HR",
            "LV",
            "LT",
            "LU",
            "MT",
            "NL",
            "AT",
            "PL",
            "PT",
            "RO",
            "SE",
            "SK",
            "SI",
            "ES",
            "CZ",
            "HU",
            "CY",
        )

    def _prepare_partner_invoice_address_values(self, partner_id):
        values = {}
        child_id = partner_id.child_ids.filtered(lambda c: c.type == "invoice")[-1:]
        if child_id:
            values["Straße (Rechnungsadresse)"] = child_id.street or ""
            values["Postleitzahl (Rechnungsadresse)"] = child_id.zip or ""
            values["Ort (Rechnungsadresse)"] = child_id.city or ""
            values["Land (Rechnungsadresse)"] = child_id.country_id.code or ""
            values["Adresszusatz (Rechnungsadresse)"] = child_id.street2 or ""
        return values

    def _prepare_partner_bank_values(self, partner_id):
        bank_count = 1
        values = {}
        for bank in partner_id.bank_ids:
            if bank_count > 5:
                continue
            values["Bankbezeichnung %s" % bank_count] = bank.bank_id.name or ""
            values["Abw. Kontoinhaber %s" % bank_count] = bank.acc_holder_name or ""
            if bank.acc_type == "iban":
                values["IBAN-Nr. %s" % bank_count] = bank.acc_number or ""
                values["SWIFT-Code %s" % bank_count] = bank.bank_id.bic or ""
            else:
                values["Bankleitzahl %s" % bank_count] = bank.bank_id.bic or ""
                values["Bank-Kontonummer %s" % bank_count] = bank.acc_number or ""
                values["Länderkennzeichen %s" % bank_count] = (
                    bank.bank_id.country.code or ""
                )
            if bank_count == 1:
                values["Kennz. Hauptbankverb. %s" % bank_count] = 1
            else:
                values["Kennz. Hauptbankverb. %s" % bank_count] = 0
            bank_count += 1
        return values

    def _prepare_partner_template_values(self, partner_id):
        values = {}
        values["Kurzbezeichnung"] = partner_id.name[:15] or ""
        if partner_id.is_company:
            values["Name (Adressattyp Unternehmen)"] = partner_id.name
            values["Unternehmensgegenstand"] = partner_id.industry_id.full_name or ""
            values["Adressattyp"] = 2
        else:
            values["Name (Adressattyp natürl. Person)"] = partner_id.name
            values["Adressattyp"] = 1
        if partner_id.vat and partner_id.vat[:2] in self._get_eu_vat_code():
            values["EU-Land"] = partner_id.vat[:2]
            values["EU-UStID"] = partner_id.vat[2:]
        if partner_id.title:
            values["Anrede"] = partner_id.title.name or ""
        values["Adressart"] = "STR"
        values["Straße"] = partner_id.street or ""
        values["Postleitzahl"] = partner_id.zip or ""
        values["Ort"] = partner_id.city or ""
        values["Land"] = partner_id.country_id.code or ""
        values["Telefon"] = partner_id.phone or ""
        values["E-Mail"] = partner_id.email or ""
        values["Internet"] = partner_id.website or ""
        bank_vals = self._prepare_partner_bank_values(partner_id)
        inv_address_vals = self._prepare_partner_invoice_address_values(partner_id)
        values.update(bank_vals)
        values.update(inv_address_vals)
        return values

    def _prepare_creditor_payment_term_values(self, partner_id):
        values = {}
        term_id = partner_id.property_supplier_payment_term_id
        for val in range(1, 3):
            goal = f"Kreditoren-Ziel {str(val)} Tg."
            discount = f"Kreditoren-Skonto {str(val)} %"
            if term_id.early_discount and val == 1:
                values[goal] = term_id.discount_days
                values[discount] = float_repr(term_id.discount_percentage, 2)
            else:
                values[goal] = self._get_max_days(term_id)
                values[discount] = float_repr(0.0, 2)
                break
        return values

    def _prepare_debitor_payment_term_values(self, partner_id):
        values = {}
        term_id = partner_id.property_payment_term_id
        if term_id.early_discount:
            values["Skonto in Prozent (Debitor)"] = float_repr(
                term_id.discount_percentage, 2
            )
        days = self._get_max_days(term_id) or ""
        values["Fälligkeit in Tagen (Debitor)"] = days
        return values

    def _get_max_days(self, term_id):
        days = []
        for line in term_id.line_ids:
            days.append(line.nb_days)
        return max(days)

    def generate_rewe_partner(self, partner_id, number, template):
        """Checks if lines are exportable and inits the generation of the export line"""
        partner_id.with_company(self.env.company)
        account_id = self.env["account.account"].search([("code", "=", number[1:])])
        template["Konto"] = account_id.code or number[1:]
        basic_vals = self._prepare_partner_template_values(partner_id)
        template.update(basic_vals)
        template["Kunden-/Lief.-Nr."] = partner_id.ref or ""
        if account_id and account_id.datev_diverse_account:
            template["Diverse-Konto"] = 1
        else:
            template["Diverse-Konto"] = 0
        if (
            partner_id.property_payment_term_id
            and number[1:] == partner_id.debitor_number
        ):
            template.update(self._prepare_debitor_payment_term_values(partner_id))

        if (
            partner_id.property_supplier_payment_term_id
            and number[1:] == partner_id.creditor_number
        ):
            template.update(self._prepare_creditor_payment_term_values(partner_id))
        sdd_module = (
            self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", "account_sepa_direct_debit")])
        )
        if sdd_module and sdd_module.state == "installed":
            sdd_count = 1
            for sdd in partner_id.sdd_mandate_ids:
                if sdd_count > 10:
                    continue
                if sdd.state == "active":
                    template["SEPA-Mandatsreferenz %s" % sdd_count] = sdd.name or ""
                    sdd_count += 1
        if number[:1] == "D":
            template["Zahlungsbedingung"] = (
                partner_id.property_payment_term_id.datev_payment_conditons_id
            )
        if number[:1] == "C":
            template["Zahlungsbedingung"] = (
                partner_id.property_supplier_payment_term_id.datev_payment_conditons_id
            )
        return template, account_id

    def generate_duo_partner(self, partner_id, number, template):
        account_id = self.env["account.account"].search([("code", "=", number[1:])])
        template["Name"] = partner_id.name
        template["Ort"] = partner_id.city or ""
        template["Kontonummer"] = number[1:] or ""
        template["Kundennummer"] = partner_id.ref or ""
        if partner_id.vat:
            template["UStIdNr."] = partner_id.vat[2:]
        if partner_id.bank_ids:
            template["BankName"] = partner_id.bank_ids[0].bank_id.name
            template["Länderkennzeichen"] = partner_id.bank_ids[0].acc_number[:2]
            template["IBAN"] = partner_id.bank_ids[0].acc_number
            template["BIC"] = partner_id.bank_ids[0].bank_id.bic
        template["Adresszusatz"] = partner_id.street2 or ""
        template["Straße"] = partner_id.street or ""
        template["PLZ"] = partner_id.zip or ""
        template["Telefonnummer"] = partner_id.phone or ""
        template["E-Mail"] = partner_id.email or ""
        template["Internetadresse"] = partner_id.website or ""
        template["Land (2-stellig)"] = partner_id.country_id.code or ""
        if partner_id.vat:
            template["UStEG-Land"] = partner_id.vat[:2]
        return template, account_id

    def generate_partner_export_header(self, header, date_from):
        if int(self.env.company.fiscalyear_last_month) == 12:
            fy_start = date_from.strftime("%Y") + f"{1:02d}" + "01"
        else:
            year_from = date_from - dateutil.relativedelta.relativedelta(months=11)
            fy_start = (
                year_from.strftime("%Y")
                + f"{int(self.env.company.fiscalyear_last_month) + 1:02d}"
                + "01"
            )
        header["Versionsnummer"] = 700
        header["Datenkategorie"] = 16
        header["Formatname"] = "Debitoren/Kreditoren"
        header["Formatversion"] = 5
        header["Erzeugtam"] = fields.datetime.now(
            timezone(self.env.context.get("tz") or self.env.user.tz or "UTC")
        ).strftime("%Y%m%d%H%M%S%f")[:-3]
        header["Exportiertvon"] = self.env.user.partner_id.name
        header["Berater"] = self.env.company.datev_accountant_number
        header["Mandant"] = self.env.company.datev_client_number
        header["WJBeginn"] = fy_start
        return header
