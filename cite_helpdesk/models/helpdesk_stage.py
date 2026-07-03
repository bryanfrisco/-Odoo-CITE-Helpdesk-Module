# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskStage(models.Model):
    _inherit = "helpdesk.stage"

    is_close = fields.Boolean(
        string="Closing Stage",
        help="Tahap akhir (Closed / Cancelled / Rejected): menghentikan SLA "
             "dan mengunci tiket.")
