# © 2024 syscoon GmbH (<https://syscoon.com>)
# License OPL-1, See LICENSE file for full copyright and licensing details.

{
    "name": "syscoon Partner Debit and Credit Accounts Automation on Invoices",
    "version": "17.0.0.0.1",
    "author": "syscoon Estonia OÜ",
    "license": "OPL-1",
    "category": "Accounting",
    "website": "https://syscoon.com",
    "depends": ["syscoon_partner_accounts_automatic"],
    "description": """
If a new invoice is created, a new debit and credit account will be created automatically.
""",
    "data": [
        "data/automatic_mode.xml",
    ],
    "installable": True,
    "module_type": "official",
}
