# -*- coding: utf-8 -*-
"""Batasi record rule RR-03 agar tidak menjangkau tiket helpdesk lain.

RR-03 ("Department Head read all tickets") lahir dengan domain [(1, '=', 1)]
supaya approver L2 bisa membaca tiket CITE lintas company. Efek sampingnya,
approver itu juga bisa membaca SELURUH tiket helpdesk lain di database yang
sama (mis. Stargo Helpdesk).

Record rule dibuat dengan noupdate=1, jadi perubahan pada security.xml tidak
diterapkan ke database yang sudah terpasang. Migration ini menerapkannya.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

NEW_DOMAIN = "[('cite_ticket', '=', True)]"


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rule = env.ref("cite_helpdesk.rule_ticket_heidi_read_all",
                   raise_if_not_found=False)
    if not rule:
        return
    if rule.domain_force == NEW_DOMAIN:
        return
    _logger.info("CITE Helpdesk: RR-03 domain %s -> %s",
                 rule.domain_force, NEW_DOMAIN)
    rule.domain_force = NEW_DOMAIN
