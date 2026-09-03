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
