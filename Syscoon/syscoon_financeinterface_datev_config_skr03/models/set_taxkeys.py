# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models

taxkeys_skr03 = {
    'l10n_de_skr03.tax_eu_19_purchase_skr03': 19,
    'l10n_de_skr03.tax_eu_7_purchase_skr03': 18,
    'l10n_de_skr03.tax_eu_sale_skr03': 10,
    'l10n_de_skr03.tax_export_skr03': 1,
    'l10n_de_skr03.tax_import_19_and_payable_skr03': 1,
    'l10n_de_skr03.tax_import_7_and_payable_skr03': 1,
    'l10n_de_skr03.tax_not_taxable_skr03': 1,
    'l10n_de_skr03.tax_ust_19_skr03': 3,
    'l10n_de_skr03.tax_ust_7_skr03': 2,
    'l10n_de_skr03.tax_vst_19_skr03': 9,
    'l10n_de_skr03.tax_vst_7_skr03': 8,
    'l10n_de_skr03.tax_ust_19_eu_skr03': 3,
    'l10n_de_skr03.tax_ust_eu_skr03': 2,
    'l10n_de_skr03.tax_free_eu_skr03': 10,
    'l10n_de_skr03.tax_free_third_country_skr03': 1,
    'l10n_de_skr03.tax_eu_19_purchase_goods_skr03': 94,
    'l10n_de_skr03.tax_vst_ust_19_purchase_13b_werk_ausland_skr03': 91,
    'l10n_de_skr03.tax_vst_19_taxinclusive_skr03': 9,
    'l10n_de_skr03.tax_ust_19_taxinclusive_skr03': 3,
    'l10n_de_skr03.tax_vst_7_taxinclusive_skr03': 8,
    'l10n_de_skr03.tax_ust_7_taxinclusive_skr03': 2,
}


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _set_taxkeys_skr03(self, company_id):
        for key, value in taxkeys_skr03.items():
            template_id = self.env.ref(key)
            tax_ids = self.env["account.tax"].search(
                ["&", ("name", "=", template_id.name), ("company_id", "=", company_id)]
            )
            tax_ids.update({"datev_tax_key": value})
        tax_ids_to_deactivate = self.env["account.tax"].search(
            [("datev_tax_key", "=", "0")]
        )
        tax_ids_to_deactivate.update({"active": False})
