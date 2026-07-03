# -*- coding: utf-8 -*-
from odoo import fields, models


class CiteTicketRejectWizard(models.TransientModel):
    _name = "cite.ticket.reject.wizard"
    _description = "CITE Ticket Reject Wizard"

    ticket_id = fields.Many2one("helpdesk.ticket", required=True,
                                readonly=True)
    level = fields.Selection([("admin", "Administrator"),
                            
                            
                            ("heidi", "Heidi Lianawaty Lisan")],
                            required=True, readonly=True)
    reason = fields.Text(string="Alasan Penolakan", required=True)

    def action_confirm(self):
        self.ensure_one()
        self.ticket_id._apply_rejection(self.level, self.reason)
        return {"type": "ir.actions.act_window_close"}
