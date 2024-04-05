# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    """Extend res.company to add financeinterface fields"""

    _inherit = "res.company"

    export_finance_interface = fields.Selection(
        selection=[("none", "None")], default="none"
    )
    export_finance_interface_active = fields.Boolean()

    def create_financeinterface_sequence(self):
        """Create a new no_gap entry_sequence for financeinterface"""
        return self.env["ir.sequence"].create(
            {
                "name": f"Financeinterface sequence for {self.name}",
                "prefix": f"EXTF_{self.id}",
                "implementation": "no_gap",
                "code": "syscoon.financeinterface.sequence",
                "padding": 8,
                "number_next": 1,
                "number_increment": 1,
                "company_id": self.id,
            }
        )

    def _check_existing_sequence(self):
        """Check if there is already a sequence for financeinterface"""
        sequence_id = self.env["ir.sequence"].search(
            [
                ("code", "=", "syscoon.financeinterface.sequence"),
                ("company_id", "=", self.id),
            ]
        )
        if not sequence_id:
            sequence_id = self.create_financeinterface_sequence()
        return sequence_id
