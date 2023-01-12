# -*- coding: utf-8 -*-

from odoo import fields, models


class password_tag(models.Model):
    """
    The model to systemize password tags
    """
    _name = "password.tag"
    _inherit = ["password.node", "bundle.security.mixin"]
    _description = "Tag"

    name = fields.Char(string="Name", required=True, translate=False)
    description = fields.Html(string="Tag Description", translate=False)
    parent_id = fields.Many2one("password.tag", string="Parent Tag")
    child_ids = fields.One2many("password.tag", "parent_id", string="Child Tags")
    color = fields.Integer(string="Color index", default=10)
    password_ids = fields.Many2many(
        "password.key",
        "password_tag_password_key_rel_table",
        "password_key_id",
        "password_tag_id",
        string="Passwords",
    )

    _order = "sequence, id"
