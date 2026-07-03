# -*- coding: utf-8 -*-
"""Terapkan nilai SLA baru pada DB yang sudah terinstall (data noupdate=1).

Dijalankan SEKALI saat upgrade ke 17.0.1.2.0. Tidak menimpa editan admin di
upgrade berikutnya (folder versi-spesifik). "time" = jam kerja (8 jam = 1 hari).
"""
from odoo import api, SUPERUSER_ID

# xmlid -> (time_jam_kerja, name)
SLA_DATA = {
    "cite_helpdesk.sla_resp_crit": (1, "SLA-RESP-CRIT — Response Critical (1 jam)"),
    "cite_helpdesk.sla_resp_high": (2, "SLA-RESP-HIGH — Response High (2 jam)"),
    "cite_helpdesk.sla_resp_med": (4, "SLA-RESP-MED — Response Medium (4 jam)"),
    "cite_helpdesk.sla_resp_low": (4, "SLA-RESP-LOW — Response Low (4 jam)"),
    "cite_helpdesk.sla_reso_crit": (24, "SLA-RESO-CRIT — Resolution Critical (3 hari)"),
    "cite_helpdesk.sla_reso_high": (32, "SLA-RESO-HIGH — Resolution High (4 hari)"),
    "cite_helpdesk.sla_reso_med": (40, "SLA-RESO-MED — Resolution Medium (5 hari)"),
    "cite_helpdesk.sla_reso_low": (40, "SLA-RESO-LOW — Resolution Low (5 hari)"),
}


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid, (hours, name) in SLA_DATA.items():
        sla = env.ref(xmlid, raise_if_not_found=False)
        if sla:
            sla.write({"time": hours, "name": name})
