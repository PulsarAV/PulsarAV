# -*- coding: utf-8 -*-

from odoo import api, fields, models


class password_key_mass_update(models.TransientModel):
    """
    The wizard to be inherited in any update wizard that assumes writing mass values in passwords
    """
    _name = "password.key.mass.update"
    _description = "Password Update"

    password_ids = fields.Many2many("password.key", string="Updated passwords")

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overwrite to trigger passwords update
        The idea is to use standard 'Save' buttons and do not introduce its own footer for each mass action wizard

        Methods:
         * action_update_passwords
        """
        wizards = super(password_key_mass_update, self).create(vals_list)
        wizards.action_update_passwords()
        return wizards

    def action_update_passwords(self):
        """
        The method to update passwords in batch

        Methods:
         * _update_passwords
        """
        for wiz in self:
            if wiz.password_ids:
                wiz._update_passwords(wiz.password_ids)

    def _update_passwords(self, password_ids):
        """
        Dummy method to prepare values
        It is to be inherited in a real update wizard

        Args:
         * password_ids - password.key recordset
        """
        pass
