# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api

from .models.ronyxx_setup import GROUP_NAME, LOGIN


def uninstall_hook(*args):
    """On uninstall: the Ronyxx user is archived (an archived user's API keys stop working at once), its keys are
    deleted, and the group's access rights and rules go. Odoo 16 calls this with (cr, registry), 17 and later with env."""
    if len(args) == 1:
        env = args[0]
    else:
        env = api.Environment(args[0], SUPERUSER_ID, {})
    Users = env["res.users"].sudo().with_context(active_test=False)
    user = Users.search([("login", "=", LOGIN)], limit=1)
    if user:
        env["res.users.apikeys"].sudo().search([("user_id", "=", user.id)]).unlink()
        user.write({"active": False})
    group = env["res.groups"].sudo().search([("name", "=", GROUP_NAME)], limit=1)
    if group:
        env["ir.rule"].sudo().with_context(active_test=False).search([("groups", "in", group.ids)]).unlink()
        env["ir.model.access"].sudo().search([("group_id", "=", group.id)]).unlink()
