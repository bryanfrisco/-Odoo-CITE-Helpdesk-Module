# CITE Helpdesk (`cite_helpdesk`)

Modul Odoo **17.0 Enterprise** — realisasi blueprint *CITE Helpdesk: IT Helpdesk & ITSM*.
Prinsip: **native-first** (Helpdesk, Maintenance, Rating, Portal) + custom ringan untuk
4 area yang tidak tersedia native: ticket numbering, auto-priority matrix, double
approval, dan SLA warning 75%/90%.

**Versi:** 17.0.1.4.3.

> **Multi-company:** satu tim CITE melayani 3 company. `company_id` tiket di-override
> menjadi field biasa (native helpdesk memaksa `related='team_id.company_id'` readonly),
> sehingga company yang dipilih di portal benar-benar tersimpan per-tiket; constraint
> partner-company native di-relax khusus tim CITE. **Dashboard Overview mengikuti
> company switcher**: centang 1 company → hanya tiket company itu; centang beberapa →
> gabungan (record rule native + filter `ticket_id.company_id` pada gauge SLA).
> Filter CITE memakai flag tersimpan `cite_ticket` (related `team_id.cite_team`,
> store) — **bukan** traversal `team_id.cite_team` di domain, karena traversal
> memicu record rule multi-company `helpdesk.team`: saat company tim tidak
> dicentang di switcher, tim "hilang" dan semua tiket CITE ikut lenyap walau
> company tiketnya dicentang.
> Catatan data: tiket yang dibuat **sebelum** fix 1.3.1 menyimpan company lama
> (company tim) — muncul hanya bila company tsb dicentang; tiket baru mengikuti
> pilihan company di portal.

> **Hidup berdampingan dengan helpdesk lain (mis. "Stargo Helpdesk").** CITE
> Helpdesk dirancang **terpisah total** dari helpdesk bawaan di database yang sama:
> tiap `helpdesk.team` CITE ditandai field `cite_team=True`, dan SELURUH
> view/action/dashboard/cron CITE difilter `team_id.cite_team=True` agar tiket tim
> lain tidak bocor. Portal CITE memakai namespace `/citehelpdesk2/*` sendiri
> (bukan `/my/tickets` bawaan) — tiket CITE disembunyikan dari portal helpdesk
> bawaan dan akses `/my/ticket/<id>` tiket CITE dialihkan ke `/citehelpdesk2/ticket/<id>`.

## Dependencies

`helpdesk` (Enterprise), `maintenance`, `hr`, `portal`, `website`,
`website_helpdesk`, `website_helpdesk_knowledge` (menarik `knowledge`).
Halaman portal `/citehelpdesk2` memakai `website.layout` (theme + Website
Builder); CITE Helpdesk Team otomatis aktif: Website Form, Help Center
Knowledge, dan Customer Ratings (CSAT).

## Deployment ke Production (stargo.odoo.com / Odoo.sh)

1. Salin folder `cite_helpdesk/` ke root repository Odoo.sh, push ke branch **dev**
   (unit test berjalan otomatis saat build).
2. Merge ke **staging** untuk UAT, lalu ke **production**.
3. Pasca-install di production:
   - 3 company sudah ada (PT Stargate Pasific Resources / PT Rajawali Sigi Lestari /
     PT Stargate Mineral Asia) — modul otomatis membuat 2 lokasi generik
     **Head Office** & **Site** yang berlaku untuk semua company (tidak
     terikat company tertentu).
   - 15 departemen (CITE, ENGI, MPMA, MEMD, HCGS, CFAT, CPMD, CSUS, MIOP, EXPL,
     QLAB, LEGL, CDRE, GOVREL, SMDE) dibuat otomatis saat install.
   - Isi anggota group (IT Support/Administrator/Manager) dan **tepat satu user**
     di group *Heidi Approver* (Heidi Lianawaty Lisan).
   - Ikuti checklist lengkap di bagian *Konfigurasi Pasca-Install* di bawah.
4. Portal user: `https://stargo.odoo.com/citehelpdesk2`.

## Instalasi

```bash
# Odoo.sh / on-premise — letakkan folder cite_helpdesk di addons path
odoo-bin -d <db> -i cite_helpdesk

# Dengan demo data (Company B/C, sites, user Heidi, contoh aset):
odoo-bin -d <db> -i cite_helpdesk --without-demo=False

# Unit tests:
odoo-bin -d <db> -i cite_helpdesk --test-tags /cite_helpdesk --stop-after-init
```

> ⚠ **Odoo Online (SaaS) tidak mendukung modul Python custom** — deployment target
> adalah **Odoo.sh** atau on-premise (Bab 28 blueprint).

## Yang Disediakan Modul

| Area | Implementasi |
|---|---|
| Ticket numbering | `ir.sequence` `IT-%(year)s-XXXXX`, reset tahunan, global lintas company |
| Priority matrix | Compute server-side `impact × urgency` (20 kombinasi), readonly semua user |
| Double approval | L1 group **IT Administrator** → L2 group **Heidi Approver**; guard `write()` anti-bypass; segregation of duty; reject wizard dengan alasan wajib; tiket Rejected terkunci |
| Stages | 10 stage (Open → … → Closed/Cancelled/Rejected) + field `is_close`. `post_init_hook` mengunci CITE Helpdesk Team ke 10 stage ini dan menghapus stage generik + team default bawaan helpdesk bila kosong (non-destruktif: dilewati bila ada tiket) |
| Departemen | 15 departemen dibuat saat install: CITE, ENGI, MPMA, MEMD, HCGS, CFAT, CPMD, CSUS, MIOP, EXPL, QLAB, LEGL, CDRE, GOVREL, SMDE |
| SLA | 8 policy native — Response (Critical 1j / High 2j / Medium 4j / Low 4j) & Resolution (Critical 3hari / High 4hari / Medium 5hari / Low 5hari, jam kerja), exclude *Waiting User*; cron warning 75%/90% + breach alert (per 10 menit). Nilai diterapkan ke DB lama via `migrations/17.0.1.2.0/` |
| Auto close | Cron harian: Resolved + 3 hari tanpa respon requester → Closed |
| Approval reminder | Cron harian: pending > 24 jam → email reminder approver |
| Waiting User | Balasan requester (portal/email) otomatis mengembalikan ke In Progress |
| Asset registry | Extend `maintenance.equipment`: asset_code (unik), brand, site, warranty_end_date, asset_status, riwayat tiket per aset, cron warranty 30 hari |
| Email | 14 template (ET-01…ET-15; ET-10 memakai notifikasi follower native) + **routing CITE**: tiap tiket baru tembusan ke kontak `cite@aspire.id` (CC + follower, `data/cite_mail_routing.xml`); **approval L1 → cite@aspire.id**, **approval L2 → grup *Heidi Approver* (heidi.lianawaty@aspire.id)** |
| Security | 6 group + record rules + access rights; `unlink` tiket hanya System Admin |
| Portal (namespace `/citehelpdesk2`) | `/citehelpdesk2` (landing website.layout) · `/citehelpdesk2/new` (form: Company mengikuti akun login, dropdown Lokasi, lampiran ≤25MB, label Impact/Urgency bahasa awam) · `/citehelpdesk2/my-tickets` (daftar tiket CITE milik user) · `/citehelpdesk2/ticket/<id>` (detail: info + status approval 2 level + percakapan + **form balas** dengan lampiran) |
| Dashboard | Menu **Overview** (client action OWL): 6 KPI cards klik-tembus, 3 tabel operasional, donut status, tren 14 hari, top solvers, gauge **SLA Compliance dengan filter periode (Day/Week/Month/Year)**, auto-refresh 60 detik |
| Master data | 8 category + subcategory + approval matrix via flag (dapat diubah admin tanpa coding), 2 lokasi generik (Head Office / Site, lintas company). Ikon kategori & flag `cite_team` ditegaskan tiap upgrade via `<function>` `_cite_post_deploy_sync` (kebal noupdate) |
| Portal | Sub Category disembunyikan dari portal (diisi tim IT di backend); lampiran maks 5 file ditampilkan sebagai komentar (preview gambar + link dokumen) |
| Tests | Priority matrix (20 kombinasi), sequence, approval flow + guard + lock + segregation |

## Konfigurasi Pasca-Install (wajib sebelum go-live)

1. **Companies & Sites** — buat `res.company` B & C (sudah ada di production
   Stargate). Lokasi `Head Office` & `Site` dibuat otomatis dan berlaku
   lintas company; tambah lokasi lain bila perlu via
   *CITE Helpdesk → Master Data → Sites*.
2. **Anggota group** — isi *Settings → Users & Groups*:
   IT Support / Infrastructure / Application / IT Administrator / IT Manager,
   dan **tepat satu user** pada *Heidi Approver* (Heidi Lianawaty Lisan).
   Tambahkan agen ke **member** CITE Helpdesk Team (untuk balanced assignment).
3. **Working calendar** — set kalender kerja team (Sen–Jum 08.00–17.00 WIB);
   pertimbangkan kalender 24/7 terpisah untuk Critical bila ada on-call.
4. **Email** — alias team CITE sudah di-set **`cite`** (terpisah dari helpdesk
   Stargo). Konfigurasi **Outgoing Mail (SMTP)** agar email benar-benar terkirim.
   Routing CITE sudah otomatis: tiap tiket baru tembusan ke kontak **`cite@aspire.id`**
   (CC + follower) — ubah alamat cukup lewat kontak "CITE Helpdesk", tanpa coding.
   Approval L2 menyasar email user di grup *Heidi Approver* → set email user Heidi
   ke **`heidi.lianawaty@aspire.id`**. (Opsional) agar email masuk ke `cite@aspire.id`
   otomatis jadi tiket: set **Alias Domain** `aspire.id` + arahkan MX-nya ke Odoo.
5. **Multi-company** — beri user IT `allowed_company_ids` = A, B, C
   (tim IT shared-service grup).
6. **Knowledge Base** — publish ≥20 artikel KB sebelum go-live
   (Help Center & Customer Ratings sudah aktif otomatis di team).
8. **Stage bawaan team** — saat team dibuat, Odoo dapat menautkan stage generik
   bawaan (New/Solved/…); lepaskan dari team agar hanya 10 stage CITE yang tampil.
9. **Dashboard** — bangun dashboard "CITE IT Management" (Bab 21) dengan
   *Dashboards/Spreadsheet* dari pivot Helpdesk (klik *Insert in Spreadsheet*).

## Catatan Teknis / Titik Verifikasi

Modul ini ditulis terhadap API Odoo 17; beberapa titik bergantung pada detail
build Enterprise dan **perlu diverifikasi saat install pertama di staging**:

- **Pemisahan dari helpdesk bawaan** (`controllers/portal.py` → class
  `CiteHelpdeskNativeSeparation`): override `_prepare_helpdesk_tickets_domain`
  (sembunyikan tiket `cite_team` dari `/my/tickets`) + override `tickets_followup`
  (alihkan `/my/ticket/<id>` tiket CITE ke `/citehelpdesk2/ticket/<id>`).
- **Data dikelola modul dengan noupdate=1** (team, kategori, SLA): perubahan pada
  DB lama TIDAK diterapkan via `<record>` (flag noupdate di `ir.model.data`).
  Solusi: `<function>` `_cite_post_deploy_sync` (ikon + `cite_team`, tiap upgrade)
  dan migration `migrations/17.0.1.2.0/` (nilai SLA, sekali saat naik versi).
- `views/portal_templates.xml` → template `portal_ticket_approval_status`
  meng-inherit `helpdesk.tickets_followup` dengan anchor generik
  (`//t[@t-call='portal.portal_layout']`). Bila build Anda memakai id/struktur
  lain, sesuaikan `inherit_id`/xpath (file terisolasi, mudah disesuaikan).
- `views/maintenance_views.xml` → xpath `serial_no` & `button_box` pada form
  Maintenance; sesuaikan bila layout native berbeda.
- `helpdesk.stage.is_close` ditambahkan oleh modul ini (digunakan guard & cron).
- Field native yang dipakai dan diasumsikan ada: `sla_fail`, `sla_status_ids`,
  `sla_deadline`, `ticket_ref` (di-overwrite dengan sequence CITE saat create),
  `assign_method='balanced'` pada team.
- Tombol "Edit in backend" pada email memakai URL `/odoo/helpdesk/<id>`
  (format URL Odoo 17); ganti bila memakai versi lain.

## Struktur

```
cite_helpdesk/
├── controllers/portal.py          # /citehelpdesk2 (+ new, submit, my-tickets,
│                                  # ticket/<id>, reply) + pemisahan portal bawaan
├── data/                          # sequence, team, 10 stages, types, 8 SLA,
│                                  # master data, cite_post_deploy (<function>),
│                                  # cite_mail_routing (cite@aspire.id),
│                                  # activity types, 14 mail tpl, 4 cron
├── demo/demo_data.xml             # Company B/C + sites + Heidi + contoh aset
├── migrations/17.0.1.2.0/         # post-migrate: terapkan nilai SLA baru
├── models/
│   ├── cite_site.py               # cite.site
│   ├── cite_category.py           # cite.category + cite.subcategory
│   ├── helpdesk_team.py           # + cite_team flag + _cite_post_deploy_sync
│   ├── helpdesk_stage.py          # + is_close
│   ├── helpdesk_ticket.py         # field, priority, approval, guards, crons, dashboard
│   └── maintenance_equipment.py   # IT asset fields + warranty cron
├── security/                      # groups, record rules, ACL
├── static/src/                    # portal JS + dashboard OWL (JS/XML/SCSS)
├── tests/                         # priority matrix, sequence, approval flow
├── views/                         # ticket views, master data, maintenance,
│                                  # portal templates, menu
└── wizard/ticket_reject_wizard.py # alasan reject wajib
```
