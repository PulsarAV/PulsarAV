# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class res_config_settings(models.TransientModel):
    """
    Overwrite to add settings for the password manager
    """
    _inherit = "res.config.settings"

    def return_charset(self):
        """
        The method to return possible charsets
        """
        return self.env["password.generator"].return_charset()

    @api.depends("passwords_ir_actions_server_ids_str")
    def _compute_ir_actions_server_pwm_default_model_id(self):
        """
        Compute method for ir_actions_server_pwm_default_model_id
        """
        template_model_id = self.env["ir.model"].search([("model", "=", "password.key")], limit=1).id
        for conf in self:
            conf.ir_actions_server_pwm_default_model_id = template_model_id

    @api.depends("passwords_ir_actions_server_ids_str")
    def _compute_passwords_ir_actions_server_ids(self):
        """
        Compute method for passwords_ir_actions_server_ids
        """
        for setting in self:
            ir_actions_server_ids = []
            if setting.passwords_ir_actions_server_ids_str:
                try:
                    actions_list = safe_eval(setting.passwords_ir_actions_server_ids_str)
                    ir_actions_server_ids = self.env["ir.actions.server"].search([("id", "in", actions_list)]).ids
                except Exception as e:
                    ir_actions_server_ids = []
            setting.passwords_ir_actions_server_ids = [(6, 0, ir_actions_server_ids)]

    @api.depends("duplicate_pw_fields_ids_str")
    def _compute_duplicate_pw_fields_ids(self):
        """
        Compute method for duplicate_pw_fields_ids
        """
        for setting in self:
            duplicate_pw_fields_ids = []
            if setting.duplicate_pw_fields_ids_str:
                try:
                    actions_list = safe_eval(setting.duplicate_pw_fields_ids_str)
                    duplicate_pw_fields_ids = self.env["ir.model.fields"].search([("id", "in", actions_list)]).ids
                except Exception as e:
                    duplicate_pw_fields_ids = []
            setting.duplicate_pw_fields_ids = [(6, 0, duplicate_pw_fields_ids)]

    @api.depends("pw_custom_portal_fields_str")
    def _compute_pw_custom_portal_fields(self):
        """
        Compute method for pw_custom_portal_fields
        """
        for setting in self:
            pw_custom_portal_fields = []
            if setting.pw_custom_portal_fields_str:
                try:
                    actions_list = safe_eval(setting.pw_custom_portal_fields_str)
                    pw_custom_portal_fields = self.env["ir.model.fields"].search([("id", "in", actions_list)]).ids
                except Exception as e:
                    pw_custom_portal_fields = []
            setting.pw_custom_portal_fields = [(6, 0, pw_custom_portal_fields)]

    def _inverse_passwords_ir_actions_server_ids(self):
        """
        Inverse method for passwords_ir_actions_server_ids
        """
        for setting in self:
            ir_actions_server_ids_str = ""
            if setting.passwords_ir_actions_server_ids:
                ir_actions_server_ids_str = "{}".format(setting.passwords_ir_actions_server_ids.ids)
            setting.passwords_ir_actions_server_ids_str = ir_actions_server_ids_str

    def _inverse_duplicate_pw_fields_ids(self):
        """
        Inverse method for duplicate_pw_fields_ids
        """
        for setting in self:
            duplicate_pw_fields_ids_str = ""
            if setting.duplicate_pw_fields_ids:
                duplicate_pw_fields_ids_str = "{}".format(setting.duplicate_pw_fields_ids.ids)
            setting.duplicate_pw_fields_ids_str = duplicate_pw_fields_ids_str

    def _inverse_pw_custom_portal_fields(self):
        """
        Inverse method for pw_custom_portal_fields
        """
        for setting in self:
            pw_custom_portal_fields_str = ""
            if setting.pw_custom_portal_fields:
                pw_custom_portal_fields_str = "{}".format(setting.pw_custom_portal_fields.ids)
            setting.pw_custom_portal_fields_str = pw_custom_portal_fields_str

    module_odoo_password_manager_custom_fields = fields.Boolean(string="Custom fields for passwords")
    password_management_export_option = fields.Boolean(
        string="Export passwords",
        config_parameter="password_management_export_option",
    )
    group_password_portal_sharing = fields.Boolean(
        string="Portal vaults",
        implied_group="odoo_password_manager.group_portal_password_vaults",
        group="base.group_portal,base.group_user",
    )
    portal_sharing_link_url = fields.Boolean(
        string="Show URL",
        config_parameter="password_management_portal_vault_link_url",
    )
    portal_sharing_phone = fields.Boolean(
        string="Show Phone",
        config_parameter="password_management_portal_vault_phone",
    )
    portal_sharing_email = fields.Boolean(
        string="Show Email",
        config_parameter="password_management_portal_vault_email",
    )
    portal_sharing_notes = fields.Boolean(
        string="Show Notes",
        config_parameter="password_management_portal_vault_notes",
    )
    generate_passord_on_create = fields.Boolean(
        string="Generate passwords on create",
        config_parameter="generate_passord_on_create",
    )
    defau_password_length = fields.Integer(
        string="Default length for generated password",
        config_parameter="defau_password_length",
        default=10,
    )
    defau_password_charset = fields.Selection(
        return_charset,
        string="Default requirements for password",
        config_parameter="defau_password_charset",
        default="ascii_62",
    )
    ir_actions_server_pwm_default_model_id = fields.Many2one(
        "ir.model",
        compute=_compute_ir_actions_server_pwm_default_model_id,
        string="Default PWM model"
    )
    passwords_ir_actions_server_ids = fields.Many2many(
        "ir.actions.server",
        compute=_compute_passwords_ir_actions_server_ids,
        inverse=_inverse_passwords_ir_actions_server_ids,
        string="Password mass actions",
        domain=[("model_id.model", "=", "password.key")],
    )
    passwords_ir_actions_server_ids_str = fields.Char(
        string="Password pass actions (Str)",
        config_parameter="passwords_passwords_ir_actions_server_ids",
    )
    duplicate_pw_fields_ids = fields.Many2many(
        "ir.model.fields",
        compute=_compute_duplicate_pw_fields_ids,
        inverse=_inverse_duplicate_pw_fields_ids,
        string="Password duplicates fields",
        domain=[
            ("model", "=", "password.key"), ("store", "=", True),
            ("ttype", "not in", ["one2many", "many2many", "binary", "reference", "serialized"]),
        ],
    )
    duplicate_pw_fields_ids_str = fields.Char(
        string="Password duplicates fields (Str)",
        config_parameter="odoo_password_manager.duplicate_pw_fields_ids",
    )
    pw_custom_portal_fields = fields.Many2many(
        "ir.model.fields",
        compute=_compute_pw_custom_portal_fields,
        inverse=_inverse_pw_custom_portal_fields,
        string="Other portal fields",
        domain=[
            ("model", "=", "password.key"),
            ("ttype", "in", ["char", "text", "html", "boolean", "selection", "integer", "float"]),
            ("store", "=", True),
            ("name", "not in",
                ["id", "user_name", "link_url", "phone", "email", "notes", "password", "confirm_password"]),
        ],
    )
    pw_custom_portal_fields_str = fields.Char(
        string="Other portal fields (str)",
        config_parameter="odoo_password_manager.pw_custom_portal_fields",
    )
