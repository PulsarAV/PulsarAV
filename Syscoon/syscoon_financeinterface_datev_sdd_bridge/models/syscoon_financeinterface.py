# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class SyscoonFinanceinterface(models.Model):
    _inherit = 'syscoon.financeinterface'

    def generate_rewe_partner(self, partner_id, number, template):
        template, account_id = super().generate_rewe_partner(
            partner_id, number, template
        )
        template["Lastschrift"] = "9"
        sdd_count = 1
        for sdd in partner_id.sdd_mandate_ids:
            if sdd_count > 10:
                continue
            if sdd.state == 'active':
                template['SEPA-Mandatsreferenz %s' % sdd_count] = sdd.name or ''
                sdd_count += 1
                template['Lastschrift'] = '8'
        return template, account_id

    def generate_export_line(self, export_line, line):
        export_line, group = super().generate_export_line(export_line, line)
        export_line["SEPA-Mandatsreferenz"] = line.move_id.sdd_mandate_id.name or ""
        return export_line, group
