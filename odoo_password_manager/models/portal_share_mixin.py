# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class portal_share_mixin(models.AbstractModel):
    """
    The model to keep portal vault basic columns
    """
    _name = "portal.share.mixin"
    _description = "Portal Share Mixin"

    bundle_id = fields.Many2one("password.bundle", string="Bundle", required=True)
    name = fields.Char(string="Vault Name")
    password = fields.Char(string="Vault Password")
    confirm_password = fields.Char(string="Confirm Vault Password")
    partner_ids = fields.Many2many("res.partner", string="Portal Access")
    valid_until = fields.Date(string="Valid Until")
    session_length = fields.Integer(string="Max Session Length (Minutes)", default=60)
    description = fields.Text(string="Notes")

    _sql_constraints = [
        ("session_length_check", "check (session_length>=3)", _("The session should last at least 3 minutes!")),
    ]

    def _return_values_dict(self):
    	"""
    	The method to prepare the values dict based on the general fields

    	Return:
    	 * dict

    	Extra info:
    	 * Expected singleton
    	"""
    	return {
    		"bundle_id": self.bundle_id.id,
    		"name": self.name,
    		"password": self.password,
    		"confirm_password": self.confirm_password,
    		"partner_ids": [(6, 0, self.partner_ids.ids)],
    		"valid_until": self.valid_until,
    		"session_length": self.session_length,
    		"description": self.description,
    	}
