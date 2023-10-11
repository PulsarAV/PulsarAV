# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models

AUTO_ACCOUNT_SKR03 = {
    "l10n_de_skr03.account_1518": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_1718": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_2406": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_2408": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_ust_19_eu_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_2436": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3010": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3030": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3060": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_7_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3062": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3091": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3092": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3106": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3108": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3123": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_goods_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3125": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_ust_19_purchase_13b_werk_ausland_skr03"
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3150": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_ust_19_purchase_13b_werk_ausland_skr03",
            "l10n_de_skr03.tax_eu_19_purchase_goods_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3151": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_ust_19_purchase_13b_werk_ausland_skr03",
            "l10n_de_skr03.tax_eu_19_purchase_goods_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3300": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3400": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3420": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_7_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3425": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3430": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3435": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3440": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3553": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3710": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3714": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3715": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3717": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_7_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3718": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3720": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3724": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_7_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3725": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3731": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3734": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3736": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3738": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3741": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3743": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_7_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3744": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3750": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3754": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3755": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3760": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3780": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3784": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_7_skr03",
            "l10n_de_skr03.tax_vst_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3785": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3790": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_vst_19_skr03",
            "l10n_de_skr03.tax_vst_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3792": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_3793": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_19_purchase_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8125": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_sale_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": True,
    },
    "l10n_de_skr03.account_8191": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8196": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8300": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8310": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8315": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_ust_19_eu_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8400": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8516": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8519": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8576": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8579": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8591": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8595": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8611": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8613": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8630": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8640": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8710": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8720": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8724": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_sale_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8725": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_ust_eu_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8726": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_ust_19_eu_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8731": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8736": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_ust_19_eu_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8741": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_free_third_country_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8742": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_free_eu_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8743": {
        "datev_automatic_tax": ["l10n_de_skr03.tax_eu_sale_skr03"],
        "datev_automatic_account": True,
        "datev_vatid_required": True,
    },
    "l10n_de_skr03.account_8746": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8748": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8750": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8760": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8780": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8790": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8801": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8820": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8910": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8915": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8920": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8921": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8922": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8925": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8930": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8932": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8935": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8940": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_19_skr03",
            "l10n_de_skr03.tax_ust_19_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
    "l10n_de_skr03.account_8945": {
        "datev_automatic_tax": [
            "l10n_de_skr03.tax_ust_7_skr03",
            "l10n_de_skr03.tax_ust_7_taxinclusive_skr03",
        ],
        "datev_automatic_account": True,
        "datev_vatid_required": False,
    },
}


class AccountAccount(models.Model):
    _inherit = "account.account"

    def _set_account_autoaccount_skr03(self, company_id):
        for key, values in AUTO_ACCOUNT_SKR03.items():
            tax_keys = False
            template_id = self.env.ref(key)
            account_id = self.env["account.account"].search(
                [("name", "=", template_id.name), ("company_id", "=", company_id)]
            )
            if values["datev_automatic_tax"]:
                template_ids = []
                for val in values["datev_automatic_tax"]:
                    template_ids.append(self.env.ref(val).name)
                tax_ids = self.env["account.tax"].search(
                    [("name", "in", template_ids), ("company_id", "=", company_id)]
                )
                if tax_ids:
                    tax_keys = tax_ids.ids
            if tax_keys:
                account_id.write(
                    {
                        "datev_vatid_required": values["datev_vatid_required"],
                        "datev_automatic_account": values["datev_automatic_account"],
                        "datev_automatic_tax": [(6, 0, tax_keys)],
                    }
                )
