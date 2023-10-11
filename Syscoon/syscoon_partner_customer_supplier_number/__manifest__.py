# © 2023 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
{
    "name": "syscoon Partner Customer and Supplier Number ",
    "summary": "syscoon Partner Customer and Supplier Number ",
    "description": """
App adds two fields for external customer and supplier number inside res.partner.
There is the possibility, when activated in the settings,
that the customer number appears on invoices and refunds.
    """,
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "website": "https://syscoon.com",
    "category": "Accounting",
    "version": "16.0.0.0.1",
    "depends": ["l10n_din5008"],  # depends on l10n_din5008 bc of the invoice reports
    "data": ["views/res_partner_view.xml", "views/res_config_settings_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
