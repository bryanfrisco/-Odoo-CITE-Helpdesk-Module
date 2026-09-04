# -*- coding: utf-8 -*-
"""Pindahkan Root Cause dari Selection hard-code ke master data cite.root.cause.

Sampai 17.0.1.5.3, helpdesk.ticket.root_cause berupa fields.Selection dengan 8
nilai yang hanya bisa diubah lewat kode Python. Sejak 17.0.1.6.0 pilihannya
menjadi master data (cite.root.cause) yang bisa dikelola dari menu.

Kolom lama `root_cause` masih ada di database saat post-migrate berjalan (field
Python-nya sudah dilepas), jadi nilainya dibaca lewat SQL lalu dipetakan ke
record baru. Kolom lama dibiarkan apa adanya sebagai cadangan audit.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

# nilai selection lama -> xmlid record baru
MAPPING = {
    "human_error": "cite_helpdesk.rc_human_error",
    "hardware_failure": "cite_helpdesk.rc_hardware_failure",
    "software_bug": "cite_helpdesk.rc_software_bug",
    "config_error": "cite_helpdesk.rc_config_error",
    "network_failure": "cite_helpdesk.rc_network_failure",
    "power_failure": "cite_helpdesk.rc_power_failure",
    "vendor_issue": "cite_helpdesk.rc_vendor_issue",
    "unknown": "cite_helpdesk.rc_unknown",
}


def migrate(cr, version):
    cr.execute("""
        SELECT column_name FROM information_schema.columns
         WHERE table_name = 'helpdesk_ticket' AND column_name = 'root_cause'
    """)
    if not cr.fetchone():
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    ids_by_key = {}
    for key, xmlid in MAPPING.items():
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            ids_by_key[key] = record.id

    cr.execute("""
        SELECT id, root_cause FROM helpdesk_ticket
         WHERE root_cause IS NOT NULL AND root_cause_id IS NULL
    """)
    rows = cr.fetchall()
    moved, unmapped = 0, set()
    for ticket_id, key in rows:
        target = ids_by_key.get(key)
        if not target:
            unmapped.add(key)
            continue
        cr.execute("UPDATE helpdesk_ticket SET root_cause_id = %s WHERE id = %s",
                   (target, ticket_id))
        moved += 1

    _logger.info("CITE Helpdesk: root cause %s tiket dipindah ke master data.",
                 moved)
    if unmapped:
        # Nilai di luar 8 bawaan (mis. hasil Studio) — buat recordnya agar
        # datanya tidak hilang, lalu petakan.
        RootCause = env["cite.root.cause"].sudo()
        for key in unmapped:
            record = RootCause.create({"name": key.replace("_", " ").title(),
                                       "code": key[:8].upper()})
            cr.execute("""UPDATE helpdesk_ticket SET root_cause_id = %s
                           WHERE root_cause = %s AND root_cause_id IS NULL""",
                       (record.id, key))
        _logger.info("CITE Helpdesk: %s root cause non-standar dibuatkan "
                     "record baru: %s", len(unmapped), ", ".join(sorted(unmapped)))
