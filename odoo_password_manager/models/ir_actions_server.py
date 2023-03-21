# -*- coding: utf-8 -*-

from odoo import fields, models


class ir_actions_server(models.Model):
    """
    Overwrite to make it possible to run certain actions under the readonly internal user
    """
    _inherit = "ir.actions.server"

    safe_pwm_action = fields.Boolean(string="Safe PWM Action")

    def run(self):
        """
        Overwrite to check password.key separately, since internal readonly users can make certain actions
        The idea is that readonly users, for example, can add to favorite. In that case, the action is executed
        under sudo
        """
        for action in self.sudo():
            if action.model_name == "password.key" and action.safe_pwm_action \
                    and self.env.user.has_group("base.group_user"):
                res = super(ir_actions_server, action.sudo()).run()
            else:
                res = super(ir_actions_server, action).run()
        return res
