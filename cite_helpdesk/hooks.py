# -*- coding: utf-8 -*-
CITE_STAGE_XMLIDS = [
    "stage_open", "stage_pending_admin", "stage_pending_heidi",
    "stage_assigned", "stage_in_progress", "stage_waiting_user",
    "stage_resolved", "stage_closed", "stage_cancelled", "stage_rejected",
]


def post_init_hook(env):
    """Dijalankan sekali saat instalasi modul (bukan saat upgrade).

    Saat instalasi, Odoo otomatis menautkan CITE Helpdesk Team ke stage generik
    bawaan helpdesk (New/In Progress/Solved/Canceled). Hook ini menguncinya agar
    hanya 10 stage CITE yang tampil di tim CITE.

    Sejak 17.0.1.5.3 hook TIDAK lagi menghapus team default maupun stage generik
    bawaan helpdesk: keduanya milik modul lain (mis. Stargo Helpdesk memakai
    team "Customer Care" dan stage New/On Hold/Solved), jadi bukan wewenang
    modul ini untuk membereskannya.
    """
    # Kunci CITE Helpdesk Team ke 10 stage CITE.
    team = env.ref("cite_helpdesk.helpdesk_team_cite", raise_if_not_found=False)
    cite_stage_ids = []
    for xmlid in CITE_STAGE_XMLIDS:
        stage = env.ref("cite_helpdesk.%s" % xmlid, raise_if_not_found=False)
        if stage:
            cite_stage_ids.append(stage.id)
    if team and cite_stage_ids:
        team.stage_ids = [(6, 0, cite_stage_ids)]
