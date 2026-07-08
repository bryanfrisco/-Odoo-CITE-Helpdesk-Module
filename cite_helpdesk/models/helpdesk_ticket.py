# -*- coding: utf-8 -*-
from datetime import timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import is_html_empty

# Bab 20.1 — Auto Priority Matrix (Impact x Urgency -> Priority).
# Priority mapping ke selection native helpdesk: 0=Low 1=Medium 2=High 3=Critical.
PRIORITY_MATRIX = {
    ("company", "site_down"): "3",
    ("company", "dept_down"): "3",
    ("company", "multi_user"): "2",
    ("company", "single_user"): "2",
    ("company", "request"): "1",
    ("site", "site_down"): "2",
    ("site", "dept_down"): "2",
    ("site", "multi_user"): "1",
    ("site", "single_user"): "1",
    ("site", "request"): "0",
    ("department", "site_down"): "2",
    ("department", "dept_down"): "2",
    ("department", "multi_user"): "1",
    ("department", "single_user"): "1",
    ("department", "request"): "0",
    ("individual", "site_down"): "1",
    ("individual", "dept_down"): "1",
    ("individual", "multi_user"): "1",
    ("individual", "single_user"): "1",
    ("individual", "request"): "0",
}

STAGE_XMLIDS = {
    "open": "cite_helpdesk.stage_open",
    "pending_admin": "cite_helpdesk.stage_pending_admin",
    "pending_heidi": "cite_helpdesk.stage_pending_heidi",
    "assigned": "cite_helpdesk.stage_assigned",
    "in_progress": "cite_helpdesk.stage_in_progress",
    "waiting_user": "cite_helpdesk.stage_waiting_user",
    "resolved": "cite_helpdesk.stage_resolved",
    "closed": "cite_helpdesk.stage_closed",
    "cancelled": "cite_helpdesk.stage_cancelled",
    "rejected": "cite_helpdesk.stage_rejected",
}

# Stage yang hanya boleh dicapai setelah approval penuh (FR-07.3 / 13.3-1).
APPROVAL_PROTECTED_STAGES = {"assigned", "in_progress", "resolved", "closed"}
# Stage terminal: tiket terkunci readonly.
LOCKED_STAGES = {"closed", "cancelled", "rejected"}
# Field yang masih boleh ditulis pada tiket terkunci (housekeeping/sistem).
LOCK_ALLOWED_FIELDS = {
    "stage_id", "active", "closed_date", "kanban_state",
    "sla_warning_75_sent", "sla_warning_90_sent", "sla_breach_sent",
    "message_main_attachment_id", "rating_last_value",
}

def _cite_human_duration(delta):
    """Format timedelta jadi '2h 05m' / '3d 4h' untuk tampilan waktu di stage."""
    seconds = max(int(delta.total_seconds()), 0)
    if seconds < 3600:
        return "%dm" % (seconds // 60)
    if seconds < 86400:
        return "%dh %02dm" % (seconds // 3600, seconds % 3600 // 60)
    return "%dd %dh" % (seconds // 86400, seconds % 86400 // 3600)


DEFAULT_DESCRIPTION = """
<p><strong>Deskripsi masalah/permintaan:</strong></p>
<p>(jelaskan di sini, tempel screenshot bila ada)</p>
<p><strong>Kondisi:</strong></p>
<ul><li>...</li><li>...</li></ul>
<p><strong>Sudah dicoba:</strong></p>
<ul><li>...</li></ul>
"""
 

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------

    # --- Identitas & lokasi ---
    ticket_ref = fields.Char(string="Ticket Number", copy=False, index=True,
                             readonly=True)
    # Native helpdesk memaksa company_id = company tim (related team_id.company_id,
    # readonly), sehingga SATU tim CITE (shared lintas 3 company) tidak bisa punya
    # tiket dengan company berbeda. Kita override jadi field biasa yang dipilih
    # per-tiket (mengikuti pilihan di portal), lepas dari company tim.
    company_id = fields.Many2one(
        "res.company", string="Company", index=True, tracking=True,
        related=False, readonly=False, store=True)
    site_id = fields.Many2one("cite.site", string="Lokasi", tracking=True)
    # Departemen CITE: hanya 15 kode (cite_department=True), terpisah dari
    # departemen native company. Dipilih manual (wajib di portal).
    department_id = fields.Many2one(
        "hr.department", string="Department", tracking=True,
        domain="[('cite_department', '=', True)]")

    description = fields.Html(default=DEFAULT_DESCRIPTION)

    # --- Klasifikasi ---
    cite_category_id = fields.Many2one("cite.category", string="Category",
                                       tracking=True)
    cite_subcategory_id = fields.Many2one(
        "cite.subcategory", string="Sub Category", tracking=True,
        domain="[('category_id', '=', cite_category_id)]")
    equipment_id = fields.Many2one(
        "maintenance.equipment", string="Asset", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    # --- Priority engine (FR-05) — plain-language labels for end users ---
    impact = fields.Selection([
        ("company", "The entire company"),
        ("site", "A whole location"),
        ("department", "A whole department"),
        ("individual", "Only me")],
        string="Who is affected?", tracking=True)
    urgency = fields.Selection([
        ("site_down", "A location is completely down"),
        ("dept_down", "A department cannot work"),
        ("multi_user", "Several people are disrupted"),
        ("single_user", "Only I am disrupted"),
        ("request", "Routine request (not urgent)")],
        string="How urgent?", tracking=True)
    priority = fields.Selection(
        selection=[("0", "Low"), ("1", "Medium"),
                   ("2", "High"), ("3", "Critical")],
        compute="_compute_priority", store=True, readonly=True, tracking=True)

    # --- Approval engine (FR-07) ---
    require_approval = fields.Boolean(
        compute="_compute_require_approval", store=True)
    admin_approval_status = fields.Selection([
        ("not_required", "Not Required"), ("pending", "Pending"),
        ("approved", "Approved"), ("rejected", "Rejected")],
        string="Administrator Approval Status",
        default="not_required", tracking=True, copy=False)
    admin_approver_id = fields.Many2one("res.users", string="Administrator Approver",
                                        readonly=True, copy=False)
    admin_approval_date = fields.Datetime(readonly=True, copy=False)
    heidi_approval_status = fields.Selection([
        ("not_required", "Not Required"), ("waiting", "Waiting Level 1"),
        ("pending", "Pending"), ("approved", "Approved"),
        ("rejected", "Rejected")],
        string="Heidi Lianawaty Lisan Approval Status",
        default="not_required", tracking=True, copy=False)
    heidi_approval_date = fields.Datetime(readonly=True, copy=False)
    approval_status = fields.Selection([
        ("not_required", "Not Required"), ("in_review", "In Review"),
        ("fully_approved", "Fully Approved"), ("rejected", "Rejected")],
        compute="_compute_approval_status", store=True, tracking=True)
    rejection_reason = fields.Text(copy=False)

    # --- Resolusi & audit (FR-12) ---
    root_cause = fields.Selection([
        ("human_error", "Human Error"), ("hardware_failure", "Hardware Failure"),
        ("software_bug", "Software Bug"), ("config_error", "Configuration Error"),
        ("network_failure", "Network Failure"), ("power_failure", "Power Failure"),
        ("vendor_issue", "Vendor Issue"), ("unknown", "Unknown")], tracking=True)
    # Html tidak mendukung chatter tracking (Odoo NotImplementedError) —
    # audit cukup via resolved_date/closed_date & perubahan stage yang tracked.
    resolution_notes = fields.Html()
    first_response_date = fields.Datetime(readonly=True, copy=False)
    resolved_date = fields.Datetime(readonly=True, copy=False, tracking=True)
    closed_date = fields.Datetime(readonly=True, copy=False, tracking=True)

    # --- SLA warning flags (Bab 20.4) ---
    sla_warning_75_sent = fields.Boolean(copy=False)
    sla_warning_90_sent = fields.Boolean(copy=False)
    sla_breach_sent = fields.Boolean(copy=False)

    # --- Helper untuk view & guard ---
    # Flag CITE disimpan di tiket (bukan traversal team_id.cite_team di domain):
    # traversal memicu record rule multi-company helpdesk.team
    # [('company_id','in',company_ids)] — saat company tim (RSL) tidak dicentang
    # di switcher, tim "hilang" dan SEMUA tiket CITE ikut lenyap dari
    # action/dashboard walau company tiketnya dicentang. Flag tersimpan ini
    # dievaluasi langsung di tabel tiket sehingga bebas dari rule tim.
    cite_ticket = fields.Boolean(
        related="team_id.cite_team", store=True, string="CITE Ticket")
    cite_stage_code = fields.Char(
        compute="_compute_cite_stage_code", store=True, string="Stage Code")
    stage_is_locked = fields.Boolean(compute="_compute_stage_is_locked")
    time_in_stage = fields.Char(
        compute="_compute_time_in_stage", string="Time in Stage",
        help="Lama tiket berada di stage saat ini.")

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    @api.depends("impact", "urgency")
    def _compute_priority(self):
        for ticket in self:
            ticket.priority = PRIORITY_MATRIX.get(
                (ticket.impact, ticket.urgency), "0")

    @api.depends("cite_category_id.require_approval",
                 "cite_subcategory_id.require_approval")
    def _compute_require_approval(self):
        for ticket in self:
            ticket.require_approval = bool(
                ticket.cite_category_id.require_approval
                or ticket.cite_subcategory_id.require_approval)

    @api.depends("require_approval", "admin_approval_status",
                 "heidi_approval_status")
    def _compute_approval_status(self):
        for ticket in self:
            if not ticket.require_approval:
                ticket.approval_status = "not_required"
            elif "rejected" in (ticket.admin_approval_status,
                                ticket.heidi_approval_status):
                ticket.approval_status = "rejected"
            elif (ticket.admin_approval_status == "approved"
                    and ticket.heidi_approval_status == "approved"):
                ticket.approval_status = "fully_approved"
            else:
                ticket.approval_status = "in_review"

    @api.depends("stage_id")
    def _compute_cite_stage_code(self):
        mapping = {}
        for code, xmlid in STAGE_XMLIDS.items():
            stage = self.env.ref(xmlid, raise_if_not_found=False)
            if stage:
                mapping[stage.id] = code
        for ticket in self:
            ticket.cite_stage_code = mapping.get(ticket.stage_id.id, False)

    @api.depends("cite_stage_code")
    def _compute_stage_is_locked(self):
        for ticket in self:
            ticket.stage_is_locked = ticket.cite_stage_code in LOCKED_STAGES

    @api.depends("stage_id", "date_last_stage_update")
    def _compute_time_in_stage(self):
        now = fields.Datetime.now()
        for ticket in self:
            ref = ticket.date_last_stage_update or ticket.create_date
            ticket.time_in_stage = (_cite_human_duration(now - ref)
                                    if ref else "-")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _cite_stage(self, code):
        return self.env.ref(STAGE_XMLIDS[code])

    def _send_cite_mail(self, template_xmlid, email_values=None):
        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            return
        for ticket in self:
            template.sudo().send_mail(
                ticket.id, email_values=email_values, force_send=False)

    def _group_user_emails(self, group_xmlid):
        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        if not group:
            return ""
        return ",".join(u.email_formatted for u in group.users if u.email)

    def _notify_group(self, group_xmlid, template_xmlid):
        emails = self._group_user_emails(group_xmlid)
        if emails:
            self._send_cite_mail(template_xmlid,
                                 email_values={"email_to": emails})

    def _notify_cite_mailbox(self, template_xmlid):
        """Kirim notifikasi ke mailbox pusat CITE (cite@aspire.id)."""
        mailbox = self.env.ref("cite_helpdesk.partner_cite_mailbox",
                               raise_if_not_found=False)
        if mailbox and mailbox.email:
            self._send_cite_mail(template_xmlid,
                                 email_values={"email_to": mailbox.email})

    def _schedule_approval_activity(self, group_xmlid, activity_xmlid):
        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        if not group:
            return
        for ticket in self:
            for user in group.users:
                ticket.activity_schedule(
                    activity_xmlid, user_id=user.id,
                    summary=_("Approval tiket %s", ticket.ticket_ref or ""))

    # ------------------------------------------------------------------
    # CRUD overrides
    # ------------------------------------------------------------------

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        # Requester otomatis = user yang sedang login.
        if ("partner_id" in fields_list and not defaults.get("partner_id")
                and not self.env.user._is_public()):
            defaults["partner_id"] = self.env.user.partner_id.id
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        # Mailbox pusat CITE (cite@aspire.id) — menerima tembusan setiap tiket.
        mailbox = self.env.ref("cite_helpdesk.partner_cite_mailbox",
                               raise_if_not_found=False)
        cc_values = ({"email_cc": mailbox.email}
                     if mailbox and mailbox.email else None)
        for ticket in tickets:
            ticket = ticket.with_context(cite_skip_status_mail=True)
            # Native create menimpa ticket_ref dengan sequence 'helpdesk.ticket'
            # — set ulang ke sequence CITE setelah create.
            ticket.ticket_ref = (
                self.env["ir.sequence"].sudo()
                .next_by_code("cite.helpdesk.ticket") or ticket.ticket_ref)
            if ticket.require_approval:
                ticket._start_admin_approval()
            elif not ticket.cite_stage_code:
                ticket.stage_id = ticket._cite_stage("open").id
            # Tembusan ke mailbox pusat: CC pada email "Ticket Created" +
            # jadikan follower agar percakapan publik berikutnya juga masuk.
            ticket._send_cite_mail("cite_helpdesk.mail_tpl_ticket_created",
                                   email_values=cc_values)
            if mailbox:
                ticket.message_subscribe(partner_ids=mailbox.ids)
        tickets._check_approval_guard()
        return tickets

    def write(self, vals):
        self._check_lock(vals)
        res = super().write(vals)
        self._check_approval_guard()
        if "stage_id" in vals and not self.env.context.get("cite_stage_followup"):
            self.with_context(cite_stage_followup=True)._on_stage_changed()
        if vals.get("user_id"):
            self._send_cite_mail("cite_helpdesk.mail_tpl_ticket_assigned")
        # Kategori diubah menjadi kategori ber-approval setelah create.
        if "cite_category_id" in vals or "cite_subcategory_id" in vals:
            for ticket in self:
                if (ticket.require_approval
                        and ticket.admin_approval_status == "not_required"
                        and not ticket.stage_is_locked):
                    ticket._start_admin_approval()
        return res

    def unlink(self):
        if not self.env.user.has_group("base.group_system"):
            raise UserError(_(
                "Tiket tidak boleh dihapus demi audit trail. "
                "Gunakan Cancel atau Archive."))
        return super().unlink()

    # ------------------------------------------------------------------
    # Guards (server-side, anti-bypass — Bab 13.3 & 30.2)
    # ------------------------------------------------------------------

    def _check_lock(self, vals):
        if self.env.su or self.env.context.get("cite_bypass_lock"):
            return
        if not set(vals) - LOCK_ALLOWED_FIELDS:
            return
        locked = self.filtered("stage_is_locked")
        if locked:
            raise UserError(_(
                "Tiket %s berstatus final (Closed/Cancelled/Rejected) dan "
                "terkunci. Gunakan tombol Reopen bila perlu dibuka kembali.",
                ", ".join(locked.mapped("ticket_ref"))))

    @api.constrains("company_id", "partner_id")
    def _check_partner_id_has_the_same_company(self):
        # Tiket CITE = shared-service grup: requester boleh berasal dari company
        # berbeda dengan company tiket (mis. melapor untuk site company lain).
        # Lewati constraint native hanya untuk tim CITE; tim lain tetap dicek.
        # (pakai flag cite_ticket — baca team_id langsung bisa kena rule tim)
        others = self.filtered(lambda t: not t.cite_ticket)
        if others:
            super(HelpdeskTicket, others)._check_partner_id_has_the_same_company()

    def _check_approval_guard(self):
        for ticket in self:
            if (ticket.require_approval
                    and ticket.approval_status != "fully_approved"
                    and ticket.cite_stage_code in APPROVAL_PROTECTED_STAGES):
                raise ValidationError(_(
                    "Tiket %s memerlukan persetujuan Administrator dan "
                    "Heidi Lianawaty Lisan sebelum diproses.",
                    ticket.ticket_ref or ticket.display_name))

    # ------------------------------------------------------------------
    # Stage lifecycle (AA-01..AA-06 versi module)
    # ------------------------------------------------------------------

    def _on_stage_changed(self):
        now = fields.Datetime.now()
        for ticket in self:
            code = ticket.cite_stage_code
            writer = ticket.with_context(cite_bypass_lock=True,
                                         cite_stage_followup=True)
            if code in ("resolved", "closed"):
                if (not ticket.root_cause
                        or is_html_empty(ticket.resolution_notes)):
                    raise ValidationError(_(
                        "Root Cause dan Resolution Notes wajib diisi "
                        "sebelum tiket di-Resolve/Close."))
            if code == "in_progress":
                if not ticket.first_response_date:
                    writer.first_response_date = now
            if code == "resolved":
                if not ticket.resolved_date:
                    writer.resolved_date = now
                ticket._send_cite_mail("cite_helpdesk.mail_tpl_resolved_csat")
            elif code == "closed":
                if not ticket.closed_date:
                    writer.closed_date = now
                ticket._send_cite_mail("cite_helpdesk.mail_tpl_closed")
            elif (code not in (False, "draft", "rejected",
                               "pending_admin", "pending_heidi")
                    and not self.env.context.get("cite_skip_status_mail")):
                ticket._send_cite_mail("cite_helpdesk.mail_tpl_status_changed")

    # AA-05 — balasan requester saat Waiting User -> kembali In Progress.
    def _message_post_after_hook(self, message, msg_vals):
        res = super()._message_post_after_hook(message, msg_vals)
        if (self.cite_stage_code == "waiting_user"
                and self.partner_id
                and message.author_id == self.partner_id
                and msg_vals.get("message_type") in ("comment", "email")):
            self.with_context(cite_bypass_lock=True).stage_id = \
                self._cite_stage("in_progress").id
        return res

    # ------------------------------------------------------------------
    # Workflow buttons
    # ------------------------------------------------------------------

    def action_start_progress(self):
        self.write({"stage_id": self._cite_stage("in_progress").id})

    def action_waiting_user(self):
        self.write({"stage_id": self._cite_stage("waiting_user").id})

    def action_resolve(self):
        self.write({"stage_id": self._cite_stage("resolved").id})

    def action_close(self):
        self.write({"stage_id": self._cite_stage("closed").id})

    def action_cancel(self):
        self.with_context(cite_skip_status_mail=False).write(
            {"stage_id": self._cite_stage("cancelled").id})

    def action_reopen(self):
        if not self.env.user.has_group("helpdesk.group_helpdesk_user"):
            raise AccessError(_("Hanya agen IT yang dapat me-reopen tiket."))
        for ticket in self:
            ticket.with_context(cite_bypass_lock=True).stage_id = \
                ticket._cite_stage("in_progress").id
            ticket.message_post(body=_("Tiket dibuka kembali oleh %s.",
                                       self.env.user.name))

    # ------------------------------------------------------------------
    # Approval engine (Bab 13)
    # ------------------------------------------------------------------

    def _check_approver(self, group_xmlid, level_label):
        if not self.env.user.has_group(group_xmlid):
            raise AccessError(_(
                "Hanya %s yang dapat melakukan aksi approval ini.",
                level_label))
        for ticket in self:
            if (ticket.create_uid == self.env.user
                    and not self.env.user.has_group("base.group_system")):
                raise UserError(_(
                    "Segregation of duty: Anda tidak dapat meng-approve "
                    "tiket yang Anda buat sendiri."))

    def _start_admin_approval(self):
        for ticket in self:
            ticket.with_context(cite_skip_status_mail=True).write({
                "admin_approval_status": "pending",
                "heidi_approval_status": "waiting",
                "stage_id": ticket._cite_stage("pending_admin").id,
            })
            ticket._schedule_approval_activity(
                "cite_helpdesk.group_it_administrator",
                "cite_helpdesk.mail_act_admin_approval")
            # Approval L1 (pertama) → mailbox pusat cite@aspire.id.
            ticket._notify_cite_mailbox(
                "cite_helpdesk.mail_tpl_admin_approval_request")

    def action_admin_approve(self):
        self._check_approver("cite_helpdesk.group_it_administrator",
                             _("IT Administrator"))
        for ticket in self:
            if ticket.admin_approval_status != "pending":
                raise UserError(_(
                    "Tiket %s tidak sedang menunggu approval Administrator.",
                    ticket.ticket_ref))
            ticket.with_context(cite_skip_status_mail=True).write({
                "admin_approval_status": "approved",
                "admin_approver_id": self.env.user.id,
                "admin_approval_date": fields.Datetime.now(),
                "heidi_approval_status": "pending",
                "stage_id": ticket._cite_stage("pending_heidi").id,
            })
            ticket.activity_feedback(["cite_helpdesk.mail_act_admin_approval"])
            ticket._send_cite_mail("cite_helpdesk.mail_tpl_admin_approved")
            ticket._schedule_approval_activity(
                "cite_helpdesk.group_heidi_approver",
                "cite_helpdesk.mail_act_heidi_approval")
            ticket._notify_group(
                "cite_helpdesk.group_heidi_approver",
                "cite_helpdesk.mail_tpl_heidi_approval_request")

    def action_heidi_approve(self):
        self._check_approver("cite_helpdesk.group_heidi_approver",
                             _("Heidi Lianawaty Lisan"))
        for ticket in self:
            if ticket.admin_approval_status != "approved":
                raise ValidationError(_("Approval Level 1 belum disetujui."))
            if ticket.heidi_approval_status != "pending":
                raise UserError(_(
                    "Tiket %s tidak sedang menunggu approval Level 2.",
                    ticket.ticket_ref))
            ticket.with_context(cite_skip_status_mail=True).write({
                "heidi_approval_status": "approved",
                "heidi_approval_date": fields.Datetime.now(),
                "stage_id": ticket._cite_stage("assigned").id,
            })
            ticket.activity_feedback(["cite_helpdesk.mail_act_heidi_approval"])
            ticket._send_cite_mail("cite_helpdesk.mail_tpl_heidi_approved")
            ticket._auto_assign()

    def _action_open_reject_wizard(self, level):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Reject Ticket"),
            "res_model": "cite.ticket.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_ticket_id": self.id, "default_level": level},
        }

    def action_admin_reject(self):
        self._check_approver("cite_helpdesk.group_it_administrator",
                             _("IT Administrator"))
        return self._action_open_reject_wizard("admin")

    def action_heidi_reject(self):
        self._check_approver("cite_helpdesk.group_heidi_approver",
                             _("Heidi Lianawaty Lisan"))
        return self._action_open_reject_wizard("heidi")

    def _apply_rejection(self, level, reason):
        self.ensure_one()
        now = fields.Datetime.now()
        vals = {
            "rejection_reason": reason,
            "stage_id": self._cite_stage("rejected").id,
        }
        if level == "admin":
            if self.admin_approval_status != "pending":
                raise UserError(_("Tiket tidak menunggu approval Administrator."))
            vals.update(admin_approval_status="rejected",
                        admin_approver_id=self.env.user.id,
                        admin_approval_date=now)
            activity = "cite_helpdesk.mail_act_admin_approval"
            template = "cite_helpdesk.mail_tpl_admin_rejected"
        else:
            if self.heidi_approval_status != "pending":
                raise UserError(_("Tiket tidak menunggu approval Level 2."))
            vals.update(heidi_approval_status="rejected",
                        heidi_approval_date=now)
            activity = "cite_helpdesk.mail_act_heidi_approval"
            template = "cite_helpdesk.mail_tpl_heidi_rejected"
        self.with_context(cite_skip_status_mail=True,
                          cite_bypass_lock=True).write(vals)
        self.activity_feedback([activity])
        self.message_post(body=_("Tiket DITOLAK oleh %(user)s. Alasan: %(reason)s",
                                 user=self.env.user.name, reason=reason))
        self._send_cite_mail(template)

    # ------------------------------------------------------------------
    # Auto assignment (SA-06)
    # ------------------------------------------------------------------

    def _auto_assign(self):
        default_team = self.env.ref("cite_helpdesk.helpdesk_team_cite",
                                    raise_if_not_found=False)
        for ticket in self:
            team = (ticket.cite_category_id.default_team_id
                    or ticket.team_id or default_team)
            if team and ticket.team_id != team:
                ticket.team_id = team
            if team and team.member_ids and not ticket.user_id:
                # Balanced: anggota dengan tiket open paling sedikit.
                counts = dict(self.env["helpdesk.ticket"]._read_group(
                    [("user_id", "in", team.member_ids.ids),
                     ("stage_id.is_close", "=", False)],
                    ["user_id"], ["__count"]))
                ticket.user_id = min(
                    team.member_ids,
                    key=lambda u: counts.get(u, 0))

    # ------------------------------------------------------------------
    # Server action helpers (SA-07, SA-08, SA-10)
    # ------------------------------------------------------------------

    def action_assign_to_me(self):
        if not self.env.user.has_group("cite_helpdesk.group_it_support"):
            raise AccessError(_("Hanya agen IT yang dapat assign tiket."))
        self.write({"user_id": self.env.user.id})

    def action_escalate_to_manager(self):
        manager_group = self.env.ref("cite_helpdesk.group_it_manager")
        for ticket in self:
            for user in manager_group.users:
                ticket.activity_schedule(
                    "mail.mail_activity_data_todo", user_id=user.id,
                    summary=_("Eskalasi tiket %s", ticket.ticket_ref or ""))

    def action_resend_csat(self):
        self.filtered(lambda t: t.cite_stage_code in ("resolved", "closed")
                      and not t.rating_ids)._send_cite_mail(
            "cite_helpdesk.mail_tpl_resolved_csat")

    # ------------------------------------------------------------------
    # Crons (AA-08..AA-12)
    # ------------------------------------------------------------------

    @api.model
    def _cron_auto_close(self):
        """AA-08 — auto close 3 hari setelah Resolved tanpa respon requester."""
        limit = fields.Datetime.now() - timedelta(days=3)
        resolved_stage = self.env.ref(STAGE_XMLIDS["resolved"],
                                      raise_if_not_found=False)
        if not resolved_stage:
            return
        tickets = self.search([
            ("stage_id", "=", resolved_stage.id),
            ("resolved_date", "<=", limit),
        ])
        Message = self.env["mail.message"]
        for ticket in tickets:
            replied = ticket.partner_id and Message.search_count([
                ("model", "=", "helpdesk.ticket"),
                ("res_id", "=", ticket.id),
                ("author_id", "=", ticket.partner_id.id),
                ("message_type", "in", ("comment", "email")),
                ("date", ">", ticket.resolved_date),
            ])
            if not replied:
                ticket.stage_id = ticket._cite_stage("closed").id

    @api.model
    def _cron_sla_warning(self):
        """AA-09/10/11 — SLA warning 75%, 90%, dan breach alert."""
        now = fields.Datetime.now()
        tickets = self.search([
            ("cite_ticket", "=", True),
            ("stage_id.is_close", "=", False),
            ("sla_status_ids", "!=", False),
        ])
        for ticket in tickets:
            ongoing = ticket.sla_status_ids.filtered(
                lambda s: s.status == "ongoing" and s.deadline)
            failed = ticket.sla_status_ids.filtered(
                lambda s: s.status == "failed")
            if failed and not ticket.sla_breach_sent:
                ticket.sla_breach_sent = True
                ticket._notify_group("cite_helpdesk.group_it_manager",
                                     "cite_helpdesk.mail_tpl_sla_breach")
            for sla_status in ongoing:
                start = sla_status.create_date
                total = (sla_status.deadline - start).total_seconds()
                if total <= 0:
                    continue
                ratio = (now - start).total_seconds() / total
                if ratio >= 0.90 and not ticket.sla_warning_90_sent:
                    ticket.sla_warning_90_sent = True
                    ticket.sla_warning_75_sent = True
                    emails = []
                    if ticket.user_id.email:
                        emails.append(ticket.user_id.email_formatted)
                    leader_emails = self._group_user_emails(
                        "cite_helpdesk.group_it_manager")
                    if leader_emails:
                        emails.append(leader_emails)
                    if emails:
                        ticket._send_cite_mail(
                            "cite_helpdesk.mail_tpl_sla_warning_90",
                            email_values={"email_to": ",".join(emails)})
                    if ticket.user_id:
                        ticket.activity_schedule(
                            "mail.mail_activity_data_todo",
                            user_id=ticket.user_id.id,
                            summary=_("SLA 90%% terpakai — %s",
                                      ticket.ticket_ref or ""))
                elif ratio >= 0.75 and not ticket.sla_warning_75_sent:
                    ticket.sla_warning_75_sent = True
                    if ticket.user_id.email:
                        ticket._send_cite_mail(
                            "cite_helpdesk.mail_tpl_sla_warning_75",
                            email_values={
                                "email_to": ticket.user_id.email_formatted})

    @api.model
    def _cron_approval_reminder(self):
        """AA-12 — reminder approval pending > 24 jam."""
        limit = fields.Datetime.now() - timedelta(hours=24)
        pending_admin = self.search([
            ("cite_ticket", "=", True),
            ("admin_approval_status", "=", "pending"),
            ("create_date", "<=", limit),
        ])
        # Reminder approval L1 → mailbox pusat cite@aspire.id.
        pending_admin._notify_cite_mailbox(
            "cite_helpdesk.mail_tpl_admin_approval_request")
        pending_heidi = self.search([
            ("cite_ticket", "=", True),
            ("heidi_approval_status", "=", "pending"),
            ("admin_approval_date", "<=", limit),
        ])
        pending_heidi._notify_group(
            "cite_helpdesk.group_heidi_approver",
            "cite_helpdesk.mail_tpl_heidi_approval_request")

    # ------------------------------------------------------------------
    # Dashboard Overview (menu CITE Helpdesk > Overview)
    # ------------------------------------------------------------------

    @api.model
    def get_cite_dashboard_data(self, sla_period="month"):
        """Data realtime untuk client action cite_helpdesk.dashboard."""
        # Dashboard mengikuti company yang dicentang di switcher (allowed_company_ids
        # dari context web client). Centang 1 company -> hanya tiket company itu;
        # centang beberapa -> gabungan. Filter ditegakkan record rule multi-company
        # helpdesk.ticket secara otomatis pada search/_read_group di bawah.
        now = fields.Datetime.now()
        tz = pytz.timezone(self.env.user.tz or "UTC")
        local_now = pytz.utc.localize(now).astimezone(tz)
        today_start_local = local_now.replace(hour=0, minute=0, second=0,
                                              microsecond=0)
        month_start_local = today_start_local.replace(day=1)
        trend_start_local = today_start_local - timedelta(days=13)

        def to_utc(dt):
            return dt.astimezone(pytz.utc).replace(tzinfo=None)

        today_start = to_utc(today_start_local)
        month_start = to_utc(month_start_local)
        trend_start = to_utc(trend_start_local)

        def dur(delta):
            seconds = max(int(delta.total_seconds()), 0)
            if seconds < 3600:
                return "%dm" % (seconds // 60)
            if seconds < 86400:
                return "%dh %02dm" % (seconds // 3600, seconds % 3600 // 60)
            return "%dd %dh" % (seconds // 86400, seconds % 86400 // 3600)

        def fmt(dt):
            if not dt:
                return "-"
            return fields.Datetime.context_timestamp(self, dt).strftime(
                "%d %b %H:%M")

        priority_labels = dict(self._fields["priority"].selection)
        now_str = fields.Datetime.to_string(now)

        # --- KPI cards + domain klik-tembus ---
        domains = {
            "total_open": [("stage_id.is_close", "=", False)],
            # Semua tiket baru yang belum direspon: Open, Assigned, dan yang
            # masih menunggu approval (Pending Admin/Heidi) — agar terlihat.
            "need_response": [
                ("stage_id.is_close", "=", False),
                ("first_response_date", "=", False),
                ("cite_stage_code", "in",
                 ["open", "assigned", "pending_admin", "pending_heidi"]),
            ],
            "on_progress": [("cite_stage_code", "=", "in_progress")],
            "almost_overdue": [
                ("stage_id.is_close", "=", False),
                ("sla_deadline", ">=", now_str),
                ("sla_deadline", "<=",
                 fields.Datetime.to_string(now + timedelta(hours=2))),
            ],
            "overdue": [
                ("stage_id.is_close", "=", False),
                "|", ("sla_fail", "=", True), ("sla_deadline", "<", now_str),
            ],
            "solved_today": [
                ("resolved_date", ">=", fields.Datetime.to_string(today_start)),
            ],
        }
        # Batasi SELURUH data dashboard ke tiket tim CITE saja (pisah dari
        # helpdesk lain/Stargo di DB yang sama). Leaf di-AND otomatis di depan.
        cite_leaf = ("cite_ticket", "=", True)
        domains = {key: [cite_leaf] + domain for key, domain in domains.items()}
        kpis = {key: self.search_count(domain)
                for key, domain in domains.items()}

        # --- Tabel operasional ---
        def ticket_rows(domain, order, extra):
            return [{
                "id": ticket.id,
                "ref": ticket.ticket_ref or ("#%s" % ticket.id),
                "name": ticket.name,
                **extra(ticket),
            } for ticket in self.search(domain, order=order, limit=8)]

        need_response_rows = ticket_rows(
            domains["need_response"], "create_date desc", lambda t: {
                "requester": t.partner_id.name or "-",
                "age": dur(now - t.create_date),
                "priority": priority_labels.get(t.priority, "-"),
                "priority_code": t.priority or "0",
            })
        almost_overdue_rows = ticket_rows(
            domains["almost_overdue"], "sla_deadline asc", lambda t: {
                "assignee": t.user_id.name or "-",
                "deadline": fmt(t.sla_deadline),
                "remaining": dur(t.sla_deadline - now) if t.sla_deadline else "-",
            })
        overdue_rows = ticket_rows(
            domains["overdue"], "sla_deadline asc", lambda t: {
                "assignee": t.user_id.name or "-",
                "deadline": fmt(t.sla_deadline),
                "overdue": dur(now - t.sla_deadline) if t.sla_deadline else "-",
            })

        # --- Donut: tiket per status ---
        status_groups = self._read_group([cite_leaf], ["stage_id"], ["__count"])
        by_status = {
            "labels": [stage.name for stage, _count in status_groups],
            "counts": [count for _stage, count in status_groups],
        }

        # --- Tren 14 hari: created vs solved ---
        def day_counts(groups):
            res = {}
            for value, count in groups:
                if value:
                    res[value.date()] = count
            return res

        created_by_day = day_counts(self._read_group(
            [cite_leaf, ("create_date", ">=", trend_start)],
            ["create_date:day"], ["__count"]))
        solved_by_day = day_counts(self._read_group(
            [cite_leaf, ("resolved_date", ">=", trend_start)],
            ["resolved_date:day"], ["__count"]))
        trend = {"labels": [], "created": [], "solved": []}
        for i in range(14):
            day = trend_start_local + timedelta(days=i)
            trend["labels"].append(day.strftime("%d %b"))
            trend["created"].append(created_by_day.get(day.date(), 0))
            trend["solved"].append(solved_by_day.get(day.date(), 0))

        # --- Top solvers bulan ini ---
        per_user = {}
        for ticket in self.search([
                cite_leaf,
                ("resolved_date", ">=", month_start),
                ("user_id", "!=", False)]):
            entry = per_user.setdefault(ticket.user_id, {"count": 0, "sec": 0.0})
            entry["count"] += 1
            entry["sec"] += (ticket.resolved_date
                             - ticket.create_date).total_seconds()
        top_solvers = [{
            "name": user.name,
            "solved": entry["count"],
            "avg": dur(timedelta(seconds=entry["sec"] / entry["count"])),
        } for user, entry in sorted(per_user.items(),
                                    key=lambda kv: kv[1]["count"],
                                    reverse=True)[:5]]

        # --- SLA compliance (periode dipilih: day/week/month/year) ---
        sla = self._cite_sla_compliance(self._cite_period_start(sla_period))

        return {
            "kpis": kpis,
            "domains": domains,
            "views": {
                "tree": self.env.ref("cite_helpdesk.view_cite_ticket_tree").id,
                "form": self.env.ref("cite_helpdesk.view_cite_ticket_form").id,
            },
            "need_response": need_response_rows,
            "almost_overdue": almost_overdue_rows,
            "overdue": overdue_rows,
            "by_status": by_status,
            "trend": trend,
            "top_solvers": top_solvers,
            "sla": sla,
            "sla_period": sla_period,
            "last_update": fmt(now),
        }

    # ------------------------------------------------------------------
    # SLA compliance — bisa difilter periode (day/week/month/year)
    # ------------------------------------------------------------------

    def _cite_period_start(self, period):
        """Awal periode (UTC naive) di zona waktu user untuk gauge SLA."""
        tz = pytz.timezone(self.env.user.tz or "UTC")
        local_now = pytz.utc.localize(fields.Datetime.now()).astimezone(tz)
        day_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        if period == "day":
            start = day_start
        elif period == "week":
            start = day_start - timedelta(days=day_start.weekday())  # Senin
        elif period == "year":
            start = day_start.replace(month=1, day=1)
        else:  # month (default)
            start = day_start.replace(day=1)
        return start.astimezone(pytz.utc).replace(tzinfo=None)

    def _cite_sla_compliance(self, start):
        """Persentase tiket CITE yang memenuhi SLA sejak `start`."""
        now = fields.Datetime.now()
        in_progress_stage = self.env.ref(STAGE_XMLIDS["in_progress"],
                                         raise_if_not_found=False)
        stats = {"response": {"reached": 0, "failed": 0},
                 "resolution": {"reached": 0, "failed": 0}}
        # helpdesk.sla.status tak punya record rule company -> filter manual ke
        # company yang dicentang di switcher agar gauge konsisten dgn KPI dashboard.
        for sla_status in self.env["helpdesk.sla.status"].search(
                [("ticket_id.cite_ticket", "=", True),
                 ("ticket_id.company_id", "in", self.env.companies.ids),
                 ("ticket_id.create_date", ">=", start)]):
            kind = ("response"
                    if in_progress_stage
                    and sla_status.sla_id.stage_id == in_progress_stage
                    else "resolution")
            reached = sla_status.reached_datetime
            deadline = sla_status.deadline
            if reached and (not deadline or reached <= deadline):
                stats[kind]["reached"] += 1
            elif (reached and deadline and reached > deadline) or \
                    (not reached and deadline and deadline < now):
                stats[kind]["failed"] += 1

        def pct(entry):
            total = entry["reached"] + entry["failed"]
            return round(entry["reached"] * 100.0 / total) if total else None

        return {"response": pct(stats["response"]),
                "resolution": pct(stats["resolution"])}

    @api.model
    def get_cite_sla_compliance(self, period="month"):
        """Dipanggil dashboard saat dropdown periode SLA diubah."""
        return self._cite_sla_compliance(self._cite_period_start(period))
