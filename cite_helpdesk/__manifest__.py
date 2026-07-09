# -*- coding: utf-8 -*-
{
    "name": "CITE Helpdesk",
    "summary": "IT Helpdesk & ITSM — Single Point of Contact untuk seluruh kebutuhan IT grup",
    "description": """
CITE Helpdesk — IT Helpdesk & IT Service Management (ITSM)
==========================================================
Implementasi blueprint CITE Helpdesk di atas Odoo 17 Enterprise.
Native-first: Helpdesk, Maintenance (IT Asset Registry), Portal, Rating.
Custom ringan: auto-priority matrix, double approval (IT Administrator +
Heidi Lianawaty Lisan), ticket numbering IT-YYYY-XXXXX, SLA warning 75%/90%,
auto-close, portal self-service /citehelpdesk2.
""",
    "version": "17.0.1.4.4",
    "category": "Services/Helpdesk",
    "author": "CITE",
    "website": "https://stargo.odoo.com/citehelpdesk2",
    "license": "OPL-1",
    "depends": [
        "helpdesk",       # Enterprise — tiket, SLA, rating, portal
        "maintenance",    # IT Asset Registry
        "hr",             # Department / Employee defaults
        "portal",
        "website",        # FR-02 — portal sebagai website page (theme/builder)
        "website_helpdesk",            # Help Center team
        "website_helpdesk_knowledge",  # FR-09 — KB search di Help Center
    ],
    "data": [
        # security
        "security/security.xml",
        "security/ir.model.access.csv",
        # data (urutan penting: team -> stages -> types -> SLA -> master)
        "data/ir_sequence.xml",
        "data/helpdesk_team.xml",
        "data/helpdesk_stage.xml",
        "data/helpdesk_ticket_type.xml",
        "data/helpdesk_sla.xml",
        "data/cite_master_data.xml",
        "data/cite_post_deploy.xml",
        "data/hr_department.xml",
        "data/mail_activity_type.xml",
        "data/cite_mail_routing.xml",
        "data/mail_templates.xml",
        "data/ir_cron.xml",
        # wizard & views
        "wizard/ticket_reject_wizard_views.xml",
        "views/helpdesk_ticket_views.xml",
        "views/cite_master_views.xml",
        "views/maintenance_views.xml",
        "views/portal_templates.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "cite_helpdesk/static/src/js/portal_form.js",
            "cite_helpdesk/static/src/scss/portal.scss",
        ],
        "web.assets_backend": [
            "cite_helpdesk/static/src/dashboard/**/*",
        ],
    },
    "application": True,
    "installable": True,
    "post_init_hook": "post_init_hook",
}
