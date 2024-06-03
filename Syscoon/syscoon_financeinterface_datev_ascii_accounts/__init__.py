# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, SUPERUSER_ID

from . import models
from . import wizards


def _init_ascii_export_accounts(env):
    model = env.ref("account.model_res_partner")
    field = env["ir.model.fields"].search(
        [("name", "=", "datev_exported"), ("model_id", "=", model.id)]
    )
    for company in env["res.company"].search([]):
        for partner in env["res.partner"].search([]):
            env["ir.property"].create(
                {
                    "name": "datev_exported",
                    "fields_id": field.id,
                    "res_id": "res.partner," + str(partner.id),
                    "value_text": "false",
                    "company_id": company.id,
                    "type": "selection",
                }
            )
