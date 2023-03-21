# -*- coding: utf-8 -*-
{
    "name": "Password Manager",
    "version": "16.0.1.1.5",
    "category": "Extra Tools",
    "author": "faOtools",
    "website": "https://faotools.com/apps/16.0/password-manager-710",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
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
        "wizard/update_password_tag.xml",
        "wizard/update_password_partner.xml",
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
    "summary": "The tool to safely keep passwords in Odoo for shared use. Shared vaults. Password generator. Team passwords. Password keeper. Encryption. Keypass. Password checkup",
    "description": """For the full details look at static/description/index.html
* Features * 
- Shared use, encryption, and protection of passwords
- &lt;i class=&#39;fa fa-gears&#39;&gt;&lt;/i&gt; Custom attributes for Odoo passwords 
- Duplicates detection and passwords merging
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "159.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=103&ticket_version=16.0&url_type_id=3",
}