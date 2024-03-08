# -*- coding: utf-8 -*-

from odoo.http import request

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class portal_password_key(models.Model):
    """
    The model to keep passwords shared in portal
    """
    _name = "portal.password.key"
    _inherit = "bundle.security.mixin"
    _description = "Portal Password"
    _rec_name = "password_id"

    @api.depends("password_id.password")
    def _compute_password(self):
        """
        Original password change is possible only when the bundle allows that. So, here we may safely 'read' it
        Read is introduced to make sure the password is decrypted

        Methods:
         * _generate_bundle_hash of password.bundle
         * _decrypt_fernet of password.bundle
         * _encrypt_fernet of password.bundle
        """
        for portal_password in self:
            portal_bundle_id = portal_password.portal_password_bundle_id
            bundle_id = portal_bundle_id.bundle_id
            portal_bundle_password =  bundle_id.decrypt_key(portal_bundle_id.password)
            bundle_hash = bundle_id._generate_bundle_hash(
                portal_bundle_id.bundle_salt, portal_bundle_id.bundle_key, portal_bundle_password
            )
            bundle_description_key = bundle_id._decrypt_fernet(bundle_hash, portal_bundle_id.bundle_key)
            decrypted_password = portal_password.password_id.read(fields=["password"])[0].get("password")
            encrypted_password = self.env["password.bundle"]._encrypt_fernet(decrypted_password, bundle_description_key)
            portal_password.password = encrypted_password

    @api.constrains("portal_bundle_bundle_id", "bundle_id")
    def _check_dates(self):
        """
        Constraint to make sure that no shared password is linked to a different password bundle
        """
        for portal_password in self:
            if portal_password.bundle_id != portal_password.portal_bundle_bundle_id:
                raise ValidationError(_(
                    "You are changing the password bundle but this password is shared. Remove shares before"
                ))

    @api.model
    def _generate_order_by(self, order_spec, query):
        """
        Specify how to proceed the technical ordering by name, so to have it in lower case
        """
        res = super(portal_password_key, self)._generate_order_by(order_spec=order_spec, query=query)
        if "name asc" or "name desc" in order_spec:
            res = res.replace('"portal_password_key"."value"', 'LOWER("portal_password_key"."value")')
            res = res.replace('"portal_password_key"."name"', 'LOWER("portal_password_key"."name")')
        return res

    password_id = fields.Many2one("password.key", string="Password Key", required=True, ondelete="cascade")
    portal_password_bundle_id = fields.Many2one(
        "portal.password.bundle",
        string="Bundle",
        required=True,
        ondelete="cascade",
    )
    bundle_id = fields.Many2one(
        string="Password Bundle",
        related="password_id.bundle_id",
        store=True,
        compute_sudo=True,
        related_sudo=True,
    )
    portal_bundle_bundle_id = fields.Many2one(
        string="Portal Bundle",
        related="portal_password_bundle_id.bundle_id",
        store=True,
        compute_sudo=True,
        related_sudo=True,
    )
    password = fields.Char(string="Password", compute=_compute_password, store=True, compute_sudo=True)
    name = fields.Char(related="password_id.name", store=True, compute_sudo=True, related_sudo=True)
    user_name = fields.Char(related="password_id.user_name", store=True, compute_sudo=True, related_sudo=True)
    email = fields.Char(related="password_id.email", store=True, compute_sudo=True, related_sudo=True)
    link_url = fields.Char(related="password_id.link_url", store=True, compute_sudo=True, related_sudo=True,)
    phone = fields.Char(related="password_id.phone", store=True, compute_sudo=True, related_sudo=True)
    notes = fields.Html(related="password_id.notes", store=True, compute_sudo=True, related_sudo=True)
    password_len = fields.Integer(related="password_id.password_len", store=True, compute_sudo=True, related_sudo=True)
    active = fields.Boolean(
        string="Active",
        related="password_id.active",
        store=True,
        compute_sudo=True,
        related_sudo=True,
    )

    _order = "name ASC, id"

    def action_return_decrypted_password(self):
        """
        The method to decrypt the password

        Methods:
         * _check_bundle_session of portal.password.bundle
         * _decrypt_fernet of password.bundle

        Returns:
         * char

        Extra info:
         * Expected singleton
        """
        portal_password_bundle_id = self.portal_password_bundle_id
        bundle_hash = portal_password_bundle_id._check_bundle_session()
        if not bundle_hash:
            return None
        if self.password:
            bundle_key = self.env["password.bundle"]._decrypt_fernet(bundle_hash, portal_password_bundle_id.bundle_key)
            encrypted_password = self.env["password.bundle"]._decrypt_fernet(self.password, bundle_key)
        else:
            encrypted_password = False
        return encrypted_password
