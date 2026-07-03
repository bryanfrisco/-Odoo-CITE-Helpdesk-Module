# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

CITE_STAGE_XMLIDS = [
    "stage_open", "stage_pending_admin", "stage_pending_heidi",
    "stage_assigned", "stage_in_progress", "stage_waiting_user",
    "stage_resolved", "stage_closed", "stage_cancelled", "stage_rejected",
]

# Stage generik + team default yang dibuat oleh core module `helpdesk`
# (bukan demo). Dirapikan agar deployment CITE bersih.
GENERIC_STAGE_XMLIDS = [
    "helpdesk.stage_new", "helpdesk.stage_in_progress",
    "helpdesk.stage_on_hold", "helpdesk.stage_solved",
    "helpdesk.stage_cancelled",
]


def post_init_hook(env):
    """Dijalankan sekali saat instalasi modul (bukan saat upgrade).

    Tujuan: pada instalasi baru, Odoo otomatis menautkan CITE Helpdesk Team ke
    stage generik bawaan helpdesk (New/In Progress/Solved/Canceled) dan membuat
    team default 'Customer Care'. Hook ini menguncinya agar hanya 10 stage CITE
    yang tampil. Penghapusan team/stage bawaan hanya dilakukan bila benar-benar
    kosong (tidak ada tiket) — aman bila modul dipasang di atas helpdesk yang
    sudah berisi data nyata.
    """
    Ticket = env["helpdesk.ticket"]

    # 1. Kunci CITE Helpdesk Team ke 10 stage CITE.
    team = env.ref("cite_helpdesk.helpdesk_team_cite", raise_if_not_found=False)
    cite_stage_ids = []
    for xmlid in CITE_STAGE_XMLIDS:
        stage = env.ref("cite_helpdesk.%s" % xmlid, raise_if_not_found=False)
        if stage:
            cite_stage_ids.append(stage.id)
    if team and cite_stage_ids:
        team.stage_ids = [(6, 0, cite_stage_ids)]

    # 2. Hapus team default 'Customer Care' bila tidak punya tiket.
    default_team = env.ref("helpdesk.helpdesk_team1", raise_if_not_found=False)
    if default_team and not Ticket.search_count(
            [("team_id", "=", default_team.id)]):
        try:
            default_team.unlink()
        except Exception:  # noqa: BLE001 - fallback non-destruktif
            default_team.active = False
            _logger.info("CITE: team default diarsipkan (tidak bisa dihapus).")

    # 3. Hapus stage generik bawaan yang tidak terpakai oleh tiket mana pun.
    for xmlid in GENERIC_STAGE_XMLIDS:
        stage = env.ref(xmlid, raise_if_not_found=False)
        if stage and not Ticket.search_count([("stage_id", "=", stage.id)]):
            try:
                stage.unlink()
            except Exception:  # noqa: BLE001 - biarkan bila masih dipakai
                _logger.info("CITE: stage generik '%s' dilewati (masih dipakai).",
                             stage.display_name)
