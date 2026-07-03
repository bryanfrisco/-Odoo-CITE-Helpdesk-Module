# -*- coding: utf-8 -*-
import re

from odoo import fields
from odoo.tests import tagged

from .common import CiteHelpdeskCommon


@tagged("post_install", "-at_install")
class TestSequence(CiteHelpdeskCommon):

    def test_ticket_ref_format(self):
        """FR-03.2 — format IT-YYYY-XXXXX."""
        ticket = self._create_ticket()
        year = fields.Date.today().year
        self.assertRegex(ticket.ticket_ref, r"^IT-%s-\d{5}$" % year)

    def test_ticket_ref_unique_increment(self):
        first = self._create_ticket()
        second = self._create_ticket()
        self.assertNotEqual(first.ticket_ref, second.ticket_ref)
        self.assertLess(first.ticket_ref, second.ticket_ref)

    def test_ticket_ref_not_copied(self):
        ticket = self._create_ticket()
        copy = ticket.copy()
        self.assertNotEqual(ticket.ticket_ref, copy.ticket_ref)
