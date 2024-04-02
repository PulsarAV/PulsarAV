# -*- coding: utf-8 -*-

from markupsafe import Markup

from odoo import _, fields, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import get_records_pager, CustomerPortal, pager as portal_pager
from odoo.tools.safe_eval import safe_eval


class CustomerPortal(CustomerPortal):
    """
    The controller to introduce portal passwords interfaces
    """
    def _prepare_home_portal_values(self, counters):
        """
        Overwrite to understand wheter the portal entry should be shown

        Methods:
         * _check_portal_vault_setting
         * _return_partner_vault_domain
        """
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        if "pwm_count" in counters and not self._check_portal_vault_setting():
            partner_id = request.env.user.partner_id.id
            com_partner_id = request.env.user.partner_id.commercial_partner_id.id
            pwm_count = request.env["portal.password.bundle"].search_count(self._return_partner_vault_domain())
            values.update({"pwm_count": pwm_count})
        return values

    def _return_partner_vault_domain(self):
        """
        The method to prepare the domain for the current user partner vaults

        Returns:
         * list (RPR)
        """
        partner_id = request.env.user.partner_id.id
        com_partner_id = request.env.user.partner_id.commercial_partner_id.id
        return ["|", ("partner_ids", "in", partner_id), ("partner_ids", "=", com_partner_id)]

    def _check_portal_vault_setting(self):
        """
        The method to check whether the portal vaults are turned on
        """
        if not request.env.user.has_group("odoo_password_manager.group_portal_password_vaults"):
            return request.render("http_routing.403")
        return False

    def _get_passwords_search(self, search=None, search_in="all", extra_fields=[]):
        """
        The method to prepare the available search criteria for portal passwords and the search domain

        Args:
         * search - str

        Returns:
         * tuple:
          ** dict of searches
          ** list - RPR current search
        """
        searchbar_inputs = {
            "all": {"input": "all", "label": _("Search in all")},
            "name": {"input": "name", "label": _("Search in references")},
            "user_name": {"input": "user_name", "label": _("Search in user names")},
        }
        if "link_url" in extra_fields:
            searchbar_inputs.update({"link_url": {"input": "link_url", "label": _("Search in URLs")}})
        if "email" in extra_fields:
            searchbar_inputs.update({"email": {"input": "email", "label": _("Search in emails")}})
        if "phone" in extra_fields:
            searchbar_inputs.update({"phone": {"input": "phone", "label": _("Search in phone numbers")}})
        if "notes" in extra_fields:
            searchbar_inputs.update({"notes": {"input": "notes", "label": _("Search in notes")}})

        search_domain = []
        if search:
            if search_in == "all":
                search_domain =  [
                    "|", "|", "|", "|", "|",
                        ("name", "ilike", search), ("user_name", "ilike", search), ("link_url", "ilike", search),
                        ("email", "ilike", search), ("phone", "ilike", search), ("notes", "ilike", search),
                ]
            elif search_in == "name":
                search_domain = [("name", "ilike", search)]
            elif search_in == "user_name":
                search_domain = [("user_name", "ilike", search)]
            elif search_in == "link_url":
                search_domain = [("link_url", "ilike", search)]
            elif search_in == "email":
                search_domain = [("email", "ilike", search)]
            elif search_in == "phone":
                search_domain = [("phone", "ilike", search)]
            elif search_in == "notes":
                search_domain = [("notes", "ilike", search)]
        return searchbar_inputs, search_domain

    @http.route(["/my/password_vaults", "/my/password_vaults/page/<int:page>"], type="http", auth="user",
        website=True, sitemap=True)
    def portal_password_vaults(self, page=1, **kw):
        """
        The route to open password vaults

        Methods:
         * _return_partner_vault_domain
        """
        res = self._check_portal_vault_setting()
        if res:
            return res
        vault_object = request.env["portal.password.bundle"]
        domain = self._return_partner_vault_domain()
        url = "/my/password_vaults"
        vaults_count = vault_object.search_count(domain)
        pager = portal_pager(url=url, url_args={}, total=vaults_count, page=page, step=self._items_per_page)
        vault_ids = vault_object.search(domain, limit=self._items_per_page, offset=pager["offset"])
        values = {
            "page_name": _("Password Vaults"), "default_url": url, "vault_ids": vault_ids, "pager": pager,
        }
        res = request.render("odoo_password_manager.portal_vaults", values)
        return res

    @http.route(["/my/password_vaults/<model('portal.password.bundle'):vault_id>",
        "/my/password_vaults/<model('portal.password.bundle'):vault_id>/page/<int:page>"], type="http", auth="user",
        website=True, sitemap=True)
    def portal_password_vault(self, page=1, vault_id=None, search=None, search_in="all", **kw):
        """
        The route to open the vault passwords

        Methods:
         * _check_bundle_session of portal.password.bundle
         * _get_passwords_search
         * _get_custom_fields
        """
        res = self._check_portal_vault_setting()
        if res:
            return res
        if vault_id:
            values = {"vault_id": vault_id, "main_object": vault_id, "page_name": vault_id.name, "passwords": None}
            if vault_id._check_bundle_session():
                pw_domain = [("portal_password_bundle_id", "=", vault_id.id)]
                url = "/my/password_vaults/{}".format(vault_id.id)

                Config = request.env["ir.config_parameter"].sudo()
                extra_fields = []
                for efield in ["link_url", "phone", "email", "notes"]:
                    need_field = safe_eval(Config.get_param("password_management_portal_vault_" + efield, "False"))
                    if need_field:
                        extra_fields.append(efield)
                searchbar_inputs, search_domain = self._get_passwords_search(search, search_in, extra_fields)
                pw_domain.extend(search_domain)
                password_count = request.env["portal.password.key"].search_count(pw_domain)
                pager = portal_pager(
                    url=url, url_args={"search": search, "search_in": search_in}, total=password_count, page=page,
                    step=self._items_per_page,
                )
                password_ids = request.env["portal.password.key"].search(
                    pw_domain, limit=self._items_per_page, offset=pager["offset"]
                )
                passwords = password_ids.read(fields=["name", "user_name", "password_len"] + extra_fields)
                values.update({
                    "passwords": passwords,
                    "searchbar_inputs": searchbar_inputs,
                    "search_in": search_in,
                    "pager": pager,
                    "done_search": search or False,
                    "default_url": url,
                    "extra_fields": extra_fields,
                })
                values.update(self._get_custom_fields(password_ids))
            res = request.render("odoo_password_manager.portal_vault", values)
        else:
            res = request.render("http_routing.404")
        return res

    def _get_custom_fields(self, password_ids):
        """
        The method to get custom portal columns if any

        Args:
         * password_ids - portal.password.key recordset

        Returns:
         * dict: custom_values/c_labels

        Extra info:
         * we use sql query to avoid security check (here not encryption should take place!)
        """
        Config = request.env["ir.config_parameter"].sudo()
        custom_fields = safe_eval(Config.get_param("odoo_password_manager.pw_custom_portal_fields", "[]"))
        if not custom_fields:
            return {"custom_values": {}, "c_labels": []}
        password_keys = password_ids.mapped("password_id.id")
        if not password_keys:
            return {"custom_values": {}, "c_labels": []}
        custom_field_ids = request.env["ir.model.fields"].sudo().search([("id", "in", custom_fields)])
        c_fields = custom_field_ids.mapped("name")
        query = "SELECT {} FROM password_key WHERE id IN %s;".format(",".join(c_fields))
        request.env.cr.execute(query, (tuple(password_keys),))
        pw_values = request.env.cr.fetchall()
        custom_values = {}
        for pw_index, pw_value in enumerate(pw_values):
            field_values = []
            for field_index, field_value in enumerate(pw_value):
                custom_field = custom_field_ids[field_index]
                ff_ttype = custom_field.ttype
                ff_value = field_value
                if field_value:
                    if ff_ttype == "html":
                        ff_value = Markup(field_value)
                    elif ff_ttype == "selection":
                        selection_value = dict((
                            request.env["password.key"]._fields[custom_field.name]._description_selection(request.env)
                        ))[field_value]
                        ff_value = selection_value
                field_values.append({"type": ff_ttype, "value": ff_value})
            custom_values.update({password_ids[pw_index].id : field_values})
        c_labels = custom_field_ids.mapped("field_description")
        return {"custom_values": custom_values, "c_labels": c_labels}
