# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import CiteHelpdeskCommon


@tagged("post_install", "-at_install")
class TestApprovalFlow(CiteHelpdeskCommon):

    def _create_approval_ticket(self):
        return self._create_ticket(
            name="Odoo access request",
            cite_category_id=self.cat_access.id,
            cite_subcategory_id=self.sub_acc_odoo.id,
            impact="individual",
            urgency="request",
        )

    def test_non_approval_ticket_goes_open(self):
        """Proses A — kategori operasional langsung Open, tanpa approval."""
        ticket = self._create_ticket()
        self.assertFalse(ticket.require_approval)
        self.assertEqual(ticket.approval_status, "not_required")
        self.assertEqual(ticket.cite_stage_code, "open")

    def test_approval_ticket_starts_pending_admin(self):
        """Proses B — kategori Access masuk Pending Administrator Approval."""
        ticket = self._create_approval_ticket()
        self.assertTrue(ticket.require_approval)
        self.assertEqual(ticket.cite_stage_code, "pending_admin")
        self.assertEqual(ticket.admin_approval_status, "pending")
        self.assertEqual(ticket.heidi_approval_status, "waiting")
        self.assertEqual(ticket.approval_status, "in_review")

    def test_subcategory_override_requires_approval(self):
        """Software Installation memaksa approval meski Software tidak."""
        ticket = self._create_ticket(
            cite_category_id=self.cat_software.id,
            cite_subcategory_id=self.sub_sw_install.id,
        )
        self.assertTrue(ticket.require_approval)
        self.assertEqual(ticket.cite_stage_code, "pending_admin")

    def test_guard_blocks_processing_without_approval(self):
        """13.3-1 — tiket ber-approval tidak bisa dipindahkan ke stage
        proses sebelum fully approved (anti-bypass server-side)."""
        ticket = self._create_approval_ticket()
        in_progress = self.env.ref("cite_helpdesk.stage_in_progress")
        with self.assertRaises(ValidationError):
            ticket.with_user(self.user_agent).write(
                {"stage_id": in_progress.id})

    def test_full_approval_path(self):
        ticket = self._create_approval_ticket()
        ticket.with_user(self.user_admin_l1).action_admin_approve()
        self.assertEqual(ticket.admin_approval_status, "approved")
        self.assertEqual(ticket.heidi_approval_status, "pending")
        self.assertEqual(ticket.cite_stage_code, "pending_heidi")

        ticket.with_user(self.user_heidi).action_heidi_approve()
        self.assertEqual(ticket.approval_status, "fully_approved")
        self.assertEqual(ticket.cite_stage_code, "assigned")

    def test_heidi_cannot_skip_level_one(self):
        ticket = self._create_approval_ticket()
        with self.assertRaises(ValidationError):
            ticket.with_user(self.user_heidi).action_heidi_approve()

    def test_admin_reject_locks_ticket(self):
        ticket = self._create_approval_ticket()
        ticket.with_user(self.user_admin_l1)._apply_rejection(
            "admin", "Tidak sesuai kebijakan.")
        self.assertEqual(ticket.approval_status, "rejected")
        self.assertEqual(ticket.cite_stage_code, "rejected")
        self.assertEqual(ticket.rejection_reason, "Tidak sesuai kebijakan.")
        # Tiket terkunci readonly
        with self.assertRaises(UserError):
            ticket.with_user(self.user_agent).write({"name": "ubah subject"})

    def test_segregation_of_duty(self):
        """Approver tidak boleh approve tiket buatannya sendiri."""
        ticket = self.env["helpdesk.ticket"].with_user(
            self.user_admin_l1).create({
                "name": "Self-created access request",
                "team_id": self.team.id,
                "partner_id": self.partner.id,
                "company_id": self.env.company.id,
                "site_id": self.site.id,
                "cite_category_id": self.cat_access.id,
                "cite_subcategory_id": self.sub_acc_odoo.id,
                "impact": "individual",
                "urgency": "request",
            })
        with self.assertRaises(UserError):
            ticket.with_user(self.user_admin_l1).action_admin_approve()

    def test_agent_cannot_approve(self):
        ticket = self._create_approval_ticket()
        with self.assertRaises(Exception):
            ticket.with_user(self.user_agent).action_admin_approve()

    def test_unlink_forbidden(self):
        ticket = self._create_ticket()
        with self.assertRaises(UserError):
            ticket.with_user(self.user_agent).unlink()
