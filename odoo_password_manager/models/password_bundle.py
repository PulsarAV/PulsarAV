# -*- coding: utf-8 -*-

import base64
import logging
import os

import passlib.context

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError as e:
    _logger.error(e)

CRYPT_CONTEXT = passlib.context.CryptContext(["pbkdf2_sha512"],)
INCORRECT_PASSWORD_WARNING = _("The entered password is not correct")
BUNDLE_ENCRYPTION_WARNING = _("Bundle password cannot be encrypted. Please try to refresh the page")
BUNDLE_SALT_ERROR = _("The bundle salt was not updated. Please try to refresh the page")
INCORRECT_CONFIRM_PASSWORD_WARNING = _("The password and its confirmation are not equal!")


class password_bundle(models.Model):
    """
    The model to manage passwords bundle (vaults)
    """
    _name = "password.bundle"
    _inherit = ["bundle.security.mixin"]
    _description = "Passwords Bundle"

    @api.model
    def _default_access_ids(self):
        """
        Default method for access_ids
        """
        values = {"user_id": self.env.user.id, "access_level": "admin"}
        return [(0, 0, values)]

    @api.depends("passwords_ids")
    def _compute_passwords_count(self):
        """
        Compute method for passwords_count
        """
        for bundle in self:
            bundle.passwords_count = len(bundle.passwords_ids)

    def _compute_has_read_right_to(self):
        """
        Compute method for has_read_right_to and has_full_right_to
        """
        current_user = self.env.user
        groups = current_user.groups_id
        self = self.sudo()
        r_bundles = self.env["password.access"]._return_all_bundles(current_user, modes=["readonly", "full", "admin"])
        w_bundles = self.env["password.access"]._return_all_bundles(current_user, modes=["full", "admin"])
        a_bundles = self.env["password.access"]._return_all_bundles(current_user, modes=["admin"])
        for bundle in self:
            bundle.has_read_right_to = bundle in r_bundles and [(6, 0, [current_user.id])] or False
            bundle.has_full_right_to = bundle in w_bundles and [(6, 0, [current_user.id])] or False
            bundle.has_admin_right_to = bundle in a_bundles and [(6, 0, [current_user.id])] or False

    @api.model
    def search_has_read_right_to(self, operator, value):
        """
        Search method for has_read_right_to

        Methods:
         * _return_all_bundles of password.access

        Returns:
         * RPN domain
        """
        current_user = self.env["res.users"].browse(value)
        groups = current_user.groups_id
        self = self.sudo()
        bundles = self.env["password.access"]._return_all_bundles(current_user, modes=["readonly", "full", "admin"])
        return [("id", "in", bundles.ids)]

    @api.model
    def search_has_full_right_to(self, operator, value):
        """
        Search method for has_full_right_to

        Methods:
         * _return_all_bundles of password.access

        Returns:
         * RPN domain
        """
        current_user = self.env.user.browse(value)
        groups = current_user.groups_id
        self = self.sudo()
        bundles = self.env["password.access"]._return_all_bundles(current_user, modes=["full", "admin"])
        return [("id", "in", bundles.ids)]

    @api.model
    def search_has_admin_right_to(self, operator, value):
        """
        Search method for search_has_admin_right_to

        Methods:
         * _return_all_bundles of password.access

        Returns:
         * RPN domain
        """
        current_user = self.env.user.browse(value)
        groups = current_user.groups_id
        self = self.sudo()
        bundles = self.env["password.access"]._return_all_bundles(current_user, modes=["admin"])
        return [("id", "in", bundles.ids)]

    def _inverse_active(self):
        """
        Inverse method for active
        """
        for bundle in self:
            if not bundle.active:
                passwords = self.env["password.key"].search([("bundle_id", "=", bundle.id)])
                passwords.write({"active": False})

    @api.constrains("extra_password_security", "session_length")
    def _check_extra_password_security(self):
        """
        Constraint to make session length long enough
        """
        for bundle in self:
            if bundle.extra_password_security and bundle.session_length < 3:
                raise ValidationError(_("The session should last at least 3 minutes"))

    name = fields.Char(string="Name")
    passwords_ids = fields.One2many("password.key", "bundle_id", string="Passwords")
    passwords_count = fields.Integer(
        string="Passwords Count",
        compute=_compute_passwords_count,
        store=True,
    )
    tag_ids = fields.One2many("password.tag", "bundle_id", string="Available tags")
    access_ids = fields.One2many(
        "password.access",
        "bundle_id",
        string="Access Levels",
        copy=True,
        help="""Bundles
A user may access (read) the passwords bundle: 
 (a) if this user is its creator; 
 (b) if this user has any access level.
A user may create, update (including change of extra bundle password) or delete the passwords bundle: 
 (a) if this user is its creator;
 (b) this user has the "Administrator" access level.

Passwords
A user may access (read) the password: 
 (a) if this user is the linked bundle creator; 
 (b) if this user has any access level to the linked bundle.
A user may create, update or delete a password: 
 (a) if this user is the linked bundle creator; 
 (b) if this user has the "Full rights" access level to the linked bundle.

Tags
A user may access password tags:
 (a) if this user is the linked bundle creator;
 (b) if this user has any access level to the linked bundle;
 (c) if a password tag does not have a linked bundle.
A user may create, update or delete password tags: 
 (a) if this user is the linked bundle creator; 
 (b) if this user has the "Full rights" access level to the linked bundle;
 (c) if a password tag does not have a linked bundle.
""",
        default=_default_access_ids,
    )
    has_read_right_to = fields.Many2many(
        "res.users",
        "res_users_password_bundle_rel_table_readonly",
        "res_users_id",
        "password_bundle_id",
        string="Current user has read rights to this bundle",
        compute=_compute_has_read_right_to,
        search=search_has_read_right_to,
    )
    has_full_right_to = fields.Many2many(
        "res.users",
        "res_users_password_bundle_rel_table_full",
        "res_users_id",
        "password_bundle_id",
        string="Current user has write rights to this bundle",
        compute=_compute_has_read_right_to,
        search=search_has_full_right_to,
    )
    has_admin_right_to = fields.Many2many(
        "res.users",
        "res_users_password_bundle_rel_table_admin",
        "res_users_id",
        "password_bundle_id",
        string="Current user has full right to this bundle",
        compute=_compute_has_read_right_to,
        search=search_has_admin_right_to,
    )
    extra_password_security = fields.Boolean(
        string="Extra password to open this bundle",
        help="If turned on, users will have to enter a paraphrase before accessing passwords or changing this bundle. \
This paraphrase is not kept in the database and it is used in password encryption. BE CAUTIOUS: if you forgot the \
paraphrase you will LOSE password data. Paraphrase is hashed and can't be recovered by any user disregarding his/her \
access levels.",
    )
    extra_password_setup = fields.Boolean(string="Extra password is set up")
    password = fields.Char(string="Bundle Password", copy=False)
    confirm_password = fields.Char(string="Confirm Bundle Password", copy=False)
    password_update_time = fields.Datetime(
        string="Password/Salt update time",
        readonly=True,
        copy=False,
    )
    session_length = fields.Integer(string="Max Session Length (Minutes)", default=60)
    bundle_key = fields.Text(string="Bundle Key", readonly=True, copy=False)
    bundle_salt = fields.Text(string="Bundle Salt", readonly=True, copy=False)
    update_policy = fields.Integer(
        string="Update frequency (days)",
        help="If set to positive number, Odoo will automatically generate activities to update passwords once in this \
number of days",
    )
    notes = fields.Html(string="Notes")
    active = fields.Boolean(string="Active", default=True, inverse=_inverse_active)
    color = fields.Integer(string="Color Index")

    def init(self):
        """
        Re-write to encrypt passwords (the method is copied from res.users)
         allow setting plaintext passwords via SQL and have them automatically encrypted at startup: look for passwords
         which don't match the "extended" MCF and pass those through passlib.
         Alternative: iterate on *all* passwords and use CryptContext.identify
        """
        cr = self.env.cr
        cr.execute("""
        SELECT id, password FROM password_bundle
        WHERE password IS NOT NULL
          AND password !~ '^\$[^$]+\$[^$]+\$.'
        """)
        if self.env.cr.rowcount:
            bundles = self.sudo()
            for uid, pw in cr.fetchall():
                bundles.browse(uid).write({"password": pw, "confirm_password": pw})

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overwrite to:
         1. encrypt bundle password if it or security type are changed (_set_encrypted_bundle_password)
         2. generate new bundle key and salt
         3. log in to the password using a new key (_update_session_bundles)

        Methods:
         * _set_encrypted_bundle_password
         * _generate_new_bundle_key
         * _generate_new_bundle_salt
         * _update_session_bundles
        """
        bundle_ids = self.env["password.bundle"]
        for values in vals_list:
            password = values.get("password")
            confirm_password = values.get("confirm_password")
            extra_security = values.get("extra_password_security")
            bundle_password = self._set_encrypted_bundle_password(password, confirm_password, extra_security)
            extra_security = bundle_password and True or False
            values.update({
                "password": bundle_password,
                "confirm_password": bundle_password,
                "extra_password_security": extra_security,
                "extra_password_setup": extra_security,
                "bundle_key": self._generate_new_bundle_key(),
                "bundle_salt": self._generate_new_bundle_salt(),
            })   
            # bundle is created really not often, so for the goals of clean code, we prefer to make a single create
            bundle_id = super(password_bundle, self).create([values])
            if bundle_password:
                bundle_id._update_session_bundles(password, True)
            bundle_ids += bundle_id
        return bundle_ids

    def write(self, values):
        """
        Overwrite to:
         1. encrypt bundle password if it or security type are changed (_set_encrypted_bundle_password)
         2. log in to the password using a new key (_update_session_bundles)
         3. decrypt password keys using previous bundle key/salt, and encrypt using a new one (_refresh_bundle_keys)

        Methods:
         * _set_encrypted_bundle_password
         * _get_bundle_key
         * _update_session_bundles
         * _refresh_bundle_keys
        """
        password = values.get("password")
        confirm_password = values.get("confirm_password")
        extra_security = values.get("extra_password_security")
        if password is not None or confirm_password is not None or extra_security is not None:
            for bundle in self:
                bundle_real_security = previous_security = bundle.extra_password_security
                if extra_security is not None:
                    bundle_real_security = extra_security
                # this assumes that either the password is known or it is False
                bundle_password = self._set_encrypted_bundle_password(password, confirm_password, bundle_real_security)
                values.update({
                    "password": bundle_password,
                    "confirm_password": bundle_password,
                    "extra_password_security": bundle_password and True or False,
                    "extra_password_setup": bundle_password and True or False,
                })
                old_bundle_key = bundle._get_bundle_key()
                res = super(password_bundle, bundle.with_context(no_pwm_security=not previous_security)).write(values)
                if bundle_password:
                    bundle._update_session_bundles(password, True)
                bundle._refresh_bundle_keys(old_bundle_key)
        else:
            # if not password or extra security change > just write values
            res = super(password_bundle, self).write(values)
        return res

    def action_login_bundle(self, password):
        """
        The method to login and update session

        Args:
         * password - char - password to check

        Methods:
         * _update_session_bundles

        Returns:
         * bool: true if verification is succesfull
         * Raises AccessError otherwise

        Extra info:
         * Expected singleton
         * session_bundles format: {1: datetime.datetime}
        """
        if not password:
            raise AccessError(INCORRECT_PASSWORD_WARNING)
        self.env.cr.execute("SELECT COALESCE(password, '') FROM password_bundle WHERE id=%s", [self.id])
        [hashed] = self.env.cr.fetchone()
        valid = CRYPT_CONTEXT.verify(password, hashed)
        if valid:
            self._update_session_bundles(password)
        else:
            raise AccessError(INCORRECT_PASSWORD_WARNING)
        return valid

    def action_update_bundle_password(self):
        """
        The method to launch password update

        Extra info:
         * Expected singleton
        """
        res = True
        if self.extra_password_security:
            res = self.sudo().env.ref("odoo_password_manager.bundle_login_password_action_update").read()[0]
        return res

    def action_update_bundle_key(self):
        """
        The method to launch salt/key update
        In case a bundle is protected by the password > launch login wizard to learn that password

        Method:
         * _update_bundle_key

        Extra info:
         * Expected singleton
        """
        res = True
        if self.extra_password_security:
            res = self.sudo().env.ref("odoo_password_manager.bundle_login_password_action_action").read()[0]
        else:
            self._update_bundle_key()
        return res

    @api.model
    def action_return_all_active_bundles(self):
        """
        The method to retrieve all bundles of active user for "all passwords"

        Returns:
         * list of ints
        """
        return self.search([]).ids

    @api.model
    def _set_encrypted_bundle_password(self, password, confirm_password, extra_password_security):
        """
        The method to encrypt BUNDLE password to the database
        The method assumes clearing passwords if extra security is not needed (to avoid their further double decryption)
    
        Args:
         * password - char (not yet encrypted password)
         * confirm_password - char (not yet encrypted password)
         * extra_password_security - boolean - whether password should be checked

        Methods: 
         * _encrypt_bundle_password

        Returns:
         * char
        """
        bundle_password = False
        if extra_password_security and password:
            if password != confirm_password:
                raise ValidationError(INCORRECT_CONFIRM_PASSWORD_WARNING)
            bundle_password = self._encrypt_bundle_password(password)
        return bundle_password       

    @api.model
    def _encrypt_bundle_password(self, password):
        """
        The method to encrypt bundle password

        Args:
         * password - str (not encrypted password)

        Returns:
         * str
        """
        try:
            encrypted_bundle_password = CRYPT_CONTEXT.hash(password)
        except Exception as er:
            _logger.error("Bundle password was not hashed: {}".format(er))
            try:
                encrypted_bundle_password = CRYPT_CONTEXT.encrypt(password) # to the case of obsolete Python lib
            except Exception as er2:
                _logger.error("Bundle password was not encrypted: {}".format(er2))
                raise ValidationError(BUNDLE_ENCRYPTION_WARNING)
        if CRYPT_CONTEXT.identify(encrypted_bundle_password) == "plaintext":
            raise ValidationError(BUNDLE_ENCRYPTION_WARNING)
        if encrypted_bundle_password == password:
            raise ValidationError(BUNDLE_ENCRYPTION_WARNING)
        return encrypted_bundle_password

    @api.model
    def _generate_new_bundle_salt(self):
        """
        The method to prepare a new bundle salt (salt&password = key)

        Returns:
         * str
        """
        try:
            bundle_salt = base64.b64encode(os.urandom(16)).decode("utf-8")
        except Exception as er:
            _logger.error("Bundle salt was not generated: {}".format(er))
            raise ValidationError(BUNDLE_SALT_ERROR)
        return bundle_salt

    @api.model
    def _generate_new_bundle_key(self):
        """
        The method to prepare a new bundle key 

        Returns:
         * str
        """
        try:
            bundle_key = Fernet.generate_key()
        except Exception as er:
            _logger.error("Bundle key was not generated: {}".format(er))
            raise ValidationError(BUNDLE_SALT_ERROR)
        return bundle_key

    def _update_bundle_key(self, password=None):
        """
        The method to generate a new key to encrypt/decrypt passwods
        In case there are passwords they should be decrypted with old key and encrypted with a new one
        IMPROTANT: if there bundle is secured with an extra password, to decrypt keys we use salted password.   

        Args:
         * password - char

        Methods:
         *  action_login_bundle
         * _get_bundle_key
         * _generate_new_bundle_salt
         * _generate_new_bundle_key
         * _update_session_bundles
         * _refresh_bundle_keys
        
        Extra info:
         * Expecteds singleton
        """
        if password:
            # check firstly the rights, and update the session
            self.action_login_bundle(password) 
        try:
            old_bundle_key = self._get_bundle_key()
            self.bundle_salt = self._generate_new_bundle_salt()
            self.bundle_key = self._generate_new_bundle_key()
            if password:
                # need to refresh session again since salt is changed
                self._update_session_bundles(password)
            self._refresh_bundle_keys(old_bundle_key)
            self.password_update_time = fields.Datetime.now()
        except Exception as er:
            raise ValidationError(_("The encryption key and salt can't be updated: {}".format(er)))

    def _get_bundle_key(self):
        """
        The method to get bundle key from session

        Methods:
         * _decrypt_fernet

        Returns:
         * str

        Extra info:
         * We check for existing bundle salt to prior versions compatibility (so when there was extra_password_security
           but keys are decrypted without salt)
         * In each 'key get' we should decrypt
         * We do not clear cache here to avoid too frequent requests, it is already done in each write,create,unlink
           and read
         * We cannot safe mere bundle_key to the session since there is no moment when it can be saved there. 
         * Expected singleton
        """
        bundle_decryption_key = self.bundle_key
        if self.extra_password_security and self.bundle_salt:
            session_bundles = request.session.get("pw_bundles") or {}
            this_bundle_session = session_bundles.get(self.id)
            if this_bundle_session and this_bundle_session.get("bundle_hash"):
                bundle_decryption_key = this_bundle_session.get("bundle_hash")
                bundle_decryption_key = self._decrypt_fernet(bundle_decryption_key, self.bundle_key)
            else:
                raise AccessError(_("The session is expired. Please refresh the page and log in to the bundle"))
        return bundle_decryption_key

    def _update_session_bundles(self, password, password_change=None):
        """
        The method to add current bundle to session. So, to keep last_login datetime and if bundle key is derived
        from password 

        1. EXTREMELY IMPORTANT: starting from v.16, session is somehow cached, and for UNCLEAR REASONS update done
        in this method is not applied. Adding an extra parameter to session update FOR UNCLEAR RASONS solve that.
        Perhaps, it is somehow connected with dict cache

        Args:
         * password -  password to prepare and generate bundle key
         * password_change - whether the password has been changed

        Methods:
         * _encrypt_fernet

        Extra info:
         * Bundle hash is encrypted with public key, so in the session it is kept in encrypted way
         * We check for existing bundle salt to prior versions compatibility (so when there was extra_password_security
           but keys are decrypted without salt)
         * Expected singleton
        """
        bundle_hash = False
        if self.extra_password_security and self.bundle_salt:
            bundle_salt = base64.b64decode(self.bundle_salt.encode("utf-8"))
            decoded_password = password.encode("utf-8")
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(), length=32, salt=bundle_salt, iterations=480000,
            )
            bundle_hash = base64.urlsafe_b64encode(kdf.derive(decoded_password))
            bundle_hash = self._encrypt_fernet(bundle_hash.decode(), self.bundle_key)
        session_bundles = request.session.get("pw_bundles") and request.session.get("pw_bundles").copy() or {}
        session_bundles.update({
            self.id: {"last_login": fields.Datetime.now(), "bundle_hash": bundle_hash}
        })
        request.session.update({
            "pw_bundles": session_bundles,
            "pw_bundle_last_update": fields.Datetime.now(), # 1 IMPORTANT
        })
        if password_change:
            self.password_update_time = fields.Datetime.now()

    def _refresh_bundle_keys(self, old_bundle_key):
        """
        The method to launch decrypt, and then encrypt linked password keys 

        Args:
         * old_bundle_key - str - previous bundle key/salt&password to decrypt linked passwords keys

        Extra info:
         * Expected singleton
        """
        password_ids = self.with_context(active_test=False).env["password.key"].search([("bundle_id", "=", self.id)])
        password_ids.with_context(old_bundle_key=old_bundle_key).write({"bundle_id": self.id})

    def encrypt_key(self, password):
        """
        The method to encrypt password usign the bundle_key

        Args:
         * password - char

        Methods:
         * _get_bundle_key
         * _encrypt_fernet

        Returns:
         * char
        """
        encrypted_key = password
        if password:
            if self:
                bundle_key = self._get_bundle_key()
                if bundle_key:
                    encrypted_key = self._encrypt_fernet(password, bundle_key)
                else:
                    _logger.warning("Password can't be encrypted: no key")
            else:
                _logger.warning("Password can't be encrypted: no bundle")
        return encrypted_key

    def decrypt_key(self, password):
        """
        The method to encrypt password usign the bundle_key

        Args:
         * password - char

        Methods:
         * _get_bundle_key
         * _decrypt_fernet

        Returns:
         * char
        """
        decrypted_key = password
        if self:
            if self.env.context.get("old_bundle_key") is not None:
                bundle_key = self.env.context.get("old_bundle_key")
            else:
                bundle_key = self._get_bundle_key()
            if password and bundle_key:
                decrypted_key = self._decrypt_fernet(password, bundle_key)
            else:
                _logger.warning("Password can't be decrypted: no key")
        else:
            _logger.warning("Password can't be decrypted: no bundle")
        return decrypted_key

    @api.model
    def _encrypt_fernet(self, password, bundle_key):
        """
        The method to encrypt password

        Args:
         * password - str
         * bundle_key - str
        
        Return:
         * str
        """
        encrypted_key = password
        try:
            fe = Fernet(bundle_key)
            password = password.encode()
            encrypted_key = fe.encrypt(password)
            encrypted_key = encrypted_key.decode()
        except Exception as er:
            _logger.warning("Password can't be encrypted: {}".format(er))
        return encrypted_key

    @api.model
    def _decrypt_fernet(self, password, bundle_key):
        """
        The method to decrypt password

        Args:
         * password - str
         * bundle_key - str
        
        Return:
         * str
        """
        decrypted_key = password
        try:
            fe = Fernet(bundle_key)
            password = password.encode()
            password = fe.decrypt(password)
            decrypted_key = password.decode()
        except Exception as error:
            _logger.warning("Password can't be decrypted: {}".format(error))
        return decrypted_key
