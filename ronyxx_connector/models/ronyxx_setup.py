# -*- coding: utf-8 -*-
import datetime
import inspect
import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError
from odoo.addons.base.models.res_users import check_identity

from .ronyxx_models import ACCESS_MODELS, RULE_MODELS

_logger = logging.getLogger(__name__)

GROUP_NAME = "Ronyxx read-only"
LOGIN = "ronyxx-readonly"
KEY_NAME = "Ronyxx"
ALL_RECORDS = "[(1, '=', 1)]"


def _groups_field(users):
    """The user's groups field: group_ids from Odoo 19, groups_id before."""
    return "group_ids" if "group_ids" in users._fields else "groups_id"


class RonyxxSetup(models.TransientModel):
    _name = "ronyxx.setup"
    _description = "Connect Ronyxx (read-only access)"

    key_days = fields.Selection(
        [("90", "90 days"), ("365", "1 year"), ("0", "No end date")],
        string="API key valid for", default="365", required=True,
        help="Odoo 18 and later give API keys an end date. Ronyxx emails the owner before the key ends. "
             "Odoo 16 and 17 keep keys until they are deleted.")
    replace_old_keys = fields.Boolean(
        string="Delete the Ronyxx user's older keys",
        help="Tick this when you are replacing a key: the old one stops working at once, so paste the new key in "
             "Ronyxx straight away.")
    odoo_url = fields.Char("Odoo address", readonly=True)
    database = fields.Char("Database", readonly=True)
    login = fields.Char("Login", readonly=True)
    api_key = fields.Char("API key", readonly=True)
    key_ends = fields.Char("Key valid until", readonly=True)
    models_count = fields.Integer("Kinds of records Ronyxx can read", readonly=True)

    def _check_admin(self):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only an Odoo administrator can connect Ronyxx."))

    def _ensure_group(self):
        Group = self.env["res.groups"].sudo()
        group = Group.search([("name", "=", GROUP_NAME)], limit=1)
        if not group:
            vals = {"name": GROUP_NAME}
            if "comment" in Group._fields:
                vals["comment"] = "Made by the Ronyxx Connector app: reads the records Ronyxx answers from, and nothing else."
            group = Group.create(vals)
        return group

    def _ensure_access(self, group):
        """Read, never write, create or delete: one access right per model this database has, and the
        read-every-record rules."""
        IrModel = self.env["ir.model"].sudo()
        Access = self.env["ir.model.access"].sudo()
        Rule = self.env["ir.rule"].sudo()
        present = IrModel.search([("model", "in", list(ACCESS_MODELS))])
        for model in present:
            vals = {"name": "%s - %s" % (GROUP_NAME, model.model), "model_id": model.id, "group_id": group.id,
                    "perm_read": True, "perm_write": False, "perm_create": False, "perm_unlink": False}
            row = Access.search([("group_id", "=", group.id), ("model_id", "=", model.id)], limit=1)
            if row:
                row.write(vals)
            else:
                Access.create(vals)
        for model in present.filtered(lambda m: m.model in RULE_MODELS):
            vals = {"name": "%s - all records - %s" % (GROUP_NAME, model.model), "model_id": model.id,
                    "groups": [(6, 0, [group.id])], "domain_force": ALL_RECORDS,
                    "perm_read": True, "perm_write": False, "perm_create": False, "perm_unlink": False}
            rule = Rule.with_context(active_test=False).search(
                [("model_id", "=", model.id), ("groups", "in", group.ids), ("domain_force", "=", ALL_RECORDS)], limit=1)
            if rule:
                rule.write(dict(vals, active=True))
            else:
                Rule.create(vals)
        return len(present)

    def _ensure_user(self, group):
        Users = self.env["res.users"].sudo().with_context(active_test=False, no_reset_password=True)
        gf = _groups_field(Users)
        internal = self.env.ref("base.group_user")
        companies = self.env["res.company"].sudo().search([])
        vals = {
            "name": "Ronyxx (read-only)",
            gf: [(6, 0, [internal.id, group.id])],
            "company_ids": [(6, 0, companies.ids)],
            "company_id": self.env.company.id,
            "active": True,
        }
        user = Users.search([("login", "=", LOGIN)], limit=1)
        if user:
            user.write(vals)
        else:
            user = Users.create(dict(vals, login=LOGIN))
        return user

    def _make_key(self, user):
        keys = self.env["res.users.apikeys"].with_user(user).sudo()
        if self.replace_old_keys:
            self.env["res.users.apikeys"].sudo().search([("user_id", "=", user.id), ("name", "=", KEY_NAME)]).unlink()
        days = int(self.key_days or "0")
        if "expiration_date" in inspect.signature(keys._generate).parameters:
            ends = datetime.datetime.now() + datetime.timedelta(days=days) if days else None
            key = keys._generate("rpc", KEY_NAME, ends)
            return key, (fields.Date.to_string(ends.date()) if ends else _("No end date"))
        return keys._generate("rpc", KEY_NAME), _("No end date (your Odoo version keeps keys until they are deleted)")

    @check_identity
    def action_setup(self):
        self.ensure_one()
        self._check_admin()
        group = self._ensure_group()
        count = self._ensure_access(group)
        user = self._ensure_user(group)
        key, ends = self._make_key(user)
        self.write({
            "odoo_url": self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
            "database": self.env.cr.dbname,
            "login": LOGIN,
            "api_key": key,
            "key_ends": ends,
            "models_count": count,
        })
        _logger.info("Ronyxx read-only access set up by %s: %s models", self.env.user.login, count)
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "views": [(self.env.ref("ronyxx_connector.ronyxx_setup_view_done").id, "form")],
            "target": "new",
            "name": _("Ronyxx access is ready"),
        }
