# -*- coding: utf-8 -*-
"""Kembalikan tiket helpdesk NON-CITE yang sempat ter-cap identitas CITE.

Sampai versi 17.0.1.5.0, override ``create()``/``write()`` CITE berjalan untuk
SEMUA ``helpdesk.ticket`` di database — termasuk tiket helpdesk lain (Stargo).
Akibatnya tiket Stargo ikut mendapat nomor IT-YYYY-XXXXX, stage CITE, dan
follower mailbox CITE.

Sejak 17.0.1.5.1 override tersebut dipagari flag ``cite_ticket``. Migration ini
membereskan data yang terlanjur ter-cap. Dijalankan SEKALI saat upgrade.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    repaired = env["helpdesk.ticket"]._cite_repair_foreign_tickets()
    _logger.info("CITE Helpdesk: %s tiket non-CITE dibersihkan dari "
                 "penomoran/stage/follower CITE.", repaired)
