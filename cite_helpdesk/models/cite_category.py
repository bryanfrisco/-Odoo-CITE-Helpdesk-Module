# -*- coding: utf-8 -*-
from odoo import fields, models


class CiteCategory(models.Model):
    _name = "cite.category"
    _description = "CITE Ticket Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    icon = fields.Char(
        string="Icon", default="fa-wrench",
        help="Nama ikon Font Awesome 4.7 (mis. fa-server, fa-print) untuk "
             "kartu kategori di portal.")
    require_approval = fields.Boolean(
        string="Require Double Approval", default=False,
        help="Jika aktif: tiket melewati Administrator Approval lalu "
             "Heidi Lianawaty Lisan Approval sebelum dapat diproses.")
    default_team_id = fields.Many2one("helpdesk.team", string="Auto-Assign Team")
    ticket_type_id = fields.Many2one("helpdesk.ticket.type",
                                     string="Default Ticket Type")
    knowledge_tag = fields.Char(
        help="Keyword pencarian artikel Knowledge Base terkait.")
    active = fields.Boolean(default=True)
    subcategory_ids = fields.One2many("cite.subcategory", "category_id",
                                      string="Sub Categories")

    # Desain: cite.category adalah master data GLOBAL (Software, Hardware, dll.
    # dipakai bersama oleh semua company), sehingga kode unik global memang
    # disengaja — bukan per-company.
    _sql_constraints = [
        ("code_uniq", "unique(code)", "Kode Category harus unik (global)."),
    ]


class CiteSubcategory(models.Model):
    _name = "cite.subcategory"
    _description = "CITE Ticket Sub Category"
    _order = "category_id, sequence, name"

    name = fields.Char(required=True)
    category_id = fields.Many2one("cite.category", string="Category",
                                  required=True, index=True,
                                  ondelete="restrict")
    sequence = fields.Integer(default=10)
    require_approval = fields.Boolean(
        string="Override: Require Double Approval",
        help="Override: paksa approval meski category tidak mewajibkan "
             "(contoh: Software Installation di bawah Software).")
    active = fields.Boolean(default=True)
