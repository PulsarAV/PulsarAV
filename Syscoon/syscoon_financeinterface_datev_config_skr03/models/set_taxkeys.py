# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

from odoo import models

TAXKEYS_SKR03 = {
    "tax_eu_19_purchase_skr03": 701,
    "tax_eu_7_purchase_skr03": 702,
    "tax_eu_sale_skr03": 231,
    "tax_export_skr03": 173,
    "tax_import_19_and_payable_skr03": 1,
    "tax_import_7_and_payable_skr03": 1,
    "tax_not_taxable_skr03": 260,
    "tax_ust_19_skr03": 101,
    "tax_ust_7_skr03": 102,
    "tax_vst_19_skr03": 401,
    "tax_vst_7_skr03": 402,
    "tax_ust_19_eu_skr03": 221,
    "tax_ust_eu_skr03": 222,
    "tax_free_eu_skr03": 270,
    "tax_free_third_country_skr03": 191,
    "tax_eu_19_purchase_goods_skr03": 506,
    "tax_vst_ust_19_purchase_13b_werk_ausland_skr03": 511,
    "tax_vst_19_taxinclusive_skr03": 401,
    "tax_ust_19_taxinclusive_skr03": 101,
    "tax_vst_7_taxinclusive_skr03": 402,
    "tax_ust_7_taxinclusive_skr03": 102,
}


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _set_taxkeys_skr03(self, company_id):
        for key, value in TAXKEYS_SKR03.items():
            name = f"account.{company_id}_{key}"
            tax_id = self.env.ref(name)
            tax_id.write({"datev_tax_key": value})
        tax_ids_to_deactivate = self.env["account.tax"].search(
            [("datev_tax_key", "=", "0")]
        )
        tax_ids_to_deactivate.write({"active": False})
