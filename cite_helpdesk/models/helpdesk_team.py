# -*- coding: utf-8 -*-
from odoo import api, fields, models

# xmlid 15 departemen CITE (dipakai backfill flag cite_department).
_CITE_DEPARTMENTS = (
    "dept_cite", "dept_engi", "dept_mpma", "dept_memd", "dept_hcgs",
    "dept_cfat", "dept_cpmd", "dept_csus", "dept_miop", "dept_expl",
    "dept_qlab", "dept_legl", "dept_cdre", "dept_govrel", "dept_smde",
)

# xmlid kategori -> ikon Font Awesome (dipakai backfill saat upgrade).
_CATEGORY_ICONS = {
    "cite_helpdesk.cat_software": "fa-window-restore",
    "cite_helpdesk.cat_hardware": "fa-desktop",
    "cite_helpdesk.cat_network": "fa-wifi",
    "cite_helpdesk.cat_server": "fa-server",
    "cite_helpdesk.cat_printer": "fa-print",
    "cite_helpdesk.cat_cctv": "fa-video-camera",
    "cite_helpdesk.cat_access": "fa-key",
    "cite_helpdesk.cat_asset_request": "fa-cube",
}


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    # Penanda agar view/action/dashboard CITE bisa memfilter HANYA tiket tim CITE
    # dan tidak tercampur dengan helpdesk lain (mis. Stargo) di database yang sama.
    cite_team = fields.Boolean(
        string="CITE Helpdesk Team", default=False,
        help="Tandai True hanya untuk tim CITE Helpdesk. Dipakai memfilter "
             "tiket CITE agar terpisah dari helpdesk bawaan/lainnya.")

    @api.model
    def _cite_post_deploy_sync(self):
        """Dipanggil via <function> tiap upgrade (lihat cite_post_deploy.xml).

        Menegaskan field yang dikelola modul pada DB yang sudah pernah install
        versi lama (mis. staging). Tidak bisa lewat <record> biasa karena
        record awal dibuat dengan noupdate=1 sehingga update XML diabaikan.
        """
        team = self.env.ref("cite_helpdesk.helpdesk_team_cite",
                            raise_if_not_found=False)
        if team and not team.cite_team:
            team.cite_team = True
        for xmlid, icon in _CATEGORY_ICONS.items():
            category = self.env.ref(xmlid, raise_if_not_found=False)
            # Isi hanya bila kosong/masih ikon default — hormati editan admin.
            if category and (not category.icon or category.icon == "fa-wrench"):
                category.icon = icon
        # Rename stage approval ke nama profesional — hanya bila masih nama lama
        # (jangan timpa bila admin sudah menamai ulang sendiri).
        stage_renames = {
            "cite_helpdesk.stage_pending_admin":
                ("Pending Administrator Approval", "Awaiting Admin Approval"),
            "cite_helpdesk.stage_pending_heidi":
                ("Pending Heidi Approval", "Awaiting Final Approval"),
        }
        for xmlid, (old_name, new_name) in stage_renames.items():
            stage = self.env.ref(xmlid, raise_if_not_found=False)
            if stage and stage.name == old_name:
                stage.name = new_name
        # Tandai 15 departemen CITE (untuk filter field department tiket).
        for xmlid in _CITE_DEPARTMENTS:
            dept = self.env.ref("cite_helpdesk." + xmlid,
                                raise_if_not_found=False)
            if dept and not dept.cite_department:
                dept.cite_department = True
