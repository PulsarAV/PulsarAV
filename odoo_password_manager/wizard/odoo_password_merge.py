# -*- coding: utf-8 -*-

from odoo import fields, models


class odoo_password_merge(models.TransientModel):
    """
    The wizard to merge passwords to a main one and archive others
    """
    _name = "odoo.password.merge"
    _inherit = "password.key.mass.update"
    _description = "Passwords merge"

    main_password_id = fields.Many2one(
        "password.key",
        string="Password to merge",
        required=True,
        help="This password will be updated after merging. Its missing values would be copied from merged passwords",
    )

    def _update_passwords(self, password_ids):
        """
        The method to prepare new vals for partner

        Args:
         * password_ids - password.key recordset (initial ones!)

        Methods:
         * _get_merged_data
        """
        main_password = self.main_password_id
        # main password is always the first
        merged_password_ids = self.password_ids - main_password
        all_password_ids = main_password + merged_password_ids
        new_data = all_password_ids._get_merged_data()
        main_password.write(new_data)
        merged_password_ids.write({"active": False})
