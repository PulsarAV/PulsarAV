# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from odoo.addons.odoo_password_manager.models.password_bundle import INCORRECT_CONFIRM_PASSWORD_WARNING, \
    INCORRECT_PASSWORD_WARNING

def get_sample_password_hash(checkkey):
    """
    The method to get some parts of the password to make a criteria to check the entered password further

    Args:
     * checkkey - str (always 32 symbols)

    Returns:
     * str
    """
    return checkkey[4:10] + checkkey[22:27]


class portal_password_bundle(models.Model):
    """
    The model to keep security settings for shared passwords

    #to-do: implement auto unlinking? or security?
    """
    _name = "portal.password.bundle"
    _inherit = ["password.node", "bundle.security.mixin", "portal.share.mixin", "mail.thread"]
    _description = "Shared Vault"

    @api.depends("portal_password_ids")
    def _compute_passwords_len(self):
        """
        Compute method for passwords_len
        """
        for portal_bundle in self:
            portal_bundle.passwords_len = len(portal_bundle.portal_password_ids)

    name = fields.Char(required=True)
    password = fields.Char(copy=False, required=True)
    confirm_password = fields.Char(copy=False, required=True)
    bundle_salt = fields.Text(string="Vault Salt", readonly=True, copy=False)
    bundle_key = fields.Text(string="Bundle Key", readonly=True, copy=False)
    checkkey = fields.Text(string="Check Key", readonly=True, copy=False)
    checksum = fields.Text(string="Checksum", readonly=True, copy=False)
    password_update_time = fields.Datetime(string="Password/Salt update time", readonly=True, copy=False)
    password_ids = fields.Many2many("password.key", string="Passwords")
    portal_password_ids = fields.One2many(
        "portal.password.key", "portal_password_bundle_id", string="Portal Passwords", readonly=True
    )
    passwords_len = fields.Integer(string="Passwords Number", compute=_compute_passwords_len, store=True)
    parent_id = fields.Many2one("portal.password.bundle", string="Parent bundle")
    child_ids = fields.One2many("portal.password.bundle", "parent_id", string="Child Bundles")

    def read(self, fields=None, load="_classic_read"):
        """
        Overwrite to:
         1. Force login to the bundle if the password is shown (so not for the list)
         2. Decrypt bundle passwords while reading.
         IMPORTANT: Applied only for internal users since decryption assumes an acccess to the bundle

        Methods:
         * _check_bundle_key of password.bundle
        """
        result = super(portal_password_bundle, self).read(fields=fields, load=load)
        if self.env.user.has_group("base.group_user"):
            for pw_dict in result:
                if pw_dict.get("password") or pw_dict.get("confirm_password"):
                    bundle_id = self.browse(pw_dict.get("id")).bundle_id
                    bundle_id._check_bundle_key()
                    try:
                        decrypted_password = bundle_id.decrypt_key(pw_dict.get("password"))
                        pw_dict.update({"password": decrypted_password, "confirm_password": decrypted_password})
                    except Exception as er:
                        pass
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overwrite to:
         1. Check that password and its confirmation are equal
         2. To generate salt, key, checksums, and decrypt passwords

        Methods:
         * _update_credentials
         * _update_portal_passwords
        """
        for vals in vals_list:
            password = vals.get("password")
            if password != vals.get("confirm_password"):
                raise ValidationError(INCORRECT_CONFIRM_PASSWORD_WARNING)
            bundle_id = self.env["password.bundle"].browse(vals.get("bundle_id"))
            vals.update(self._update_credentials(bundle_id, password))
        bundles = super(portal_password_bundle, self).create(vals_list)
        for bundle in bundles:
            bundle._update_portal_passwords()
        return bundles

    def write(self, vals):
        """
        Overwrite to:
         1. Check that password and its confirmation are equal
         2. To generate salt, key, checksums, and decrypt passwords

        Methods:
         * decrypt_key of password.bundle
         * _update_credentials
         * _update_portal_passwords
        """
        pw_bundle_object = self.env["password.bundle"]
        bundle_password = False
        res = True
        if (vals.get("bundle_id"), vals.get("password"), vals.get("confirm_password")).count(None) != 3:
            password = vals.get("password")
            if password != vals.get("confirm_password"):
                raise ValidationError(INCORRECT_CONFIRM_PASSWORD_WARNING)
            for portal_bundle in self:
                values = vals.copy()
                bundle_id = self.env["password.bundle"].browse(values.get("bundle_id") or portal_bundle.bundle_id.id)
                old_bundle_id = portal_bundle.bundle_id
                password = password or old_bundle_id.decrypt_key(portal_bundle.password)
                values.update(self._update_credentials(bundle_id, password))
                res = super(portal_password_bundle, portal_bundle).write(values)
                if not self._context.get("no_new_portal_passwords"):
                    portal_bundle._update_portal_passwords()
        elif vals.get("password_ids") is not None:
            res = super(portal_password_bundle, self).write(vals)
            for portal_bundle in self:
                portal_bundle._update_portal_passwords()
        else:
            res = super(portal_password_bundle, self).write(vals)
        return res

    def action_check_entered_password(self, password):
        """
        The method to check the entered password
        If it is correct > save it to the user session. Otherwise raise the access error
         1: @see #1 password.bundle > _update_session_bundles

        Args:
         * password - str

        Methods:
         * _decrypt_fernet of password.bundle

        Returns:
         * True

        Extra info:
         * Expected Singleton
        """
        bundle_hash = self.env["password.bundle"]._generate_bundle_hash(self.bundle_salt, self.bundle_key, password)
        bundle_description_key = self.env["password.bundle"]._decrypt_fernet(bundle_hash, self.bundle_key)
        checkkey = self.env["password.bundle"]._decrypt_fernet(self.checksum, bundle_description_key)
        if self.checkkey != get_sample_password_hash(checkkey):
            raise AccessError(INCORRECT_PASSWORD_WARNING)
        else:
            portal_vaults = request.session.get("portal_vaults") and request.session.get("portal_vaults").copy() or {}
            portal_vaults.update({self.id: {"last_login": fields.Datetime.now(), "vault_hash": bundle_hash}})
            request.session.update({
                "portal_vaults": portal_vaults,
                "po_bundle_last_update": fields.Datetime.now(), # 1 IMPORTANT
            })
        return True

    def action_clear_expired_vaults(self):
        """
        The method to check expired vauls and archive if any
        We use direct SQL update to avoid security checks
        """
        expired_ids = self.search([("valid_until", "!=", False), ("valid_until", "<", fields.Date.today())])
        if expired_ids:
            self.env.cr.execute(
                "UPDATE portal_password_bundle SET active = 'f' WHERE id IN %s", (tuple(expired_ids.ids),)
            )
            self.env.cr.commit()

    def _check_bundle_session(self):
        """
        The method to understand whether the current session hash is fine to decrypt passwords

        Returns:
         * False if the hash is obsolete, otherwise - str (the hash itslef)

        Extra info:
         * Expected singleton
        """
        today_now = fields.Datetime.now()

        def _clear_session():
            new_session_bundles = request.session.get("portal_vaults")
            new_session_bundles.update({self.id: {"last_login": last_login, "vault_hash": False}})
            request.session.update({
                "portal_vaults": new_session_bundles,
                "pw_bundle_last_update": today_now, # IMPORTANT; @see 1 password.bundle _update_session_bundles
            })
            return False

        session_vaults = request.session.get("portal_vaults")
        if not session_vaults or not session_vaults.get(self.id):
            # if no session > not correct hash
            return False
        vault_dict = session_vaults.get(self.id)
        last_login = vault_dict.get("last_login")
        if self.password_update_time and last_login < self.password_update_time:
            # if last bundle password update is after the last login > not correct hash
            return _clear_session()
        diff = (today_now - last_login).total_seconds() / 60
        session_len = self.session_length > 3 and self.session_length or 3
        if session_len < diff:
            # if session is expired > not correct hash
            return _clear_session()
        if not self.active:
            return _clear_session()
        return vault_dict.get("vault_hash")

    @api.model
    def _update_credentials(self, bundle_id, password):
        """
        The method to prepare the values for the updated portal bundle
         1. Encrypt portal bundle password with bundle password. It is done the same as for ordinary password keys.
         IMPORTANT: in this way, in the backend we always have an access to original vault password, while it is
         never stored in the database
         2. Save a sample password to check the password validity in the portal
         IMPORTANT: we save only parts of the generated password, so it will not give more clues to brootforce.
         Even if the db is accessed, the checkkey will contain only part of the decrypted from checksum. In the exreme
         rare worst case of wrong compared checkkey equals the real one, a portal user will just be shown not correctly
         encrypted passwords

        Args:
         * bundle_id - password.bundle object
         * password - str

        Methods:
         * encrypt_key of password.bundle
         * _generate_new_bundle_salt of password.bundle
         * _generate_new_bundle_key of password.bundle
         * _encrypt_fernet of password.bundle
         * _generate_bundle_hash
         * _decrypt_fernet

        Returns:
         * dict
        """
        encrypted_password = bundle_id.encrypt_key(password)
        bundle_key = bundle_id._generate_new_bundle_key()
        bundle_salt = bundle_id._generate_new_bundle_salt()
        checkkey = bundle_id._generate_new_bundle_salt() + bundle_id._generate_new_bundle_salt() # 32 symbols
        bundle_hash = bundle_id._generate_bundle_hash(bundle_salt, bundle_key.decode(), password)
        bundle_description_key = bundle_id._decrypt_fernet(bundle_hash, bundle_key.decode())
        checksum = bundle_id._encrypt_fernet(checkkey, bundle_description_key)
        return {
            "password": encrypted_password,
            "confirm_password": encrypted_password,
            "bundle_salt": bundle_salt,
            "bundle_key": bundle_key,
            "checkkey": get_sample_password_hash(checkkey),
            "checksum": checksum,
            "password_update_time": fields.Datetime.now(),
        }

    def _update_portal_passwords(self):
        """
        The method create/update portal.password.key to encrypt its password using portal bundle salt and password
        IMPORTANT: @see portal_password_key _compute_password & related attribute
        We just unlink old portal passwords even if they exist for simplicity

        Extra info:
         * Expected singleton
        """
        portal_passwords_vals_list = []
        for password_key in self.password_ids:
            if password_key.bundle_id != self.bundle_id:
                continue
            portal_passwords_vals_list.append({"portal_password_bundle_id": self.id, "password_id": password_key.id})
        self.portal_password_ids.unlink()
        self.env["portal.password.key"].create(portal_passwords_vals_list)

    def action_update_nodes(self, node):
        """
        The method to update record after d&d

        Args:
         * node - str (nodex_)

        Extra info:
         * We are in try/except to make sure that an excess node is removed
         * Expected singleton
        """
        try:
            node_int = int(node[6:])
            node_id = self.env["password.key"].browse(node_int).exists()
            if self.exists() and node_id:
                if node_int not in self.password_ids.ids:
                    pw_values = [(4, node_int)]
                    self.write({"password_ids": pw_values})
        except:
            pass
