# -*- coding: utf-8 -*-
import base64

from markupsafe import Markup, escape

from odoo import _, http
from odoo.http import request
from odoo.addons.helpdesk.controllers.portal import (
    CustomerPortal as HelpdeskCustomerPortal)

MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25 MB / file (NFR / Bab 12.2)
MAX_ATTACHMENT_COUNT = 5                 # maks 5 lampiran per tiket


class CiteHelpdeskPortal(http.Controller):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _form_data(self):
        env = request.env
        user = env.user
        # Hanya company yang bisa diakses akun ini; default = company aktif
        # (yang sedang dicentang di company switcher).
        companies = user.company_ids
        default_company = (env.company if env.company in companies
                           else (user.company_id or companies[:1]))
        return {
            "companies": companies,
            "departments": env["hr.department"].sudo().search(
                [("cite_department", "=", True)], order="name"),
            "sites": env["cite.site"].sudo().search([]),
            "categories": env["cite.category"].sudo().search([]),
            "subcategories": env["cite.subcategory"].sudo().search([]),
            "ticket_types": env["helpdesk.ticket.type"].sudo().search([]),
            "default_company": default_company,
            "default_partner": user.partner_id,
        }

    # ------------------------------------------------------------------
    # Routes (Bab 12.1 / 24)
    # ------------------------------------------------------------------

    @http.route("/citehelpdesk2", type="http", auth="user", website=True,
                sitemap=False)
    def landing(self, **kw):
        categories = request.env["cite.category"].sudo().search([])
        return request.render("cite_helpdesk.portal_landing", {
            "categories": categories,
        })

    @http.route("/citehelpdesk2/my-tickets", type="http", auth="user",
                website=True, sitemap=False)
    def my_tickets(self, **kw):
        env = request.env
        team = env.ref("cite_helpdesk.helpdesk_team_cite",
                       raise_if_not_found=False)
        # Hanya tiket CITE milik user — terpisah dari helpdesk lain (Stargo).
        domain = [("partner_id", "=", env.user.partner_id.id)]
        if team:
            domain.append(("team_id", "=", team.id))
        tickets = env["helpdesk.ticket"].sudo().search(
            domain, order="create_date desc")
        return request.render("cite_helpdesk.portal_my_tickets", {
            "tickets": tickets,
        })

    # ------------------------------------------------------------------
    # Detail tiket — route MILIK CITE sendiri (ter-namespace, tidak memakai
    # /my/ticket bawaan yang membuang ke /my saat cek akses gagal).
    # ------------------------------------------------------------------

    def _cite_get_ticket(self, ticket_id):
        """Ambil tiket CITE bila user berhak; selain itu None."""
        env = request.env
        ticket = env["helpdesk.ticket"].sudo().browse(int(ticket_id))
        if not ticket.exists() or not ticket.team_id.cite_team:
            return None
        user = env.user
        is_owner = ticket.partner_id and ticket.partner_id == user.partner_id
        is_agent = user.has_group("helpdesk.group_helpdesk_user")
        return ticket if (is_owner or is_agent) else None

    def _cite_public_messages(self, ticket):
        """Hanya percakapan publik (komentar/email), bukan catatan internal."""
        return ticket.message_ids.filtered(
            lambda m: not m.is_internal
            and m.message_type in ("comment", "email"))

    @http.route("/citehelpdesk2/ticket/<int:ticket_id>", type="http",
                auth="user", website=True, sitemap=False)
    def cite_ticket(self, ticket_id, **kw):
        ticket = self._cite_get_ticket(ticket_id)
        if not ticket:
            return request.redirect("/citehelpdesk2/my-tickets")
        return request.render("cite_helpdesk.portal_cite_ticket", {
            "ticket": ticket,
            "messages": self._cite_public_messages(ticket),
            "error": kw.get("error"),
        })

    @http.route("/citehelpdesk2/ticket/<int:ticket_id>/reply", type="http",
                auth="user", website=True, methods=["POST"], csrf=True)
    def cite_ticket_reply(self, ticket_id, **post):
        ticket = self._cite_get_ticket(ticket_id)
        if not ticket:
            return request.redirect("/citehelpdesk2/my-tickets")
        env = request.env
        body_text = (post.get("message") or "").strip()

        # Lampiran balasan (maks 5 file, 25MB/file).
        uploads = request.httprequest.files.getlist("attachments")
        attachments = env["ir.attachment"].sudo()
        for upload in uploads:
            if not upload or not upload.filename:
                continue
            data = upload.read()
            if not data or len(data) > MAX_ATTACHMENT_SIZE:
                continue
            attachments |= env["ir.attachment"].sudo().create({
                "name": upload.filename,
                "datas": base64.b64encode(data),
                "res_model": "helpdesk.ticket",
                "res_id": ticket.id,
            })
            if len(attachments) >= MAX_ATTACHMENT_COUNT:
                break

        if not body_text and not attachments:
            return request.redirect(
                "/citehelpdesk2/ticket/%s?error=%s"
                % (ticket.id, _("Write a message or attach a file first.")))

        body = Markup("<p>%s</p>") % escape(body_text) if body_text else Markup("")
        if body_text:
            body = Markup(str(body).replace("\n", "<br/>"))
        for att in attachments:
            if (att.mimetype or "").startswith("image/"):
                body += Markup(
                    '<div class="mb-2"><img src="/web/image/%s" alt="%s" '
                    'style="max-width:100%%;max-height:320px;border:1px solid '
                    '#dee2e6;border-radius:4px"/></div>') % (att.id, escape(att.name))
            else:
                body += Markup(
                    '<div class="mb-1">📎 <a href="/web/content/%s?download=true">'
                    '%s</a></div>') % (att.id, escape(att.name))

        # message_post sbg requester -> memicu AA-05 (Waiting User -> In Progress).
        message = ticket.sudo().message_post(
            body=body, attachment_ids=attachments.ids,
            author_id=env.user.partner_id.id,
            message_type="comment", subtype_xmlid="mail.mt_comment")
        if attachments:
            message.sudo().attachment_ids = [(6, 0, attachments.ids)]
        return request.redirect("/citehelpdesk2/ticket/%s" % ticket.id)

    @http.route("/citehelpdesk2/new", type="http", auth="user", website=True,
                methods=["GET"], sitemap=False)
    def new_ticket(self, **kw):
        values = self._form_data()
        values["error"] = kw.get("error")
        # Pra-pilih kategori bila dibuka dari kartu "Kategori Bantuan Populer".
        values["selected_category"] = kw.get("category")
        return request.render("cite_helpdesk.portal_ticket_form", values)

    @http.route("/citehelpdesk2/submit", type="http", auth="user",
                website=True, methods=["POST"], csrf=True)
    def submit_ticket(self, **post):
        env = request.env
        # Sub Category sengaja tidak diminta di portal — diisi tim IT di backend.
        required = ("name", "company_id", "department_id", "site_id",
                    "cite_category_id", "impact", "urgency", "description")
        if any(not post.get(field) for field in required):
            return request.redirect(
                "/citehelpdesk2/new?error=" + _("Please fill in all required fields."))

        # Keamanan: pastikan company yang dikirim memang boleh diakses user
        # (cegah manipulasi POST ke company lain).
        company_id = int(post["company_id"])
        if company_id not in env.user.company_ids.ids:
            return request.redirect(
                "/citehelpdesk2/new?error=" + _("Invalid company selection."))

        team = env.ref("cite_helpdesk.helpdesk_team_cite",
                       raise_if_not_found=False)
        description = Markup("<p>%s</p>") % escape(post["description"])
        description = Markup(str(description).replace("\n", "<br/>"))
        vals = {
            "name": post["name"],
            "description": description,
            "partner_id": env.user.partner_id.id,
            "company_id": company_id,
            "department_id": int(post["department_id"]),
            "site_id": int(post["site_id"]),
            "cite_category_id": int(post["cite_category_id"]),
            "impact": post["impact"],
            "urgency": post["urgency"],
        }
        if team:
            vals["team_id"] = team.id
        if post.get("ticket_type_id"):
            vals["ticket_type_id"] = int(post["ticket_type_id"])
        else:
            category = env["cite.category"].sudo().browse(
                int(post["cite_category_id"]))
            if category.ticket_type_id:
                vals["ticket_type_id"] = category.ticket_type_id.id

        ticket = env["helpdesk.ticket"].with_company(
            company_id).sudo().create(vals)

        # Lampiran: maks 5 file, 25MB/file. Diposting sebagai komentar publik
        # atas nama requester dengan preview gambar agar tampil di percakapan.
        uploads = request.httprequest.files.getlist("attachments")
        attachments = env["ir.attachment"].sudo()
        for upload in uploads:
            if not upload or not upload.filename:
                continue
            data = upload.read()
            if not data or len(data) > MAX_ATTACHMENT_SIZE:
                continue
            attachments |= env["ir.attachment"].sudo().create({
                "name": upload.filename,
                "datas": base64.b64encode(data),
                "res_model": "helpdesk.ticket",
                "res_id": ticket.id,
            })
            if len(attachments) >= MAX_ATTACHMENT_COUNT:
                break

        if attachments:
            body = Markup("<p>%s</p>") % _("Attachments from requester:")
            for att in attachments:
                if (att.mimetype or "").startswith("image/"):
                    body += Markup(
                        '<div class="mb-2"><img src="/web/image/%s" '
                        'alt="%s" style="max-width:100%%;max-height:320px;'
                        'border:1px solid #dee2e6;border-radius:4px"/></div>'
                    ) % (att.id, escape(att.name))
                else:
                    body += Markup(
                        '<div class="mb-1">📎 <a href="/web/content/%s?'
                        'download=true">%s</a></div>'
                    ) % (att.id, escape(att.name))
            message = ticket.sudo().message_post(
                body=body,
                attachment_ids=attachments.ids,
                author_id=env.user.partner_id.id,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
            # Pastikan lampiran tertaut ke pesan agar tampil sebagai preview
            # native di portal (selain gambar inline pada body).
            message.sudo().attachment_ids = [(6, 0, attachments.ids)]

        # Arahkan ke detail tiket CITE (bukan /my/ticket bawaan).
        return request.redirect("/citehelpdesk2/ticket/%s" % ticket.id)


class CiteHelpdeskNativeSeparation(HelpdeskCustomerPortal):
    """Pisahkan TOTAL CITE dari portal helpdesk bawaan (/my/tickets, /my/ticket).

    Tiket CITE punya portal sendiri di /citehelpdesk2; di sini kita:
      - sembunyikan tiket CITE dari daftar & hitungan portal bawaan, dan
      - alihkan akses /my/ticket/<id> tiket CITE ke /citehelpdesk2/ticket/<id>.
    """

    def _prepare_helpdesk_tickets_domain(self):
        domain = super()._prepare_helpdesk_tickets_domain()
        # Hanya tiket NON-CITE yang tampil di portal helpdesk bawaan.
        return domain + [("team_id.cite_team", "=", False)]

    @http.route([
        "/helpdesk/ticket/<int:ticket_id>",
        "/helpdesk/ticket/<int:ticket_id>/<access_token>",
        "/my/ticket/<int:ticket_id>",
        "/my/ticket/<int:ticket_id>/<access_token>",
    ], type="http", auth="public", website=True)
    def tickets_followup(self, ticket_id=None, access_token=None, **kw):
        if ticket_id:
            ticket = request.env["helpdesk.ticket"].sudo().browse(int(ticket_id))
            # Tiket CITE -> halaman CITE sendiri (user login). Akses tamu via
            # token tetap memakai halaman bawaan agar tidak memaksa login.
            if (ticket.exists() and ticket.team_id.cite_team
                    and not request.env.user._is_public()):
                return request.redirect(
                    "/citehelpdesk2/ticket/%s" % ticket.id)
        return super().tickets_followup(
            ticket_id=ticket_id, access_token=access_token, **kw)
