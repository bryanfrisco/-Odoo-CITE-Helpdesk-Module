# -*- coding: utf-8 -*-
from odoo import fields, models


class CiteRootCause(models.Model):
    """Master data Root Cause tiket.

    Dulu berupa fields.Selection dengan 8 nilai hard-code, sehingga menambah
    atau mengubah pilihan harus lewat kode Python. Dijadikan model tersendiri
    agar IT Administrator bisa mengelolanya langsung dari menu Master Data.
    """

    _name = "cite.root.cause"
    _description = "CITE Root Cause"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(
        help="Kode singkat untuk pelaporan (mis. HW, SW, NET). Opsional.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(
        default=True,
        help="Nonaktifkan (bukan hapus) bila tidak dipakai lagi — tiket lama "
             "tetap menyimpan root cause-nya.")
    description = fields.Text(help="Penjelasan singkat kapan pilihan ini dipakai.")

    _sql_constraints = [
        ("cite_root_cause_name_uniq", "unique(name)",
         "Root Cause dengan nama itu sudah ada."),
    ]
