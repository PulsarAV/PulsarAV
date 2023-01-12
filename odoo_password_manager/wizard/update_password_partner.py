# -*- coding: utf-8 -*-

from odoo import fields, models


class update_password_partner(models.TransientModel):
    """
    The wizard to update partner of passwords in batch
    """
    _name = "update.password.partner"
    _inherit = "password.key.mass.update"
    _description = "Update Partner"

    partner_id = fields.Many2one("res.partner", string="New Partner")

    def _update_passwords(self, password_ids):
        """
        The method to prepare new vals for partner

        Args:
         * passwords_ids - password.key recordset
        """
        password_ids.write({"partner_id": self.partner_id.id})
