# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import logging
import os
import re
import shutil
import zipfile
from collections import namedtuple
from functools import partial
from itertools import chain

import PyPDF2
from lxml import etree
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SyscoonFinanceinterface(models.Model):
    """Inherits the basic class to provide the export for DATEV ASCII"""

    _inherit = "syscoon.financeinterface"

    mode = fields.Selection(
        selection_add=[("datev_xml", "DATEV XML")],
        ondelete={"datev_xml": lambda recs: recs.write({"mode": "none"})},
    )
    xml_mode = fields.Selection(
        [("standard", "Standard"), ("extended", "Extended"), ("bedi", "BEDI Link")],
        string="XML-Export Methode",
        help="Export Methode: Standard: without Accounts, Extended: with Accounts",
    )

    def export(self, mode=False, date_from=False, date_to=False, args=False):
        """Method that generates the export by the given parameters"""
        export_id = super().export(mode, date_from, date_to, args)
        if mode != "datev_xml":
            return export_id
        invoice_mode = args[0]
        invoice_selection = args[1]
        invoice_type = []
        export_id.write({"xml_mode": invoice_mode})
        if invoice_selection in ["customers", "both"]:
            invoice_type.extend(["out_invoice", "out_refund"])
        if invoice_selection in ["vendors", "both"]:
            invoice_type.extend(["in_invoice", "in_refund"])
        move_domain = [
            ("invoice_date", ">=", date_from),
            ("invoice_date", "<=", date_to),
            ("move_type", "in", invoice_type),
            ("state", "=", "posted"),
        ]
        if invoice_mode != "bedi":
            move_domain.append(("export_id", "=", False))
        moves = self.env["account.move"].search(move_domain)
        if not moves:
            raise UserError(
                _("There are no invoices to export in the selected date range!")
            )
        export_vals = self.generate_export_invoices(invoice_mode, moves, export_id)
        if export_vals["doc_paths"] and export_vals["moves_ok"]:
            zip_file = self.make_zip_file(
                export_vals["export_path"],
                export_vals["doc_paths"],
                export_vals["export_time"],
                invoice_mode,
            )
            self._create_export_file_attachment(
                export_id, zip_file, invoice_mode, export_vals
            )
        return export_id

    def _create_export_file_attachment(
        self, export_id, zip_file, invoice_mode, export_vals
    ):
        if not zip_file:
            return
        attachment = self.env["ir.attachment"].create(
            {
                "name": "%s.zip" % (export_id.name),
                "store_fname": "%s.zip" % (export_id.name),
                "res_model": "syscoon.financeinterface",
                "res_id": export_id.id,
                "type": "binary",
                "datas": base64.b64encode(zip_file),
            }
        )
        if invoice_mode != "bedi":
            export_vals["moves_ok"].write({"export_id": export_id.id})
        if export_vals["move_errors"] and invoice_mode != "bedi":
            errors = self.env["account.move"].browse(export_vals["move_errors"])
            export_vals["move_errors"] = errors
            export_vals["move_errors"].write({"export_id": False})
        if os.path.exists(export_vals["export_path"]):
            shutil.rmtree(export_vals["export_path"])
        return attachment

    def generate_export_invoices(self, invoice_mode, moves, export_id):
        """Generates a list of dicts which have all the exportlines to
        datev"""

        def clean_move_number(move):
            """
            Return a cleaned invoice
            number consisting only of
            alphanumeric characters
            """
            return ''.join(re.findall(r'\w+', move.name or ''))

        export_time = fields.Datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        move_xmls = []
        move_errors = []
        moves_with_xml = []
        for move in moves:
            xml = self.get_invoice_xml(move, invoice_mode, export_id)
            if xml:
                move_xmls.append(xml)
                moves_with_xml.append(move.id)
            else:
                move_errors.append(move.id)
        moves_ok = self.env['account.move'].browse(moves_with_xml)
        invoice_pdfs = map(self.get_invoice_pdf, moves_ok)
        move_numbers = moves_ok.mapped(clean_move_number)
        move_ids = moves_ok.ids
        invoice_docs = filter(all, zip(move_ids, move_numbers, move_xmls, invoice_pdfs))
        export_path = self.get_export_dir_path()
        docs = map(partial(self.write_export_invoice, export_path), invoice_docs)
        doc_paths = self.write_docs(docs, export_time, export_path, invoice_mode)
        return {
            "doc_paths": doc_paths,
            "export_path": export_path,
            "export_time": export_time,
            "move_errors": move_errors,
            "moves_ok": moves_ok,
        }

    def get_export_dir_path(self):
        """ Check if temporary directory exists for buffering documents before zipping it """
        path = '/tmp/odoo/datev_xml_export'
        if not os.path.exists(path) or not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
        return path

    def get_invoice_pdf(self, move):
        """ Return the PDF report for a given invoice """
        content = False
        report = namedtuple('Report', ['content', 'filetype'])
        datas = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', move.id),
            ('mimetype', '=', 'application/pdf'),
        ], order='id asc')
        if datas:
            content, filetype = self.merge_pdf(datas, move)
        else:
            content, filetype = self.env["ir.actions.report"]._render_qweb_pdf(
                "account.account_invoices", [move.id]
            )
        report_make = report._make((content, filetype))
        return report_make

    def get_invoice_xml(self, move_id, invoice_mode, export_id):
        """ Return the XML Export for a given invoice """
        errors = []
        vnote = ""
        schema = etree.parse(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "schemas/Belegverwaltung_online_invoice_v050.xsd",
            )
        )
        schema = etree.XMLSchema(schema)
        parser = etree.XMLParser(schema=schema, encoding="utf-8")
        xml = self.env["syscoon.financeinterface.xml"].create_invoice_xml(
            move_id, invoice_mode
        )
        try:
            etree.fromstring(xml, parser)
        except (etree.XMLSyntaxError, ValueError) as e:
            errors.append(self.get_error_msg(move_id))
            for arg in e.args:
                errors.append(arg)
            if export_id.log:
                vnote = export_id.log
                vnote += '\n'.join(errors)
                vnote += '\n'
            else:
                vnote = '\n'.join(errors)
                vnote += '\n'
            export_id.write({
                'log': vnote,
            })
            return False
        return xml

    def write_export_invoice(self, dir_path, inv_doc):
        """
        Either both files are written or neither.
        """
        inv_id, name, xml, report = inv_doc

        xml_path = os.path.join(dir_path, name + '.xml')
        pdf_path = os.path.join(dir_path, '.'.join([name, report.filetype]))
        try:
            with open(xml_path, "w") as file:
                xml = xml.decode(encoding="utf-8", errors="strict")
                file.write(xml)
            with open(pdf_path, "wb") as file:
                file.write(report.content)
            return (inv_id, name, xml_path, pdf_path)
        except Exception:
            _logger.error(
                _(f"An error occurred while saving {name} export in {dir_path}")
            )
            if os.path.exists(xml_path):
                os.remove(xml_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            raise

    def write_export(self, dir_path, inv_doc):
        """
        Either both files are written or neither.
        """
        inv_id, name, xml, report = inv_doc

        xml_path = os.path.join(dir_path, name + '.xml')
        pdf_path = os.path.join(dir_path, '.'.join([name, report.filetype]))
        try:
            with open(xml_path, "w") as file:
                xml = xml.decode(encoding="utf-8", errors="strict")
                file.write(xml)
            with open(pdf_path, "wb") as file:
                file.write(report.content)
            return (inv_id, name, xml_path, pdf_path)
        except Exception:
            _logger.error(
                _(f"An error occurred while saving {name} export in {dir_path}")
            )
            if os.path.exists(xml_path):
                os.remove(xml_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            raise

    @api.model
    def write_docs(self, docs, timestamp, dir_path, invoice_mode):
        """
        Consumes the docs generator and additionally
        writes an xml file with info of the made exports
        """
        WrittenDoc = namedtuple(
            'WrittenDoc', ['inv', 'name', 'xml_path', 'pdf_path'])

        def get_doc_paths(doc):
            return dir_path + '/' + doc.pdf_path, dir_path + '/' + doc.xml_path

        written_docs = []
        inv_documents_xml_path = False
        try:
            for move_id, name, xml_path, pdf_path in docs:
                inv = self.env["account.move"].browse(move_id)
                xp = xml_path.replace(dir_path + "/", "")
                pp = pdf_path.replace(dir_path + "/", "")
                written_docs.append(WrittenDoc._make((inv, name, xp, pp)))
                _logger.info(_("%s has been exported" % name))
                _logger.info(xml_path)
                _logger.info(pdf_path)
                export_info_xml = self.get_documents_xml(
                    written_docs, timestamp, invoice_mode
                )
                inv_documents_xml_path = self.write_export_invoice_info(
                    dir_path, export_info_xml, timestamp
                )
            return filter(
                None,
                chain((inv_documents_xml_path,), *map(get_doc_paths, written_docs)),
            )
        except Exception as e:
            raise UserError(_("Something went wrong: %s " % e))

    def get_error_msg(self, move_id):
        return _(f"{move_id.name} (id={move_id.id}) could not be exported: ")

    def make_zip_file(self, export_path, doc_path, timestamp, invoice_mode):
        zip_path = os.path.join(export_path, timestamp + ".zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as file:
            for path in doc_path:
                if invoice_mode == "bedi":
                    if ".xml" not in path or "document.xml" in path:
                        file.write(path, os.path.basename(path))
                else:
                    file.write(path, os.path.basename(path))

        datas_content = ""
        with open(zip_path, "rb") as datas_file:
            datas_content = datas_file.read()
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return datas_content

    def get_documents_xml(self, docs, timestamp, invoice_mode):
        """ Return the XML Export for a given invoice """
        errors = []
        vnote = ""
        schema = etree.parse(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "schemas/Document_v050.xsd",
            )
        )
        schema = etree.XMLSchema(schema)
        parser = etree.XMLParser(schema=schema, encoding="utf-8")
        xml = self.env["syscoon.financeinterface.xml"].create_documents_xml(
            docs, timestamp, invoice_mode
        )
        try:
            etree.fromstring(xml, parser)
            return xml
        except Exception as e:
            errors.append('documents.xml')
            for arg in e.args:
                errors.append(arg)
            if self.log:
                vnote = self.log
                vnote += '\n'.join(errors)
                vnote += '\n'
            else:
                vnote = '\n'.join(errors)
                vnote += '\n'
            self.write({
                'log': vnote,
            })
            return

    def write_export_invoice_info(self, dir_path, xml, timestamp):
        xml_path = os.path.join(dir_path, 'document.xml')
        if not xml:
            return
        try:
            with open(xml_path, "w") as file:
                file.write(xml.decode("utf-8"))
            return xml_path
        except Exception:
            _logger.error(
                _(f"An error occurred while saving {timestamp} export in {dir_path}")
            )
            if os.path.exists(xml_path):
                os.remove(xml_path)
            raise

    def merge_pdf(self, datas, inv):
        """
        concentrate pdf's if the number of the attachments is > 1
        otherwise use odoo standard for reading the pdf
        """
        base64fname = False
        if len(datas) > 1:
            merger = PyPDF2.PdfFileMerger(strict=False)
            myio = io.BytesIO()
            for pdf in datas:
                if base64fname and base64fname == pdf.store_fname:
                    continue
                base64fname = pdf.store_fname
                attach = pdf._file_read(pdf.store_fname)
                content = io.BytesIO(attach)
                try:
                    merger.append(content, import_bookmarks=False)
                except Exception:
                    raise UserError(
                        _(
                            "Export stopped! \n Invoice %s can not exported, because the "
                            "PDF has no EOF-Marker. \n Please repair it and start "
                            "the export again." % inv.name
                        )
                    )
            merger.write(myio)
            merger.close()
            content, filetype = myio.getvalue(), 'pdf'
        else:
            attach = datas._file_read(datas.store_fname)
            content, filetype = attach, "pdf"
        return content, filetype
