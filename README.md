# Ronyxx Connector for Odoo

A free Odoo app that gives [Ronyxx](https://ronyxx.com) read-only access in one click. Ronyxx answers your team's
questions with exact figures from your own Odoo, on WhatsApp, ChatGPT and Claude.

Under **Settings > Connect Ronyxx**, one button creates:

- a group, **Ronyxx read-only**, that can read the records Ronyxx answers from and can't write, create or delete;
- a user, **Ronyxx (read-only)**, in that group, with no password;
- an API key for that user, shown once with the Odoo address and database name, to paste into Ronyxx.

Works on Odoo 16, 17, 18 and 19 (one branch per version), Community and Enterprise, on Odoo.sh and your own server.
Odoo Online can't install outside apps; there, Ronyxx connects with an API key from an existing login.

On a paid Odoo plan the Ronyxx user counts as one more Odoo user. Uninstalling the app archives the user and deletes
its keys. This app sends nothing anywhere; Ronyxx reads your Odoo only after you paste the key into your account.

License: LGPL-3. Support: support@ronyxx.com
