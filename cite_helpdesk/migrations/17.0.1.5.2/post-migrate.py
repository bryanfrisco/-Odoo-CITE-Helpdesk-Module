# -*- coding: utf-8 -*-
"""Isi company_id tiket yang terlanjur kosong.

Versi 17.0.1.3.x - 17.0.1.5.1 mengubah helpdesk.ticket.company_id dari
related team_id.company_id (readonly) menjadi field biasa TANPA nilai default.
Akibatnya tiket yang dibuat tanpa company eksplisit - terutama lewat form
website helpdesk bawaan (Stargo) - lahir dengan company kosong. Dampaknya:

  1. submit form gagal ("The customer cannot belong to a different company
     than the ticket") bila partner requester punya company, dan
  2. tiket yang terlanjur dibuat tidak muncul di filter multi-company mana pun.

Sejak 17.0.1.5.2 field itu computed-editable dengan fallback company tim.
Migration ini membereskan baris lama. Dijalankan SEKALI saat upgrade.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    tickets = env["helpdesk.ticket"].sudo().with_context(
        active_test=False).search([("company_id", "=", False)])
    filled = 0
    for ticket in tickets:
        company = ticket.team_id.company_id or env.company
        if company:
            ticket.company_id = company.id
            filled += 1
    _logger.info("CITE Helpdesk: company_id diisi pada %s tiket yang "
                 "sebelumnya kosong.", filled)
