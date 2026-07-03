# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class CiteHelpdeskCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(
            cls.env.context,
            no_reset_password=True,
            mail_create_nosubscribe=True,
            mail_notrack=True,
        ))
        Users = cls.env["res.users"].with_context(no_reset_password=True)

        cls.user_admin_l1 = Users.create({
            "name": "Andi IT Admin",
            "login": "andi.itadmin",
            "email": "andi.itadmin@example.com",
            "groups_id": [(4, cls.env.ref("base.group_user").id),
                          (4, cls.env.ref(
                              "cite_helpdesk.group_it_administrator").id)],
        })
        cls.user_heidi = Users.create({
            "name": "Heidi Lianawaty Lisan",
            "login": "heidi.test",
            "email": "heidi.test@example.com",
            "groups_id": [(4, cls.env.ref("base.group_user").id),
                          (4, cls.env.ref(
                              "cite_helpdesk.group_heidi_approver").id)],
        })
        cls.user_agent = Users.create({
            "name": "Budi Agent",
            "login": "budi.agent",
            "email": "budi.agent@example.com",
            "groups_id": [(4, cls.env.ref("base.group_user").id),
                          (4, cls.env.ref(
                              "cite_helpdesk.group_it_support").id)],
        })

        cls.team = cls.env.ref("cite_helpdesk.helpdesk_team_cite")
        cls.site = cls.env.ref("cite_helpdesk.site_ho_a")
        cls.cat_printer = cls.env.ref("cite_helpdesk.cat_printer")
        cls.sub_printer = cls.env.ref("cite_helpdesk.sub_prn_printer")
        cls.cat_access = cls.env.ref("cite_helpdesk.cat_access")
        cls.sub_acc_odoo = cls.env.ref("cite_helpdesk.sub_acc_odoo")
        cls.sub_sw_install = cls.env.ref("cite_helpdesk.sub_sw_installation")
        cls.cat_software = cls.env.ref("cite_helpdesk.cat_software")
        cls.partner = cls.env["res.partner"].create({
            "name": "Citra Requester",
            "email": "citra.requester@example.com",
        })

    def _create_ticket(self, **extra):
        vals = {
            "name": "Test ticket",
            "team_id": self.team.id,
            "partner_id": self.partner.id,
            "company_id": self.env.company.id,
            "site_id": self.site.id,
            "cite_category_id": self.cat_printer.id,
            "cite_subcategory_id": self.sub_printer.id,
            "impact": "individual",
            "urgency": "single_user",
        }
        vals.update(extra)
        return self.env["helpdesk.ticket"].create(vals)
