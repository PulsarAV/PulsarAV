# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Partner Credit Accounts Automation on Purchase Orders",
    "version": "17.0.0.0.1",
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "category": "Accounting",
    "website": "https://syscoon.com",
    "depends": ["syscoon_partner_accounts_automatic", "purchase"],
    "description": """
If a purchase order is confirmed, a new credit account will be created automatically.
""",
    "data": [
        "data/automatic_mode.xml",
    ],
    "installable": True,
    "module_type": "official",
}
