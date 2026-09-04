# -*- coding: utf-8 -*-
"""Regresi: modul CITE tidak boleh menyentuh tiket helpdesk tim lain.

Database produksi (stargo.odoo.com) memakai helpdesk bawaan untuk tim non-CITE.
Sampai 17.0.1.5.0 override create()/write() CITE berjalan untuk SEMUA tiket,
sehingga tiket tim lain ikut mendapat nomor IT-YYYY-XXXXX + stage CITE.
"""
from .common import CiteHelpdeskCommon


class TestForeignHelpdeskUntouched(CiteHelpdeskCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.foreign_team = cls.env["helpdesk.team"].create({
            "name": "Stargo Helpdesk (test)",
            "cite_team": False,
        })
        cls.foreign_stage = cls.env["helpdesk.stage"].create({
            "name": "Foreign New",
            "sequence": 1,
            "team_ids": [(4, cls.foreign_team.id)],
        })

    def _create_foreign_ticket(self, **extra):
        vals = {"name": "Tiket tim lain", "team_id": self.foreign_team.id}
        vals.update(extra)
        return self.env["helpdesk.ticket"].create(vals)

    def test_foreign_ticket_keeps_native_ref(self):
        """Nomor tiket tim lain tidak boleh ditimpa sequence CITE."""
        ticket = self._create_foreign_ticket()
        self.assertFalse(ticket.cite_ticket)
        self.assertNotRegex(ticket.ticket_ref or "", r"^IT-\d{4}-\d{5}$")

    def test_foreign_ticket_keeps_native_stage(self):
        """Stage tiket tim lain tidak boleh dipaksa ke stage CITE."""
        ticket = self._create_foreign_ticket()
        cite_stages = self.env["helpdesk.stage"].search(
            [("team_ids", "in", self.team.ids)])
        self.assertNotIn(ticket.stage_id, cite_stages)
        self.assertFalse(ticket.cite_stage_code)

    def test_foreign_ticket_no_cite_mailbox_follower(self):
        """Mailbox pusat CITE tidak ikut jadi follower tiket tim lain."""
        mailbox = self.env.ref("cite_helpdesk.partner_cite_mailbox",
                               raise_if_not_found=False)
        if not mailbox:
            self.skipTest("mailbox CITE tidak terpasang")
        ticket = self._create_foreign_ticket()
        self.assertNotIn(mailbox, ticket.message_partner_ids)

    def test_foreign_ticket_deletable(self):
        """Guard audit-trail CITE tidak boleh mengunci tiket tim lain."""
        ticket = self._create_foreign_ticket()
        ticket.with_user(self.user_agent).unlink()
        self.assertFalse(ticket.exists())

    def test_cite_ticket_still_numbered(self):
        """Tiket CITE tetap memakai penomoran & stage CITE."""
        ticket = self._create_ticket()
        self.assertTrue(ticket.cite_ticket)
        self.assertRegex(ticket.ticket_ref, r"^IT-\d{4}-\d{5}$")
        self.assertEqual(ticket.cite_stage_code, "open")

    def test_repair_foreign_ticket(self):
        """Repair mengembalikan nomor & stage tiket tim lain yang ter-cap."""
        ticket = self._create_foreign_ticket()
        native_ref = ticket.ticket_ref
        # Simulasi kerusakan versi lama.
        ticket.write({
            "ticket_ref": "IT-2026-09999",
            "stage_id": self.env.ref("cite_helpdesk.stage_open").id,
        })
        self.env["helpdesk.ticket"]._cite_repair_foreign_tickets()
        self.assertNotEqual(ticket.ticket_ref, "IT-2026-09999")
        self.assertNotEqual(ticket.ticket_ref, native_ref,
                            "nomor baru diambil dari sequence native")
        # Kembali ke stage milik tim tiket itu sendiri, bukan stage CITE.
        self.assertIn(self.foreign_team, ticket.stage_id.team_ids)
        self.assertFalse(ticket.cite_stage_code)

    def test_foreign_ticket_company_follows_team(self):
        """Tiket tim lain tanpa company eksplisit tetap ikut company tim.

        Regresi form website helpdesk bawaan (Stargo): company kosong membuat
        constraint native _check_partner_id_has_the_same_company menolak
        submit dengan "The customer cannot belong to a different company
        than the ticket."
        """
        partner = self.env["res.partner"].create({
            "name": "Requester Stargo",
            "email": "requester.stargo@example.com",
            "company_id": self.env.company.id,
        })
        ticket = self._create_foreign_ticket(partner_id=partner.id)
        self.assertTrue(ticket.company_id)
        self.assertEqual(ticket.company_id, self.foreign_team.company_id)

    def test_cite_ticket_keeps_chosen_company(self):
        """Company pilihan portal CITE tidak boleh ditimpa company tim."""
        ticket = self._create_ticket()
        self.assertEqual(ticket.company_id, self.env.company)

    def test_foreign_ticket_priority_stays_manual(self):
        """Agen helpdesk lain tetap bisa mengatur priority sendiri."""
        ticket = self._create_foreign_ticket()
        ticket.priority = "3"
        self.assertEqual(ticket.priority, "3")
        ticket.write({"priority": "1"})
        self.assertEqual(ticket.priority, "1")

    def test_foreign_form_has_no_cite_description(self):
        """Form tim lain tidak ikut terisi template deskripsi CITE."""
        defaults = self.env["helpdesk.ticket"].with_context(
            default_team_id=self.foreign_team.id).default_get(
                ["description", "partner_id"])
        self.assertFalse(defaults.get("description"))
        self.assertFalse(defaults.get("partner_id"))

    def test_cite_form_keeps_prefill(self):
        """Form tim CITE tetap mendapat template deskripsi & requester."""
        defaults = self.env["helpdesk.ticket"].with_context(
            default_team_id=self.team.id).default_get(
                ["description", "partner_id"])
        self.assertTrue(defaults.get("description"))
        self.assertTrue(defaults.get("partner_id"))

    def test_cite_priority_cannot_be_overridden(self):
        """Priority tiket CITE tetap turunan impact x urgency (anti-bypass)."""
        ticket = self._create_ticket(impact="individual", urgency="request")
        self.assertEqual(ticket.priority, "0")
        ticket.write({"priority": "3"})
        self.assertEqual(ticket.priority, "0")

    def test_approver_rule_does_not_widen_foreign_access(self):
        """RR-03 tidak boleh membuka tiket helpdesk lain yang ditutup native.

        Tim dengan privacy_visibility='invited_internal' hanya terlihat oleh
        anggotanya menurut record rule native. Approver L2 CITE bukan anggota,
        jadi tiket tim itu harus tetap tertutup — sebelum 17.0.1.5.3 domain
        RR-03 [(1,'=',1)] justru membukanya.
        """
        self.foreign_team.privacy_visibility = "invited_internal"
        foreign = self._create_foreign_ticket()
        cite = self._create_ticket()
        readable = self.env["helpdesk.ticket"].with_user(
            self.user_heidi).search([("id", "in", (foreign | cite).ids)])
        self.assertIn(cite, readable, "tiket CITE tetap terbaca approver L2")
        self.assertNotIn(foreign, readable)

    def test_cite_activity_on_new_ticket(self):
        """Tiket CITE baru memunculkan activity, bukan email saja."""
        ticket = self._create_ticket()
        act_type = self.env.ref("cite_helpdesk.mail_act_new_ticket")
        self.assertTrue(
            ticket.activity_ids.filtered(
                lambda a: a.activity_type_id == act_type),
            "activity 'Tiket Baru' harus terjadwal untuk tim penanggung jawab")

    def test_cite_activity_on_assign(self):
        """Penugasan memunculkan activity untuk agen yang ditunjuk."""
        ticket = self._create_ticket()
        ticket.write({"user_id": self.user_agent.id})
        act_type = self.env.ref("cite_helpdesk.mail_act_assigned")
        activity = ticket.activity_ids.filtered(
            lambda a: a.activity_type_id == act_type)
        self.assertTrue(activity)
        self.assertEqual(activity.user_id, self.user_agent)

    def test_cite_activity_cleared_when_closed(self):
        """Activity dibersihkan saat tiket selesai agar tidak menggantung."""
        ticket = self._create_ticket()
        ticket.write({"user_id": self.user_agent.id})
        self.assertTrue(ticket.activity_ids)
        ticket.write({
            "root_cause_id": self.env.ref("cite_helpdesk.rc_human_error").id,
            "resolution_notes": "<p>Selesai.</p>",
            "stage_id": self.env.ref("cite_helpdesk.stage_resolved").id,
        })
        self.assertFalse(ticket.activity_ids)

    def test_foreign_ticket_gets_no_cite_activity(self):
        """Tiket helpdesk lain tidak ikut mendapat activity CITE."""
        ticket = self._create_foreign_ticket()
        cite_types = self.env["mail.activity.type"].browse([
            self.env.ref("cite_helpdesk.mail_act_new_ticket").id,
            self.env.ref("cite_helpdesk.mail_act_assigned").id,
        ])
        self.assertFalse(
            ticket.activity_ids.filtered(
                lambda a: a.activity_type_id in cite_types))

    def test_root_cause_is_master_data(self):
        """Root Cause bisa ditambah dari UI tanpa ubah kode."""
        baru = self.env["cite.root.cause"].create({"name": "Kabel Digigit Tikus"})
        ticket = self._create_ticket()
        ticket.root_cause_id = baru
        self.assertEqual(ticket.root_cause_id.name, "Kabel Digigit Tikus")
        self.assertEqual(len(self.env.ref("cite_helpdesk.rc_unknown")), 1)

    def test_sla_calendar_excludes_weekend(self):
        """Jam kerja SLA tim CITE hanya Senin-Jumat."""
        calendar = self.team.resource_calendar_id
        self.assertTrue(calendar, "tim CITE harus punya jam kerja")
        days = set(calendar.attendance_ids.mapped("dayofweek"))
        self.assertEqual(days, {"0", "1", "2", "3", "4"},
                         "Sabtu (5) dan Minggu (6) tidak boleh jadi jam kerja")
