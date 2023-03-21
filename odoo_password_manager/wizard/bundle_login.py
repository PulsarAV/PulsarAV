# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError

EMPTY_PASSWORD_WARNING = _("The entered password is not correct!")


class bundle_login(models.TransientModel):
    """
    The wizard to enter password for this bundle
    """
    _name = "bundle.login"
    _description = "Passwords Bundle Log In"

    bundle_id = fields.Many2one("password.bundle", string="Bundle")
    password = fields.Char(string="Password", required=True)
    new_password = fields.Char(string="New Password")
    new_password_confirmation = fields.Char(string="New Password Confirmation")

    @api.model_create_multi
    def create(self, vals_list):
        """
        Re-write to check the bundle in case the wizard is shown without the footer
        """
        wizards = super(bundle_login, self).create(vals_list)
        if self._context.get("need_password_check"):
            for wizard in wizards:
                wizard.action_log_in()
        return wizards

    def action_log_in(self):
        """
        The method to log in into the bundle

        Methods:
         * action_login_bundle

        Extra info:
         * Expected singleton
        """
        if self.bundle_id and self.password:
            self.bundle_id.action_login_bundle(self.password)
        else:
            raise AccessError(EMPTY_PASSWORD_WARNING)

    def action_update_password(self):
        """
        The method to check credentials and trigger password update

        Methods:
         * action_login_bundle

        Extra info:
         * Check for new password / password confirmation validity is done on the password bundle level
         * Expected singleton
        """
        if not self.new_password or not self.new_password_confirmation:
            raise ValidationError(_("Please enter a new password and its confirmation"))

        if self.bundle_id and self.password:
            self.bundle_id.action_login_bundle(self.password)
            self.bundle_id.write({"password": self.new_password, "confirm_password": self.new_password_confirmation})
        else:
            raise AccessError(EMPTY_PASSWORD_WARNING)

    def action_update_bundle_key(self):
        """
        The method to check credentials and trigger key/salt update. That, in turn, launches password 
        encryption/decryption

        Methods:
         * _update_bundle_key

        Extra info:
         * Expected singleton
        """
        if self.bundle_id and self.password:
            self.bundle_id._update_bundle_key(self.password)
        else:
            raise AccessError(EMPTY_PASSWORD_WARNING)
