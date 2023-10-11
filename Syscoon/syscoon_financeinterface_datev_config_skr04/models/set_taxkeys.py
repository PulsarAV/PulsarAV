# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models

taxkeys_skr04 = {
    'l10n_de_skr04.tax_eu_19_purchase_skr04': 19,
    'l10n_de_skr04.tax_eu_7_purchase_skr04': 18,
    'l10n_de_skr04.tax_eu_sale_skr04': 10,
    'l10n_de_skr04.tax_export_skr04': 1,
    'l10n_de_skr04.tax_import_19_and_payable_skr04': 1,
    'l10n_de_skr04.tax_import_7_and_payable_skr04': 1,
    'l10n_de_skr04.tax_not_taxable_skr04': 1,
    'l10n_de_skr04.tax_ust_19_skr04': 3,
    'l10n_de_skr04.tax_ust_7_skr04': 2,
    'l10n_de_skr04.tax_vst_19_skr04': 9,
    'l10n_de_skr04.tax_vst_7_skr04': 8,
    'l10n_de_skr04.tax_ust_19_eu_skr04': 3,
    'l10n_de_skr04.tax_ust_eu_skr04': 2,
    'l10n_de_skr04.tax_free_eu_skr04': 10,
    'l10n_de_skr04.tax_free_third_country_skr04': 1,
    'l10n_de_skr04.tax_eu_19_purchase_goods_skr04': 94,
    'l10n_de_skr04.tax_vst_ust_19_purchase_13b_werk_ausland_skr04': 91,
    'l10n_de_skr04.tax_vst_19_taxinclusive_skr04': 9,
    'l10n_de_skr04.tax_ust_19_taxinclusive_skr04': 3,
    'l10n_de_skr04.tax_vst_7_taxinclusive_skr04': 8,
    'l10n_de_skr04.tax_ust_7_taxinclusive_skr04': 2,

}


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _set_taxkeys_skr04(self, company_id):
        for key, value in taxkeys_skr04.items():
            template_id = self.env.ref(key)
            template_id = self.env.ref(key)
            tax_ids = self.env["account.tax"].search(
                ["&", ("name", "=", template_id.name), ("company_id", "=", company_id)]
            )
            tax_ids.update({"datev_tax_key": value})
        tax_ids_to_deactivate = self.env["account.tax"].search(
            [("datev_tax_key", "=", "0")]
        )
        tax_ids_to_deactivate.update({"active": False})
