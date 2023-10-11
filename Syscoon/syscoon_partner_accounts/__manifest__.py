# © 2023 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.
{
    "name": "syscoon Partner Debit and Credit Accounts",
    "version": "16.0.0.0.8",
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "category": "Accounting",
    "website": "https://syscoon.com",
    "depends": ["syscoon_partner_customer_supplier_number"],
    "description": """
        If a partner is created a new debit and/or credit account
        will be created following a
        sequence that can be created individually per company.
    """,
    "data": [
        "data/partner_account_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner.xml",
    ],
    "active": False,
    "installable": True,
}
