# -*- coding: utf-8 -*-
from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    # Penanda departemen CITE (15 kode singkatan, global lintas company).
    # Field department di tiket CITE difilter ke yang ber-flag ini agar dropdown
    # hanya menampilkan 15 kode tsb — terpisah dari departemen native company.
    cite_department = fields.Boolean(
        string="CITE Department", default=False,
        help="Tandai True hanya untuk 15 departemen CITE. Dipakai memfilter "
             "pilihan departemen pada tiket/portal CITE.")
