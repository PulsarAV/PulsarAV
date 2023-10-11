from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    datev_cost_center = fields.Selection(
        [("add_to_kost1", "add to Datev KOST1"), ("add_to_kost2", "add to Datev KOST2")]
    )

    @api.onchange('datev_cost_center')
    def _compute_datev_cost_centers(self):
        if self.datev_cost_center:
            check_cost_center = self.env["account.analytic.plan"].search(
                [("datev_cost_center", "=", self.datev_cost_center)]
            )
            if check_cost_center:
                self.datev_cost_center = False
                raise UserError(
                    _("Cost Center Already Assigned in " + check_cost_center.name)
                )
