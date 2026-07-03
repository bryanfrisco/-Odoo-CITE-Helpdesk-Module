# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    asset_code = fields.Char(string="Asset Code", copy=False, index=True)
    brand = fields.Char()
    site_id = fields.Many2one("cite.site", string="Lokasi")
    warranty_end_date = fields.Date()
    asset_status = fields.Selection([
        ("in_use", "In Use"), ("spare", "Spare"), ("repair", "Under Repair"),
        ("disposed", "Disposed"), ("lost", "Lost")], default="in_use",
        tracking=True)
    ticket_ids = fields.One2many("helpdesk.ticket", "equipment_id",
                                 string="Helpdesk Tickets")
    ticket_count = fields.Integer(compute="_compute_ticket_count")

    _sql_constraints = [
        ("asset_code_uniq", "unique(asset_code)", "Asset Code harus unik."),
    ]

    def _compute_ticket_count(self):
        counts = dict(self.env["helpdesk.ticket"]._read_group(
            [("equipment_id", "in", self.ids)], ["equipment_id"], ["__count"]))
        for equipment in self:
            equipment.ticket_count = counts.get(equipment, 0)

    def action_view_tickets(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Tickets"),
            "res_model": "helpdesk.ticket",
            "view_mode": "tree,kanban,form",
            "domain": [("equipment_id", "=", self.id)],
            "context": {"default_equipment_id": self.id},
        }

    @api.model
    def _cron_warranty_alert(self):
        """AA-13 — warning aset dengan garansi berakhir <= 30 hari."""
        limit = fields.Date.today() + timedelta(days=30)
        equipments = self.search([
            ("warranty_end_date", "!=", False),
            ("warranty_end_date", "<=", limit),
            ("asset_status", "in", ("in_use", "spare", "repair")),
        ])
        admin_group = self.env.ref("cite_helpdesk.group_it_administrator",
                                   raise_if_not_found=False)
        if not admin_group or not admin_group.users:
            return
        user = admin_group.users[0]
        for equipment in equipments:
            already = self.env["mail.activity"].search_count([
                ("res_model", "=", "maintenance.equipment"),
                ("res_id", "=", equipment.id),
                ("summary", "like", "Warranty expiring"),
            ])
            if not already:
                equipment.activity_schedule(
                    "mail.mail_activity_data_todo", user_id=user.id,
                    summary=_("Warranty expiring: %s (%s)",
                              equipment.name, equipment.asset_code or "-"),
                    note=_("Garansi berakhir pada %s.",
                           equipment.warranty_end_date))
