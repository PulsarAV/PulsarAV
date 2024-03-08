# -*- coding: utf-8 -*-
{
    "name": "Password Manager",
    "version": "17.0.1.3.2",
    "category": "Extra Tools",
    "author": "faOtools",
    "website": "https://faotools.com/apps/17.0/password-manager-819",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail",
        "portal"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/mail_data.xml",
        "data/cron.xml",
        "views/res_config_settings.xml",
        "wizard/bundle_login.xml",
        "wizard/password_generator.xml",
        "views/password_key.xml",
        "views/password_bundle.xml",
        "views/password_tag.xml",
        "views/res_partner.xml",
        "views/portal_password_bundle.xml",
        "views/templates.xml",
        "wizard/update_password_tag.xml",
        "wizard/update_password_partner.xml",
        "wizard/share_portal_password.xml",
        "wizard/odoo_password_merge.xml",
        "views/menu.xml"
    ],
    "assets": {
        "web.assets_backend": [
                "odoo_password_manager/static/src/views/kanban/*.scss",
                "odoo_password_manager/static/src/views/kanban/*.xml",
                "odoo_password_manager/static/src/views/kanban/*.js",
                "odoo_password_manager/static/src/views/bundle_kanban/*.js",
                "odoo_password_manager/static/src/views/search/*.js",
                "odoo_password_manager/static/src/views/fields/password_copy_field/*.scss",
                "odoo_password_manager/static/src/views/fields/password_copy_field/*.xml",
                "odoo_password_manager/static/src/views/fields/password_copy_field/*.js",
                "odoo_password_manager/static/src/views/fields/password_duplicates/*.scss",
                "odoo_password_manager/static/src/views/fields/password_duplicates/*.xml",
                "odoo_password_manager/static/src/views/fields/password_duplicates/*.js",
                "odoo_password_manager/static/src/views/dialogs/password_export_dialog/*.js",
                "odoo_password_manager/static/src/views/dialogs/password_login_dialog/*.js",
                "odoo_password_manager/static/src/views/dialogs/password_login_dialog/*.xml",
                "odoo_password_manager/static/src/components/password_manager/*.xml",
                "odoo_password_manager/static/src/components/password_manager/*.js",
                "odoo_password_manager/static/src/components/pwm_jstree_container/*.xml",
                "odoo_password_manager/static/src/components/pwm_jstree_container/*.js",
                "odoo_password_manager/static/src/components/password_preview/*.xml",
                "odoo_password_manager/static/src/components/password_preview/*.js",
                "odoo_password_manager/static/src/components/password_preview/*.scss",
                "odoo_password_manager/static/src/components/password_navigation/*.xml",
                "odoo_password_manager/static/src/components/password_navigation/*.js"
        ],
        "web.assets_frontend": [
                "odoo_password_manager/static/src/components/portal_password/*.xml",
                "odoo_password_manager/static/src/components/portal_password/*.js",
                "odoo_password_manager/static/src/js/vault_login.js",
                "odoo_password_manager/static/src/js/vault_login.scss"
        ]
},
    "demo": [
        
    ],
    "external_dependencies": {
        "python": [
                "zxcvbn",
                "cryptography"
        ]
},
    "summary": "The tool to safely keep passwords in Odoo for shared use. Shared vaults. Password generator. Team passwords. Shared passwords. Password keeper. Encryption. Keypass. Password checkup",
    "description": """For the full details look at static/description/index.html
* Features * 
- Shared use, encryption, and protection of passwords
- Portal vaults
- &lt;i class=&#39;fa fa-gears&#39;&gt;&lt;/i&gt; Custom attributes for Odoo passwords 
- Duplicates detection and passwords merging
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "198.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=103&ticket_version=17.0&url_type_id=3",
}