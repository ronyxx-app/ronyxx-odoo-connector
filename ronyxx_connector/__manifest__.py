# -*- coding: utf-8 -*-
{
    "name": "Ronyxx Connector",
    "summary": "Read-only access for Ronyxx in one click: ask your Odoo in plain words on WhatsApp, ChatGPT and Claude",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "author": "Ronyxx",
    "website": "https://ronyxx.com",
    "support": "support@ronyxx.com",
    "license": "LGPL-3",
    "description": """
Gives Ronyxx (ronyxx.com), an outside service that answers questions from your Odoo, read-only access: a group that
can only read the records Ronyxx answers from, a user in that group, and an API key shown once. Nothing is sent
anywhere by this app; Ronyxx reads your Odoo only after you paste the key into your Ronyxx account.
""",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/ronyxx_setup_views.xml",
    ],
    "images": ["static/description/banner.png", "static/description/screenshot_connect.png", "static/description/screenshot_ready.png"],
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": True,
}
