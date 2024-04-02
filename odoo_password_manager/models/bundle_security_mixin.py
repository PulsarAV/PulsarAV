# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import RedirectWarning
from odoo.http import request


class bundle_security_mixin(models.AbstractModel):
    """
    The model to keep checks for CRUD based on the linked bundle_id
    """
    _name = "bundle.security.mixin"
    _description = "Bundle Security Mixin"

    def read(self, fields=None, load="_classic_read"):
        """
        Overwrite to check bundle security
        We check read rights for password keys only since:
         * for bundle, otherwise, the initial kanban overview will require log in to each available bundle
         * for tags, the common list be not actually functioning

        Methods:
         * _check_bundle_key
        """
        result = super(bundle_security_mixin, self).read(fields=fields, load=load)
        if self._name == "password.key":
            try:
                self._check_bundle_key()
            except:
                result = []
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overwrite to check bundle security
        We do not check rights for just created bundle

        Methods:
         * _check_bundle_key
        """
        result = super(bundle_security_mixin, self).create(vals_list)
        if self._name != "password.bundle":
            result._check_bundle_key()
        return result

    def write(self, vals):
        """
        Overwrite to check bundle security
        We check security of both previous and next bundle if it is changed to make sure both operations are allowed

        Methods:
         * _check_bundle_key
        """
        self._check_bundle_key()
        result = super(bundle_security_mixin, self).write(vals)
        if self._name == "password.bundle" or vals.get("bundle_id"):
            self._check_bundle_key()
        return result

    def unlink(self):
        """
        Overwrite to check bundle security

        Methods:
         * _check_bundle_key
        """
        self._check_bundle_key()
        return super(bundle_security_mixin, self).unlink()

    def export_data(self, fields_to_export):
        """
        Overwrite to check bundle security

        Methods:
         * _check_bundle_key
        """
        self._check_bundle_key()
        return super(bundle_security_mixin, self).export_data(fields_to_export=fields_to_export)

    def action_check_bundle_key(self):
        """
        The method that checks security on js level for passed bundles

        Methods:
         * _check_bundle_key

        Returns:
         * list of ints

        Extra info:
         * We need the exact bundles that fail, so we should check each one step by step
        """
        valid_action = True
        failed_bundle_ids = []
        for bundle in self:
            try:
                bundle._check_bundle_key()
            except:
                failed_bundle_ids.append(bundle.id)
        return failed_bundle_ids

    def _check_bundle_key(self):
        """
        The method to check whether the action on target model is possible based on bundle extra security

        Returns:
         * True if check is successfull
         * Raises RedirectWarning
        """
        def return_login_popup(default_bundle_id):
            """
            The method to trigger redirect warning with the Log in action
            """
            xml_id = self.sudo().env.ref("odoo_password_manager.bundle_login_password_action_simple").id
            raise RedirectWarning(
                message=_("The bundle session is expired! Please log in"),
                action=xml_id,
                button_text=_("Press to log in"),
                additional_context= {"default_bundle_id": default_bundle_id.id},
            )

        if not self:
            return True
        if self._name == "password.bundle":
            # IMPORTANT: check does not assume check for read/create
            bundles_ids = self
        else:
            bundles_ids = self.mapped("bundle_id")

        if not bundles_ids:
            return True
        for bundle in bundles_ids:
            # no extra security > no special checks
            # here we also check for previous_security in context for the case when not secured bundle becomes secured
            if not bundle.extra_password_security or self._context.get("no_pwm_security"):
                continue
            # no bundle in session at all
            session_bundles = request.session.get("pw_bundles")
            if not session_bundles or not session_bundles.get(bundle.id):
                return_login_popup(bundle)
            # no last_login in session (should not be a real case, but suddenly)
            last_login = session_bundles.get(bundle.id).get("last_login")
            if not last_login:
                return_login_popup(bundle)
            # bundle password (and, hence, salt) was updated after the last log in
            if bundle.password_update_time and last_login < bundle.password_update_time:
                bundle._clear_session(bundle.id, last_login)
                return_login_popup(bundle)
            # log in is not valid since it is too old in comparison to set session length
            now = fields.Datetime.now()
            diff = (now - last_login).total_seconds() / 60
            if bundle.session_length < diff:
                bundle._clear_session(bundle.id, last_login)
                return_login_popup(bundle)
        return True

    @api.model
    def _clear_session(self, bundle_id, last_login):
        """
        The method to clear bundle hash from session and return required by the method list

        Args:
         * bundle - int
         * last_login - datetime or Fale

        Returns:
         * always True

        Extra info:
         * we take session valus from request to be 100% sure it is fine
        """
        today_now = fields.Datetime.now()
        new_session_bundles = request.session.get("pw_bundles")
        new_session_bundles.update({bundle_id: {"last_login": last_login, "bundle_hash": False}})
        request.session.update({
            "pw_bundles": new_session_bundles,
            "pw_bundle_last_update": today_now, # IMPORTANT; @see 1 password.bundle _update_session_bundles
        })
        return True
