# -*- coding: utf-8 -*-

import json
import logging
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.addons.odoo_password_manager.models.password_bundle import INCORRECT_CONFIRM_PASSWORD_WARNING
from odoo.exceptions import AccessError, ValidationError
from odoo.osv.expression import OR
from odoo.tools.safe_eval import safe_eval
from odoo.tools import is_html_empty

_logger = logging.getLogger(__name__)

try:
    # for the version from 1.7
    import passlib.pwd as pwd
    def pw_generate(length, charset):
        return pwd.genword(length=length, charset=charset)
except:
    # for the version after 1.7
    import passlib.utils as pwd
    def pw_generate(length, charset):
        return pwd.generate_password(size=length, charset=charset)

try:
    from zxcvbn import zxcvbn
    def zxcvbn_calc(password):
        if len(password) > 200:
            # for very long passwords the method will be hanging for a long time. So we estimate the first 200 letters
            # that, in practice, should be more than enough
            return zxcvbn(password[:200])
        else:
            return zxcvbn(password)
except ImportError as e:
    _logger.error(e)
    def zxcvbn_calc(password):
        return 0

ALLOWED_UNDER_SUDO = [
    "odoo_password_manager.password_key_add_to_favourite", "odoo_password_manager.password_key_remove_from_favourite"]
PASSWORD_FIELDS_TO_MERGE = [
    "name", "bundle_id", "user_name", "password_update_date", "email", "link_url", "phone", "partner_id",
]
ACCESS_DENIED_WARNING = _("Access denied! Please login to the bundle {}")


class password_key(models.Model):
    """
    The model to keep passwords and related info
    """
    _name = "password.key"
    _inherit = ["mail.activity.mixin", "mail.thread", "bundle.security.mixin"]
    _description = "Password"
    _mail_post_access = "read"

    @api.model
    def default_bundle_id(self):
        """
        Default method for bundle_id (needed in case of page refresh)
        """
        if self._context.get("params") and self._context.get("params").get("default_bundle_id"):
            return self._context.get("params").get("default_bundle_id")

    @api.depends("password")
    def _compute_password_streng(self):
        """
        Onchange method for password
        The goal is to show calculated strength in real time
        """
        for passwordkey in self:
            password_streng = passwordkey.password and str(zxcvbn_calc(passwordkey.password).get("score")) or "0"
            passwordkey.password_streng = password_streng

    def _compute_duplicates_count(self):
        """
        Compute method for duplicates_count

        Methods:
         * _construct_duplicates_domain
         * search_count
        """
        for password in self:
            domain = password._construct_duplicates_domain()
            duplicates_count = domain and self.search_count(domain) or 0
            password.duplicates_count = duplicates_count

    def search_duplicates_count(self, operator, value):
        """
        Search method for duplicates_count
        Introduced since the field is not stored

        Methods:
         * _construct_duplicates_domain

        Extra info:
         * this search mehod covers 2 cases: when we search a specific ID (ilike operator) or just all passwords that
           might have duplicates
        """
        domain = []
        if operator == "ilike":
            # this is searh for a specific password duplicates
            domain = [("id", "=", 0)]
            try:
                password_id = self.env["password.key"].browse(int(value))
                if password_id.exists():
                    domain = password_id._construct_duplicates_domain(exclude_self=False) or domain
            except:
                domain = [("id", "=", 0)]
        else:
            passwords = self.search([])
            potential_dupplicates = []
            for password in passwords:
                if password.duplicates_count > 0:
                    potential_dupplicates.append(password.id)
            domain = [("id", "in", potential_dupplicates)]
        return domain

    def _inverse_link_url(self):
        """
        Inverse method for link_url
        The goal is to make an url have proper format

        Methods:
         * url_parse of werkzeugurls
        """
        for password in self:
            clean_url = password.link_url
            if clean_url:
                url = urls.url_parse(clean_url)
                if not url.scheme:
                    if not url.netloc:
                        url = url.replace(netloc=url.path, path="")
                    clean_url = url.replace(scheme="http").to_url()
            if clean_url != password.link_url:
                password.link_url = clean_url

    def _inverse_attachment_ids(self):
        """
        Inverse method for attachment_ids
        The goal is to make attachments ordinary one with stated res_id
        """
        for password in self:
            password.attachment_ids.write({"res_id": password.id})

    @api.model
    def _generate_order_by(self, order_spec, query):
        """
        Specify how to proceed the technical ordering by name, so to have it in lower case
        """
        res = super(password_key, self)._generate_order_by(order_spec=order_spec, query=query)
        if "name asc" or "name desc" in order_spec:
            res = res.replace('"password_key"."value"', 'LOWER("password_key"."value")')
            res = res.replace('"password_key"."name"', 'LOWER("password_key"."name")')
        return res

    @api.depends("access_user_group_ids", "access_user_group_ids.users", "access_user_ids")
    def _compute_access_all_user_ids(self):
        """
        Compute method for access_all_user_ids
        """
        for passwordkey in self:
            users = passwordkey.access_user_group_ids.mapped("users")
            user_ids = (users | passwordkey.access_user_ids).ids
            passwordkey.access_all_user_ids = [(6, 0, user_ids)]

    @api.depends("share_ids")
    def _compute_vault_ids(self):
        """
        Compute method for vault_ids
        """
        for passwordkey in self:
            passwordkey.vault_ids = [(6, 0, passwordkey.share_ids.mapped("portal_password_bundle_id").ids)]

    name = fields.Char(string="Reference")
    bundle_id = fields.Many2one("password.bundle", string="Bundle", ondelete="cascade", default=default_bundle_id)
    user_name = fields.Char(string="User name")
    password = fields.Char(string="Password", copy=False)
    password_streng = fields.Selection(
        [("0", "Horrible"), ("1", "Bad"), ("2", "Weak"), ("3", "Good"), ("4", "Strong")],
        string="Password Strength",
        compute=_compute_password_streng,
        readonly=False,
        store=True,
    )
    password_len = fields.Integer(string="Password Length", default=0)
    confirm_password = fields.Char(string="Confirm Password", copy=False)
    password_update_date = fields.Date(string="Password is updated on", readonly=True)
    mail_activity_update_id = fields.Many2one("mail.activity", string="Mail Activity to update password")
    email = fields.Char(string="Email")
    link_url = fields.Char(string="URL", inverse=_inverse_link_url)
    phone = fields.Char(string="Phone")
    partner_id = fields.Many2one("res.partner", string="Partner")
    tag_ids = fields.Many2many(
        "password.tag",
        "password_tag_password_key_rel_table",
        "password_tag_id",
        "password_key_id",
        string="Tags",
    )
    no_update_required = fields.Boolean(
        string="No Update Required",
        help="If checked, bundle update policies will not generate activities for this password",
    )
    notes = fields.Html(string="Notes")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "ir_attachment_password_key_rel_table",
        "attachment_id",
        "password_key_id",
        string="Attachments",
        copy=True,
        inverse=_inverse_attachment_ids,
    )
    favourite_user_ids = fields.Many2many(
        "res.users",
        "res_users_password_key_rel_favor_table",
        "res_users_favor_id",
        "password_key_favor_id",
        string="Favourite of",
        copy=False,
    )
    duplicates_count = fields.Integer(
        string="Duplicates Count",
        compute=_compute_duplicates_count,
        search="search_duplicates_count",
    )
    color = fields.Integer(string="Color Index")
    active = fields.Boolean(string="Active", default=True)
    access_user_group_ids = fields.Many2many(
        "res.groups",
        "res_groups_password_key_rel_table",
        "res_groups_id",
        "password_key_id",
        string="Access Groups",
        help="""If selected, a user should belong to one of those groups or among 'Access Users' to access this key.
The exceptions are (1) Bundle 'Full rights' managers and administrators; (2) The bundle creator.
To access the key a user should also have an access to its bundle""",
    )
    access_user_ids = fields.Many2many(
        "res.users",
        "res_users_password_key_rel_table",
        "res_users_id",
        "password_key_id",
        string="Access Users",
        help="""If selected, a user should be among the chosen users or should belong to one of those groups to access \
this key.
The exceptions are (1) Bundle 'Full rights' managers and administrators; (2) The bundle creator.
To access the key a user should also have an access to its bundle""",
    )
    access_all_user_ids = fields.Many2many(
        "res.users",
        "res_users_password_key_all_rel_table",
        "res_users_id",
        "password_key_id",
        string="All Access Users",
        compute=_compute_access_all_user_ids,
        compute_sudo=True,
        store=True,
    )
    share_ids = fields.One2many("portal.password.key", "password_id", string="Shares")
    vault_ids = fields.Many2many(
        "portal.password.bundle", compute=_compute_vault_ids, compute_sudo=True, store=True,
    )

    _order = "name ASC, id"

    def read(self, fields=None, load="_classic_read"):
        """
        Overwrite to decrypt passwords while reading
        We do that here not in field widget for example to avoid complexity of detecting whether a field is encrypted,
        or it should be decrypted. E.g. when we save a record, or when a user start changing it
        """
        result = super(password_key, self).read(fields=fields, load=load)
        for pw_dict in result:
            if pw_dict.get("password") or pw_dict.get("confirm_password"):
                bundle_id = self.browse(pw_dict.get("id")).bundle_id
                if pw_dict.get("password"):
                    pw_dict.update({"password": bundle_id.decrypt_key(pw_dict.get("password"))})
                if pw_dict.get("confirm_password"):
                    pw_dict.update({"confirm_password": bundle_id.decrypt_key(pw_dict.get("confirm_password"))})
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overwrite to decrypt password and confirm_password

        Methods:
         * _calculate_properties
        """
        global_ctx_bundle_id = self._context.get("default_bundle_id") or (self._context.get("params") \
            and self._context.get("params").get("default_bundle_id")) or False
        need2copy_confirm_pw = self._context.get("import_file")
        today_date = fields.Date.today()
        for values in vals_list:
            if need2copy_confirm_pw and not values.get("confirm_password"):
                values["confirm_password"] = values.get("password")
            if values.get("password") != values.get("confirm_password"):
                raise ValidationError(INCORRECT_CONFIRM_PASSWORD_WARNING)
            bundle_to_edit = values.get("bundle_id") or global_ctx_bundle_id
            bundle_id = self.env["password.bundle"].browse(bundle_to_edit)
            password = values.get("password")
            encrypted_password, password_streng, password_len = self._calculate_properties(bundle_id, password)
            values.update({
                "password": encrypted_password,
                "confirm_password": encrypted_password,
                "password_streng": password_streng,
                "password_len": password_len,
                "password_update_date": today_date,
            })
        password_ids = super(password_key, self).create(vals_list)
        return password_ids

    def write(self, vals):
        """
        Overwrite to decrypt password and confirm_password
        In case bundle id or password or confirm password are changed --> encrypt password

        Methods:
         * _calculate_properties
        """
        if not self._context.get("import_file") and vals.get("password") != vals.get("confirm_password"):
            raise ValidationError(INCORRECT_CONFIRM_PASSWORD_WARNING)
        res = True
        for password_object in self:
            pw_updated = False
            values = vals.copy()
            if (values.get("bundle_id"), values.get("password"), values.get("confirm_password")).count(None) != 3:
                pw_updated = values.get("password") is not None
                pw_dict = password_object.read(fields=["password", "bundle_id"], load=False)[0] # to decrypt
                bundle_id = self.env["password.bundle"].browse(values.get("bundle_id") or pw_dict.get("bundle_id"))
                if pw_updated:
                    password = values.get("password")
                else:
                    password = pw_dict.get("password")
                encrypted_password, password_streng, password_len = self._calculate_properties(bundle_id, password)
                values.update({
                    "password": encrypted_password,
                    "confirm_password": encrypted_password,
                    "password_streng": password_streng,
                    "password_len": password_len,
                })
                if pw_updated:
                    values.update({"password_update_date": fields.Date.today()})
            res = super(password_key, password_object).write(values)
            if pw_updated and password_object.mail_activity_update_id:
                password_object.mail_activity_update_id.action_done()
        return res

    def export_data(self, fields_to_export):
        """
        Re-write to decrypt passwords when exporting

        Args:
         * fields_to_export - dict

        Methods:
         * super
         * decrypt_key of password.bundle

        1. Export data indexes of password and confirm password if any
        2. Go by each expported password > convert according to the bunlde descryption
           IMPORTANT: here we assume that export_data order is absolutely the same as in self.
        """
        result = super(password_key, self).export_data(fields_to_export=fields_to_export)
        datas = result.get("datas")
        # 1
        to_decrypt_indexes = []
        for e_index, e_field in enumerate(fields_to_export):
            if e_field in ["password", "confirm_password"]:
                to_decrypt_indexes.append(e_index)
        if to_decrypt_indexes:
            # 2
            result_index = 0
            for pw_key in self:
                bundle_id = pw_key.bundle_id
                for field_index in to_decrypt_indexes:
                    if datas[result_index][field_index]:
                        datas[result_index][field_index] = bundle_id.decrypt_key(datas[result_index][field_index])
                result_index += 1
            result.update({"datas": datas})
        return {"datas": datas}

    @api.model
    def default_get(self, fields):
        """
        Overwrite to pass password default value
        The reason fo not using just "default", since we should have the same value for password and confirm_password

        Methods:
         * action_generate_new_password
        """
        values = super(password_key, self).default_get(fields)
        Config = self.env["ir.config_parameter"].sudo()
        need_default = safe_eval(Config.get_param("generate_passord_on_create", "False"))
        pw_default = False
        if need_default:
            length = int(Config.get_param("defau_password_length", default="10"))
            charset = Config.get_param("defau_password_charset", default="ascii_62")
            pw_default = self.action_generate_new_password(length, charset)
        values.update({"password": pw_default, "confirm_password": pw_default})
        return values

    @api.model
    def action_generate_new_password(self, length, charset):
        """
        The method to generate a new password

        Args:
         * length - int
         * charset - selection (observe password.generator model)

        Returns:
         * unicode
        """
        if not length or length <= 0 or not charset:
            raise ValidationError(_("Please select a proper password length and complexity!"))
        return pw_generate(length, charset)

    @api.model
    def action_check_bundle_edit_rights(self, bundle_ids):
        """
        The method to check whether the current user has full rights at least for one of active bundles

        Args:
         * bundle_ids - list of ints

        Return:
         * bool
        """
        result = False
        domain = []
        if bundle_ids:
            domain.append(("id", "in", bundle_ids))
        all_bundle_ids = self.env["password.bundle"].search(domain)
        for bundle in all_bundle_ids:
            if bundle.has_full_right_to:
                result = True
                break
        return result

    @api.model
    def action_return_mass_actions(self, can_update=False):
        """
        The method to return available mass actions in js format
        This should be called only if a user has right at least for a single considered bundle
        (@see components/password_manager)

        Returns:
         * list of dict
           ** id
           ** name
        """
        result = []
        self = self.sudo()
        Config = self.env["ir.config_parameter"].sudo()
        mass_actions_list = safe_eval(Config.get_param("passwords_passwords_ir_actions_server_ids", "[]"))
        mass_action_ids = self.env["ir.actions.server"].search([("id", "in", mass_actions_list)])
        for mass_action in mass_action_ids:
            if can_update or mass_action.safe_pwm_action:
                if not mass_action.groups_id or (self.env.user.groups_id & mass_action.groups_id):
                    result.append({"id": mass_action.id, "name": mass_action.name})
        return result

    @api.model
    def action_return_export_conf(self):
        """
        The method to return available mass actions in js format

        Returns:
         * bool
        """
        export_conf = False
        if self.env.is_admin() or self.env.user.has_group("base.group_allow_export"):
            Config = self.env["ir.config_parameter"].sudo()
            export_conf = safe_eval(Config.get_param("password_management_export_option", "False"))
        return export_conf

    @api.model
    def action_proceed_mass_action(self, pw_list, action_id):
        """
        The method to trigger mass action for selected passwords

        Args:
         * pw_list - list of ints (selected password IDs)
         * action_id - int - ir.actions.server id

        Methods:
         * run() of ir.actions.server

        Returns:
         * dict: either action dict, or special view dict, or empty dict if no result

        Extra info:
         * we use api@model with search to make sure each record exists (e.g. deleted in meanwhile)
        """
        pw_ids = self.env["password.key"].with_context(active_test=False).search([("id", "in", pw_list)])
        result = {}
        if pw_ids:
            action_server_id = self.env["ir.actions.server"].browse(action_id)
            if action_server_id.exists():
                action_context = {
                    "active_id": pw_ids[0].id,
                    "active_ids": pw_ids.ids,
                    "active_model": self._name,
                    "record": pw_ids[0],
                    "records": pw_ids,
                }
                result = action_server_id.with_context(action_context).run()
                if result and result.get("type"):
                    local_context = {}
                    if result.get("context"):
                        local_context = result.get("context")
                        if not isinstance(local_context, dict):
                            local_context = json.loads(result.get("context"))
                    local_context.update({"default_password_ids": [(6, 0, pw_ids.ids)]})
                    result["context"] = local_context
        return result or {}

    def action_return_share_action(self):
        """
        The method to prepare the wizard action to share passwords

        Returns:
         * dict (action)
        """
        if not self:
            raise ValidationError(_("There are no passwords selected! Please select at least one password"))
        bundle_ids = self.mapped("bundle_id")
        if len(bundle_ids) != 1:
            raise ValidationError(
                _("The passwords relate to different bundles. Sharing is possible within a single bundle only!")
            )
        bundle_id = bundle_ids[0]
        action = self.env.ref("odoo_password_manager.share_portal_password_action").sudo().read()[0]
        action["context"] = {"default_bundle_id": bundle_id.id, "need_navigation_reload": True}
        return action

    def action_return_duplicates_action(self):
        """
        The method to get the correct action for duplicates view

        Returns:
         * dict - action to execute
        """
        if self._context.get("with_bundle"):
            action_id = self.sudo().env.ref("odoo_password_manager.password_key_action").read()[0]
        else:
            action_id = self.sudo().env.ref("odoo_password_manager.password_key_action_all").read()[0]
        return action_id

    def action_toggle_favorite(self):
        """
        The action to add the password to favourites
        Done under sudo to make "favorite" possible for readonly users
        """
        current_user = self.env.user.id
        for password in self:
            if current_user in self.favourite_user_ids.ids:
                self.sudo().favourite_user_ids = [(3, current_user)]
            else:
                self.sudo().favourite_user_ids = [(4, current_user)]

    ####################################################################################################################
    ####################################### jsTree Methods #############################################################
    ####################################################################################################################
    @api.model
    def action_get_hierarchy(self, key, bundle_ids):
        """
        The method to prepare hierarchy

        Args:
         * key - string - js tree reference
         * bundle_ids - list of int or None

        Methods:
         * _return_nodes of password.tag (password.node)
         * _return_types_nodes (dummy, inherited in odoo_password_manager_custom_types)

        Returns:
         * list
        """
        result = []
        if key == "password_tags":
            result = self.env["password.tag"]._return_nodes(bundle_ids)
        elif key == "password_types":
            result = self.env["password.key"]._return_types_nodes()
        elif key == "portal_vaults":
            result = False
            if self.env.user.has_group("odoo_password_manager.group_portal_password_vaults"):
                result = self.env["portal.password.bundle"]._return_nodes(bundle_ids) or False
        return result

    @api.model
    def action_create_node(self, model_name, data, bundle_ids):
        """
        The method to force node unlinking

        Args:
         * key - string
         * data - dict of node params
         * bundle_ids - list of int or None

        Methods:
         * update_node of password.node

        Returns:
         * int

        Extra info:
         * We do not save bundle for types since types are global
         * When a few bundles exist in context, we get the first one (actually, should not be the case)
        """
        node_id = False
        if model_name:
            bundle_id = False
            if model_name == "password.tag" and bundle_ids:
                bundle_id = bundle_ids[0]
            node_id = self.env[model_name].create_node(data, bundle_id)
        return node_id

    @api.model
    def action_update_node(self, model_name, node_id, data, position):
        """
        The method to force node unlinking

        Args:
         * key - string
         * node_id - int - object ID
         * data - dict of node params
         * position - int or False

        Methods:
         * update_node of password.node
        """
        if model_name:
            node_object = self.env[model_name].browse(node_id)
            if node_object.exists():
                node_object.update_node(data, position)

    @api.model
    def action_delete_node(self, model_name, node_id):
        """
        The method to force node unlinking

        Args:
         * key - string
         * node_id - int - object ID

        Methods:
         * delete_node of password.node
        """
        if model_name:
            node_object = self.env[model_name].browse(node_id)
            if node_object.exists():
                node_object.delete_node()

    @api.model
    def _return_types_nodes(self):
        """
        The DUMMY method to return types hierarchy
        Introduced for inheritance purposes
        """
        return None

    ####################################################################################################################
    ####################################### Helpers  ###################################################################
    ####################################################################################################################
    @api.model
    def _calculate_properties(self, bundle_id, password):
        """
        The method to calculate password_streng and password_len when password is updated

        Args:
         * bundle_id - password.bundle object
         * password - str (might be False/None)

        Methods:
         * encrypt_key of password.bundle

        Returns:
         * tuple

        Extra info:
         * -1 is used for missing passwords to distinguish no password from obsolete, not calculated passwords
        """
        password_streng = "0"
        password_len = -1
        encrypted_password = password
        if password:
            encrypted_password = bundle_id.encrypt_key(password)
            password_streng = str(zxcvbn_calc(password).get("score"))
            password_len = len(password)
        return encrypted_password, password_streng, password_len

    def _construct_duplicates_domain(self, exclude_self=True):
        """
        The method to construct domain for a given record by given fields

        Args:
         * exclude_self - bool - whether current key should be shown

        Returns:
         * list of leaves (reverse polish notation) or False

        Extra info:
         * We do not check field type for relations and so on, since we rely upon xml fields domain
         * If we are in the bundle interface, we search for duplicates only inside this bundle
         * Expected singleton
        """
        self = self.sudo()
        domain = False
        fields_domain = []
        Config = self.env["ir.config_parameter"].sudo()
        duplicate_fields = safe_eval(Config.get_param("odoo_password_manager.duplicate_pw_fields_ids", "[]"))
        fields = self.sudo().env["ir.model.fields"].search([("id", "in", duplicate_fields)])
        for field in fields:
            if self[field.name]:
                if field.ttype == "many2one":
                    fields_domain = OR([fields_domain, [(field.name, "in", self[field.name].ids)]])
                elif field.ttype == "char":
                    fields_domain = OR([fields_domain, [(field.name, "=ilike", self[field.name])]])
                else:
                    fields_domain = OR([fields_domain, [(field.name, "=", self[field.name])]])
        if fields_domain:
            domain = fields_domain
            if exclude_self:
                domain.append(("id", "!=", self.id))
            if self._context.get("default_bundle_id"):
                domain.append(("bundle_id", "=", self.bundle_id.id))
        return domain

    def _merge_get_fields_specific(self):
        """
        The method to process specific fields

        Returns:
         * dict
        """
        return {
            "notes": lambda fname, passwords: "<br/><br/>".join(
                desc for desc in passwords.mapped("notes") if not is_html_empty(desc)
            ),
            "tag_ids": lambda fname, passwords: [(6, 0, passwords.mapped("tag_ids").ids)],
            "attachment_ids": lambda fname, passwords: [(6, 0, passwords.mapped("attachment_ids").ids)],
            "favourite_user_ids": lambda fname, passwords: [(6, 0, passwords.mapped("favourite_user_ids").ids)],
        }

    def _merge_get_fields(self):
        """
        The method to get all fields which should be merged

        Returns:
         * list
        """
        return list(PASSWORD_FIELDS_TO_MERGE) + list(self._merge_get_fields_specific().keys())

    def _get_merged_data(self):
        """
        The method to read fields of merged opportunities
        The idea is the same as in case of crm.lead merging tool (@see crm.lead _merge_data):
         * text: all the values are concatenated
         * m2m and o2m: those fields aren't processed
         * m2o: the first not null value prevails (the other are dropped)
         * any other type of field: same as m2o

        Returns:
         * dict of new values for passwords
        """
        fnames = self._merge_get_fields()
        fcallables = self._merge_get_fields_specific()

        def _get_first_not_null(attr, opportunities):
            value = False
            for opp in opportunities:
                if opp[attr]:
                    value = opp[attr].id if isinstance(opp[attr], models.BaseModel) else opp[attr]
                    break
            return value

        data = {}
        for field_name in fnames:
            field = self._fields.get(field_name)
            if field is None:
                continue

            fcallable = fcallables.get(field_name)
            if fcallable and callable(fcallable):
                data[field_name] = fcallable(field_name, self)
            elif not fcallable and field.type in ("many2many", "one2many"):
                continue
            else:
                data[field_name] = _get_first_not_null(field_name, self)  # take the first not null
        return data
