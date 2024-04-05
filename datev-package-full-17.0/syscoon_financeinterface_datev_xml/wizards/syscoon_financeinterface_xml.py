# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from lxml import etree
from odoo import _, models
from odoo.tools import float_repr

EU_VAT = [
    "BE",
    "BG",
    "DK",
    "DE",
    "EE",
    "FI",
    "FR",
    "EL",
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
]


class SyscoonFinanceinterfaceXML(models.TransientModel):
    _name = "syscoon.financeinterface.xml"
    _description = "definitions for the syscoon financeinterface DATEV XML-export"

    def create_invoice_xml(self, move_id, invoice_mode):
        xml = self.make_invoice_xml(move_id, invoice_mode)
        invoice = etree.tostring(
            xml, pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )
        return invoice

    def get_subelement(self, tag, values):
        elem = etree.Element(tag)
        for key, val in values.items():
            if val:
                elem.attrib[key] = self.make_string(val)
            if key == "tax" and val == 0.0:
                elem.attrib[key] = self.make_string(val)
        return elem

    def make_string(self, val):
        if isinstance(val, float):
            return format(val, ".2f")
        return str(val)

    def get_invoice_info(self, move_id, invoice_mode):
        vals = {}
        vals["invoice_date"] = move_id.invoice_date
        if move_id.move_type in ["out_invoice", "in_invoice"]:
            vals["invoice_type"] = "Rechnung"
        if move_id.move_type in ["out_refund", "in_refund"]:
            vals["invoice_type"] = "Gutschrift/Rechnungskorrektur"
        if move_id.move_type in ["in_invoice", "in_refund"] and move_id.ref:
            vals["invoice_id"] = re.sub(r"[^\w]", "", move_id.ref[:36])
        else:
            vals["invoice_id"] = re.sub(r"[^\w]", "", move_id.name[:36])
        vals["delivery_date"] = str(move_id.date)
        return vals

    def get_accounting_info(self, move_id, invoice_mode):
        vals = {}
        if move_id.move_type == "out_invoice":
            vals["booking_text"] = "Erlöse"
        if move_id.move_type == "out_refund":
            vals["booking_text"] = "Gutschrift Erlöse"
        if move_id.move_type == "in_invoice":
            vals["booking_text"] = "Aufwand"
        if move_id.move_type == "in_refund":
            vals["booking_text"] = "Gutschrift Aufwand"
        return vals

    def _prepare_address_values(self, partner_id, invoice_mode, check_for_ref=False):
        vals = {}
        if partner_id.name:
            vals["name"] = partner_id.name[:50]
        elif partner_id.parent_id.name:
            vals["name"] = partner_id.parent_id.name[:50]
        if partner_id.street:
            vals["street"] = partner_id.street[:40]
        if partner_id.zip:
            vals["zip"] = partner_id.zip
        if partner_id.city:
            vals["city"] = partner_id.city
        if partner_id.country_id:
            vals["country"] = partner_id.country_id.code
        if invoice_mode == "extended":
            if partner_id.phone:
                vals["phone"] = partner_id.phone[:20]
            if (
                "ref" in partner_id._fields
                and partner_id.ref
                and (
                    not check_for_ref
                    or (check_for_ref and partner_id.ref != partner_id.customer_number)
                )
            ):
                vals["party_id"] = partner_id.ref[:15]
        return vals

    def _prepare_account_values(self, partner_bank_id):
        vals = {}
        if partner_bank_id.sanitized_acc_number:
            vals["iban"] = partner_bank_id.sanitized_acc_number
        if partner_bank_id.bank_id.bic:
            vals["swiftcode"] = partner_bank_id.bank_id.bic
        if partner_bank_id.bank_id.name:
            vals["bank_name"] = partner_bank_id.bank_id.name[:27]
        return vals

    def get_invoice_party(self, move_id, invoice_mode):
        if move_id.move_type in ["out_invoice", "out_refund"]:
            partner_id = move_id.commercial_partner_id
            booking_info = True
        if move_id.move_type in ["in_invoice", "in_refund"]:
            partner_id = move_id.company_id.partner_id
            booking_info = False
        vals = {}
        if partner_id.vat and partner_id.vat[:2] in EU_VAT:
            vals["vat_id"] = partner_id.vat
        address_val = self._prepare_address_values(
            partner_id, invoice_mode, check_for_ref=True
        )
        vals["address"] = address_val
        if invoice_mode == "extended" and booking_info:
            if move_id.partner_bank_id:
                partner_bank_id = move_id.partner_bank_id
                if partner_bank_id.acc_type == "iban" and partner_bank_id.bank_id.name:
                    vals["account"] = self._prepare_account_values(partner_bank_id)
            vals["booking_info_bp"] = {
                "bp_account_no": (
                    partner_id.debitor_number
                    or partner_id.property_account_receivable_id.code
                )
            }
        return vals

    def get_supplier_party(self, move_id, invoice_mode):
        if move_id.move_type in ["out_invoice", "out_refund"]:
            partner_id = move_id.company_id.partner_id
            booking_info = False
        if move_id.move_type in ["in_invoice", "in_refund"]:
            partner_id = move_id.commercial_partner_id
            booking_info = True
        vals = {}
        if partner_id.vat and partner_id.vat[:2] in EU_VAT:
            vals["vat_id"] = partner_id.vat
        address_val = self._prepare_address_values(partner_id, invoice_mode)
        vals["address"] = address_val
        if invoice_mode == "extended" and booking_info:
            if move_id.partner_bank_id:
                partner_bank_id = move_id.partner_bank_id
                if partner_bank_id.acc_type == "iban" and partner_bank_id.bank_id.name:
                    vals["account"] = self._prepare_account_values(partner_bank_id)
            code = (
                partner_id.creditor_number
                or partner_id.property_account_payable_id.code
            )
            vals.update(
                {
                    "booking_info_bp": {"bp_account_no": code},
                    "party_id": partner_id.supplier_number or code,
                }
            )
        return vals

    def get_payment_conditions(self, move_id):
        vals = {}
        payment_term = move_id.invoice_payment_term_id
        vals["currency"] = move_id.currency_id.name
        vals["due_date"] = move_id.invoice_date_due
        vals["payment_conditions_text"] = payment_term.name
        if payment_term.datev_payment_conditons_id:
            vals["payment_conditions_id"] = payment_term.datev_payment_conditons_id
        return vals

    def get_invoice_item_list(self, move_id, invoice_mode):  # noqa: C901
        vals = []
        total_invoice_amount = 0.0
        checked_keys = [
            ("price_line_amount", "tax"),
            ("accounting_info", "account_no"),
            ("accounting_info", "cost_category_id"),
            ("accounting_info", "cost_category_id2"),
            ("accounting_info", "bu_code"),
        ]

        def is_matching(vals_1, vals_2):
            return all(
                vals_1[key].get(child_key) == vals_2[key].get(child_key)
                for key, child_key in checked_keys
            )

        for line in move_id.invoice_line_ids:
            if (
                line.display_type not in ["line_section", "line_note"]
                and line.price_subtotal != 0.0
            ):
                item = self._get_invoice_item_list_item(move_id, line, invoice_mode)
                vals.append(item)
        if self.env.company.export_xml_group_lines and invoice_mode == "extended":
            new_vals = []
            for val in vals:
                if not any(is_matching(new_val, val) for new_val in new_vals):
                    new_vals.append(val)
                else:
                    for new_val in new_vals:
                        if not is_matching(new_val, val):
                            continue
                        new_val["description_short"] = _("Grouped Invoice Line")
                        new_val["quantity"] += val["quantity"]
                        amount_vals = val["price_line_amount"]
                        new_amount_vals = new_val["price_line_amount"]
                        gross_amount = amount_vals["gross_price_line_amount"]
                        net_amount = amount_vals["net_price_line_amount"]
                        if amount_vals.get("tax_amount"):
                            new_amount_vals["tax_amount"] += amount_vals["tax_amount"]
                        new_amount_vals["gross_price_line_amount"] += gross_amount
                        new_amount_vals["net_price_line_amount"] += net_amount
                        break
            for new_val in new_vals:
                new_amount_vals = new_val["price_line_amount"]
                new_val["quantity"] = 1.0
                if not new_amount_vals.get("tax_amount"):
                    total_invoice_amount += new_amount_vals["gross_price_line_amount"]
                else:
                    new_val["price_line_amount"][
                        "gross_price_line_amount"
                    ] = move_id.currency_id.round(
                        new_val["price_line_amount"]["net_price_line_amount"]
                        * (100 + new_val["price_line_amount"]["tax"])
                        / 100
                    )
                    new_val["price_line_amount"]["tax_amount"] = (
                        new_val["price_line_amount"]["gross_price_line_amount"]
                        - new_val["price_line_amount"]["net_price_line_amount"]
                    )
                    total_invoice_amount += new_val["price_line_amount"][
                        "gross_price_line_amount"
                    ]
                    if new_val["price_line_amount"].get("tax_amount") and float_repr(
                        new_val["price_line_amount"]["tax_amount"], 2
                    ) in ["0.00", "-0.00"]:
                        new_val["price_line_amount"].pop("tax_amount")
            vals = new_vals
        else:
            for val in vals:
                price_line_ammount = dict(val["price_line_amount"])
                if "gross_price_line_amount" in price_line_ammount:
                    total_invoice_amount += val["price_line_amount"][
                        "gross_price_line_amount"
                    ]
        if float_repr(total_invoice_amount, 2) != float_repr(move_id.amount_total, 2):
            sign = -1 if move_id.move_type in ["in_refund", "out_refund"] else 1
            difference = move_id.currency_id.round(
                total_invoice_amount - (move_id.amount_total * sign)
            )
            if vals:
                last_val = vals[-1]
                del vals[-1]
                if last_val["price_line_amount"].get("tax_amount"):
                    last_val["price_line_amount"][
                        "tax_amount"
                    ] = move_id.currency_id.round(
                        last_val["price_line_amount"]["tax_amount"] - difference
                    )
                if last_val["price_line_amount"].get("gross_price_line_amount", 0.0):
                    last_val["price_line_amount"][
                        "gross_price_line_amount"
                    ] = move_id.currency_id.round(
                        last_val["price_line_amount"].get(
                            "gross_price_line_amount", 0.0
                        )
                        - difference
                    )
                vals.append(last_val)
        return vals

    def _get_invoice_item_list_item(self, move_id, line, invoice_mode):  # noqa: C901
        item = {
            "description_short": line.name[:40] if line.name else _("Description"),
            "quantity": line.quantity if line.quantity else 1.0,
            "price_line_amount": {"tax": line.tax_ids[:1].amount},
        }
        if invoice_mode != "extended":
            return item
        tax_amount = move_id.currency_id.round(line.price_total - line.price_subtotal)
        sign = 1
        if move_id.move_type in ["out_refund", "in_refund"]:
            sign = -1
        if tax_amount != 0.0:
            item["price_line_amount"]["tax_amount"] = sign * tax_amount
        item["price_line_amount"].update(
            {
                "gross_price_line_amount": sign * line.price_total,
                "net_price_line_amount": sign * line.price_subtotal,
                "currency": line.currency_id.name or "EUR",
            }
        )
        item["accounting_info"] = {
            "account_no": line.account_id.code.lstrip("0"),
            "bu_code": False,
        }
        if (
            line.currency_id
            and line.currency_id != line.company_id.currency_id
            and line.amount_currency != 0.0
        ):
            exchange_rate = line.amount_currency / line.balance
            item["accounting_info"]["exchange_rate"] = f"{exchange_rate:.6f}"
        item["accounting_info"].update(
            {
                "bu_code": False,
                "booking_text": line.name and line.name[:60] or _("Description"),
            }
        )
        tax_key = line.tax_ids[:1].datev_tax_key
        if not line.account_id.datev_automatic_account and tax_key != "0":
            item["accounting_info"]["bu_code"] = tax_key
        if move_id.company_id.export_xml_analytic_accounts:
            analytic_obj = self.env["account.analytic.account"]
            if line.analytic_distribution:  # value might be Boolean
                for key in line.analytic_distribution:
                    analytic_id = analytic_obj.search([("id", "=", int(key))])
                    if not analytic_id:
                        continue
                    if analytic_id.plan_id.datev_cost_center == "add_to_kost1":
                        item["accounting_info"]["cost_category_id"] = analytic_id.code
                    if analytic_id.plan_id.datev_cost_center == "add_to_kost2":
                        item["accounting_info"]["cost_category_id2"] = analytic_id.code
        return item

    def get_total_amount(self, move_id, invoice_mode):
        vals = {}
        if move_id.move_type in ["out_refund", "in_refund"]:
            total = -move_id.amount_total
        else:
            total = move_id.amount_total
        vals["total_gross_amount_excluding_third-party_collection"] = total
        if invoice_mode == "extended":
            if move_id.move_type in ["out_refund", "in_refund"]:
                vals["net_total_amount"] = -move_id.amount_untaxed
            else:
                vals["net_total_amount"] = move_id.amount_untaxed
        vals["currency"] = move_id.currency_id.name or "EUR"
        tax_lines = move_id.line_ids.filtered(lambda line: line.tax_line_id)
        tax_key_lines = move_id.line_ids.filtered(lambda line: line.tax_ids)
        currency_rate = 1.0
        if move_id.currency_id and move_id.currency_id != self.env.company.currency_id:
            currency_rate = move_id.company_id.currency_id._convert(
                1.0, move_id.currency_id, move_id.company_id, move_id.date, round=False
            )
        result = {}
        done_taxes = set()
        for line in tax_lines:
            result.setdefault(
                line.tax_line_id.tax_group_id,
                {"rate": 0.0, "base": 0.0, "amount": 0.0, "currency_amount": 0.0},
            )
            result[line.tax_line_id.tax_group_id]["rate"] = line.tax_line_id.amount
            result[line.tax_line_id.tax_group_id]["amount"] += abs(line.balance)
            tax_key_add_base = (line.tax_line_id.id,)
            base_amount = line.tax_base_amount * currency_rate
            if tax_key_add_base not in done_taxes:
                # The base should be added ONCE
                result[line.tax_line_id.tax_group_id]["base"] += base_amount
                done_taxes.add(tax_key_add_base)
        for line in tax_key_lines:
            result.setdefault(
                line.tax_ids[0].tax_group_id,
                {"rate": 0.0, "base": 0.0, "amount": 0.0, "currency_amount": 0.0},
            )
            if line.tax_ids[0].amount == 0.0:
                result[line.tax_ids[0].tax_group_id]["base"] += (
                    line.debit + line.credit
                ) * currency_rate
                result[line.tax_ids[0].tax_group_id]["currency_amount"] += (
                    -line.amount_currency
                    if line.amount_currency < 0.0
                    else line.amount_currency
                )
        vals["tax_line"] = self._prepare_tax_line_values(
            move_id, invoice_mode, currency_rate, result
        )
        if not vals["tax_line"]:
            line_vals = {}
            line_vals["tax"] = 0.0
            line_vals["currency"] = move_id.currency_id.name
            vals["tax_line"].append(line_vals)
        return vals

    def _prepare_tax_line_values(
        self, move_id, invoice_mode, currency_rate, result_values
    ):
        value_list = []
        result_values = sorted(result_values.items(), key=lambda l: l[0].sequence)
        for _group, amounts in result_values:
            line_vals = {}
            line_vals["tax"] = amounts["rate"]
            line_vals["currency"] = move_id.currency_id.name
            if amounts["rate"] != 0.0:
                currency_rate = 1.0
            if (
                amounts["currency_amount"]
                and amounts["base"] != amounts["currency_amount"]
            ):
                amounts["base"] = amounts["currency_amount"]
            if invoice_mode == "extended":
                if move_id.move_type in ["out_refund", "in_refund"]:
                    line_vals["net_price_line_amount"] = -amounts["base"]
                    line_vals["gross_price_line_amount"] = -amounts["base"] + (
                        amounts["amount"] * currency_rate
                    )
                else:
                    line_vals["net_price_line_amount"] = amounts["base"]
                    line_vals["gross_price_line_amount"] = amounts["base"] + (
                        amounts["amount"] * currency_rate
                    )
                if amounts["amount"] > 0.0:
                    if move_id.move_type in ["out_refund", "in_refund"]:
                        line_vals["tax_amount"] = -amounts["amount"]
                    else:
                        line_vals["tax_amount"] = amounts["amount"]
            value_list.append(line_vals)
        return value_list

    def get_additional_footer(self, move_id):
        text = self.env["syscoon.financeinterface"].text_from_html(
            move_id.narration, max_chars=60
        )
        if text:
            return False
        return {"type": "text", "context": text}

    def make_invoice_xml(self, move_id, invoice_mode):
        attr_qname = etree.QName(
            "http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"
        )
        nsmap = {
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            None: "http://xml.datev.de/bedi/tps/invoice/v050",
        }

        invoice = etree.Element(
            "invoice",
            {
                attr_qname: "http://xml.datev.de/bedi/tps/invoice/v050 "
                "Belegverwaltung_online_invoice_v050.xsd"
            },
            nsmap=nsmap,
        )
        invoice.attrib["generator_info"] = "Odoo 13"
        invoice.attrib["generating_system"] = "Odoo-ERP Software"
        invoice.attrib["description"] = "DATEV Import invoices"
        invoice.attrib["version"] = "5.0"
        invoice.attrib[
            "xml_data"
        ] = "Kopie nur zur Verbuchung berechtigt nicht zum Vorsteuerabzug"

        invoice_info = etree.SubElement(invoice, "invoice_info")
        for key, val in self.get_invoice_info(move_id, invoice_mode).items():
            invoice_info.attrib[key] = self.make_string(val)

        if invoice_mode == "extended":
            account_info = etree.SubElement(invoice, "accounting_info")
            for key, val in self.get_accounting_info(move_id, invoice_mode).items():
                account_info.attrib[key] = self.make_string(val)

        self._process_invoice_party_xml(move_id, invoice_mode, invoice)
        self._process_supplier_party_xml(move_id, invoice_mode, invoice)
        self._process_payment_conditions_xml(move_id, invoice_mode, invoice)
        self._process_invoice_item_list_xml(move_id, invoice_mode, invoice)
        self._process_total_amount_xml(move_id, invoice_mode, invoice)
        self._process_additional_info_footer_xml(move_id, invoice_mode, invoice)

        return invoice

    def _process_invoice_party_xml(self, move_id, invoice_mode, invoice_element):
        invoice_party = etree.SubElement(invoice_element, "invoice_party")
        for key, val in self.get_invoice_party(move_id, invoice_mode).items():
            if key == "vat_id":
                invoice_party.attrib[key] = self.make_string(val)
            if key == "address":
                invoice_party.append(self.get_subelement(key, val))
            if key == "account":
                invoice_party.append(self.get_subelement(key, val))
            if key == "booking_info_bp":
                invoice_party.append(self.get_subelement(key, val))
        return invoice_party

    def _process_supplier_party_xml(self, move_id, invoice_mode, invoice_element):
        supplier_party = etree.SubElement(invoice_element, "supplier_party")
        for key, val in self.get_supplier_party(move_id, invoice_mode).items():
            if key == "vat_id":
                supplier_party.attrib[key] = self.make_string(val)
            if key == "address":
                supplier_party.append(self.get_subelement(key, val))
            if key == "account":
                supplier_party.append(self.get_subelement(key, val))
            if key == "booking_info_bp":
                supplier_party.append(self.get_subelement(key, val))
        return supplier_party

    def _process_payment_conditions_xml(self, move_id, invoice_mode, invoice_element):
        payment_conditions = False
        if invoice_mode == "extended" and move_id.invoice_payment_term_id:
            payment_conditions = etree.SubElement(invoice_element, "payment_conditions")
            for key, val in self.get_payment_conditions(move_id).items():
                payment_conditions.attrib[key] = self.make_string(val)
        return payment_conditions

    def _process_invoice_item_list_xml(self, move_id, invoice_mode, invoice_element):
        invoice_item_list = False
        for item in self.get_invoice_item_list(move_id, invoice_mode):
            invoice_item_list = etree.SubElement(invoice_element, "invoice_item_list")
            for key, val in item.items():
                if key == "description_short":
                    invoice_item_list.attrib[key] = self.make_string(val)
                if key == "quantity":
                    invoice_item_list.attrib[key] = self.make_string(val)
                if key == "price_line_amount":
                    invoice_item_list.append(self.get_subelement(key, val))
                if key == "accounting_info":
                    invoice_item_list.append(self.get_subelement(key, val))
        return invoice_item_list

    def _process_total_amount_xml(self, move_id, invoice_mode, invoice_element):
        total_amount = etree.SubElement(invoice_element, "total_amount")
        for key, val in self.get_total_amount(move_id, invoice_mode).items():
            if key != "tax_line":
                total_amount.attrib[key] = self.make_string(val)
            if key == "tax_line":
                for line in val:
                    total_amount.append(self.get_subelement(key, line))
        return total_amount

    def _process_additional_info_footer_xml(
        self, move_id, invoice_mode, invoice_element
    ):
        additional_info_footer = False
        narration = False
        if move_id.narration:
            narration = self.env["syscoon.financeinterface"].text_from_html(
                move_id.narration
            )
        if narration:
            vals = self.get_additional_footer(move_id)
            if vals:
                additional_info_footer = etree.SubElement(
                    invoice_element, "additional_info_footer"
                )
                additional_info_footer.attrib["type"] = vals["type"]
                additional_info_footer.attrib["content"] = vals["context"]
        return additional_info_footer

    def create_documents_xml(self, docs, timestamp, invoice_mode):
        xml = self.make_documents_xml(docs, timestamp, invoice_mode)
        documents = etree.tostring(
            xml, pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )
        return documents

    def make_documents_xml(self, docs, timestamp, invoice_mode):
        attr_qname = etree.QName(
            "http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"
        )
        qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "type")
        nsmap = {
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            None: "http://xml.datev.de/bedi/tps/document/v05.0",
        }
        archive = etree.Element(
            "archive",
            {
                attr_qname: "http://xml.datev.de/bedi/tps/document/v05.0 "
                "document_v050.xsd"
            },
            nsmap=nsmap,
        )
        archive.attrib["version"] = "5.0"
        archive.attrib["generatingSystem"] = "Odoo-ERP Software"
        header = etree.SubElement(archive, "header")
        date = etree.SubElement(header, "date")
        date.text = str(timestamp)
        description = etree.SubElement(header, "description")
        description.text = "Rechnungsexport"
        content = etree.SubElement(archive, "content")
        if invoice_mode == "bedi":
            for doc in docs:
                document = etree.SubElement(content, "document")
                if doc.inv.datev_bedi:
                    document.attrib["guid"] = doc.inv.datev_bedi
                extension = etree.Element("extension", {qname: "File"})
                extension.attrib["name"] = doc.pdf_path
                document.append(extension)
        else:
            for doc in docs:
                document = etree.SubElement(content, "document")
                extension = etree.Element("extension", {qname: "Invoice"})
                extension.attrib["datafile"] = doc.xml_path
                tree_property = etree.SubElement(extension, "property")
                tree_property.attrib["key"] = "InvoiceType"
                tree_property.attrib["value"] = self.get_document_value(doc.inv)
                document.append(extension)
                extension = etree.Element("extension", {qname: "File"})
                extension.attrib["name"] = doc.pdf_path
                document.append(extension)
        return archive

    def get_document_value(self, move_id):
        if move_id.move_type in ["out_invoice", "out_refund"]:
            return "Outgoing"
        return "Incoming"
