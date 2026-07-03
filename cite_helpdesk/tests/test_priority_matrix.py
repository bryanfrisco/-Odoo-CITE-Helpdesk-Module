# -*- coding: utf-8 -*-
from odoo.tests import tagged

from odoo.addons.cite_helpdesk.models.helpdesk_ticket import PRIORITY_MATRIX
from .common import CiteHelpdeskCommon


@tagged("post_install", "-at_install")
class TestPriorityMatrix(CiteHelpdeskCommon):

    def test_all_combinations(self):
        """Bab 20.1 — seluruh 20 kombinasi Impact x Urgency."""
        ticket = self._create_ticket()
        for (impact, urgency), expected in PRIORITY_MATRIX.items():
            ticket.write({"impact": impact, "urgency": urgency})
            self.assertEqual(
                ticket.priority, expected,
                "Matrix gagal untuk (%s, %s)" % (impact, urgency))

    def test_required_combinations(self):
        """Kombinasi yang dipersyaratkan eksplisit pada blueprint."""
        cases = {
            ("company", "site_down"): "3",     # Critical
            ("site", "site_down"): "2",        # High
            ("department", "multi_user"): "1",  # Medium
            ("individual", "single_user"): "1",  # Medium
            ("individual", "request"): "0",    # Low
        }
        ticket = self._create_ticket()
        for (impact, urgency), expected in cases.items():
            ticket.write({"impact": impact, "urgency": urgency})
            self.assertEqual(ticket.priority, expected)

    def test_priority_readonly_computed(self):
        """Priority dihitung server-side; perubahan impact/urgency
        selalu menghitung ulang."""
        ticket = self._create_ticket(impact="individual", urgency="request")
        self.assertEqual(ticket.priority, "0")
        ticket.write({"impact": "company", "urgency": "site_down"})
        self.assertEqual(ticket.priority, "3")
