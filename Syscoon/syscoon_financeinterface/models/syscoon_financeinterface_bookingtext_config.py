# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SyscoonFinanceinterfaceBookingtextConfig(models.Model):
    """This class provides parameters for the configuration of the creation of the bookingtext"""

    _name = "syscoon.financeinterface.bookingtext.config"
    _description = "syscoon Financial Interface Config for the Bookingtext"
    _order = "sequence asc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    sequence = fields.Integer(default=10)
    name = fields.Char(compute="_compute_name", store=True)
    journal_id = fields.Many2one("account.journal")
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
