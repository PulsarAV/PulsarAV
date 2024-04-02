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
            if self.exists() and node_id and self.id not in node_id.tag_ids.ids:
                node_id.write({"tag_ids": [(4, self.id)]})
        except:
            pass
