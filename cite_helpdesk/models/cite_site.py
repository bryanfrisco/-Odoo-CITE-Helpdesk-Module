# -*- coding: utf-8 -*-
from odoo import fields, models


class CiteSite(models.Model):
    _name = "cite.site"
    _description = "CITE Site / Location"
    _order = "sequence, name"

    name = fields.Char(required=True)                      # "Head Office", "Site"
    code = fields.Char(required=True)                      # "HO", "ST"
    site_type = fields.Selection(
        [("ho", "Head Office"), ("site", "Site")],
        string="Site Type", required=True, default="site")
    company_id = fields.Many2one("res.company", string="Company", index=True,
                                 help="Kosongkan agar lokasi berlaku untuk "
                                      "semua company.")
    address = fields.Text()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    ticket_ids = fields.One2many("helpdesk.ticket", "site_id", string="Tickets")
    ticket_count = fields.Integer(compute="_compute_ticket_count")

    # Desain: cite.site adalah master data GLOBAL (Head Office / Site berlaku
    # lintas company, company_id boleh kosong). Karena itu kode wajib unik
    # secara global — bukan per-company. unique(code, company_id) sengaja TIDAK
    # dipakai karena NULL company_id akan lolos uniqueness di PostgreSQL.
    _sql_constraints = [
        ("code_uniq", "unique(code)", "Kode Site harus unik (global)."),
    ]

    def _compute_ticket_count(self):
        counts = dict(self.env["helpdesk.ticket"]._read_group(
            [("site_id", "in", self.ids)], ["site_id"], ["__count"]))
        for site in self:
            site.ticket_count = counts.get(site, 0)

    def action_view_tickets(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Tickets",
            "res_model": "helpdesk.ticket",
            "view_mode": "tree,kanban,form",
            "domain": [("site_id", "=", self.id)],
            "context": {"default_site_id": self.id},
        }
