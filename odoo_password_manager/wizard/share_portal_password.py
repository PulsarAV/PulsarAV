# -*- coding: utf-8 -*-

from odoo import api, fields, models


class share_portal_password(models.TransientModel):
    """
    The wizard to update partner of passwords in batch
    """
    _name = "share.portal.password"
    _inherit = ["password.key.mass.update", "portal.share.mixin"]
    _description = "Share in Portal"

    vault_method = fields.Selection(
        [("new_vault", "Create a new portal vault"), ("existing_vault", "Add to an existing portal vault")],
        string="Sharing",
        required=True,
        default="new_vault",
    )
    vault_id = fields.Many2one("portal.password.bundle", string="Portal Vault", required=False)
    send_invitation = fields.Boolean(string="Send Invitation")

    def _update_passwords(self, password_ids):
        """
        The method to prepare new vals for partner

        Args:
         * passwords_ids - password.key recordset

        Methods:
         * _return_values_dict of portal.share.mixin
        """
        if self.vault_method == "new_vault":
            values = self._return_values_dict()
            values.update({"password_ids": [(6, 0,  password_ids.ids)]})
            new_vault_id = self.env["portal.password.bundle"].create([values])
            if self.send_invitation and self.partner_ids:
                template = self.env.ref("odoo_password_manager.portal_vault_invitation")
                message = template._render_template_qweb(
                    template.body_html, "portal.password.bundle", [new_vault_id.id]
                ).get(new_vault_id.id)
                new_vault_id.message_post(body=message, partner_ids=self.partner_ids.ids)
        else:
            pw_values = [(4, pw.id) for pw in password_ids if pw not in self.vault_id.password_ids]
            self.vault_id.write({"password_ids": pw_values})
