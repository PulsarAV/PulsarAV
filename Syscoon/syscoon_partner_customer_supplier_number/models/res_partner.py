# © 2023 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_number = fields.Char("Customer Number", company_dependent=True)
    supplier_number = fields.Char("Supplier Number", company_dependent=True)
