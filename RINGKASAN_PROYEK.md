# RINGKASAN PROYEK — CITE Helpdesk (Odoo 17 Enterprise)

> Salin seluruh dokumen ini ke chat baru (mis. Claude web) sebagai konteks lengkap proyek.

## 1. Apa proyek ini

Modul custom Odoo bernama **`cite_helpdesk`** di `d:\CITE Helpdesk Module\cite_helpdesk\`,
dibangun dari dokumen blueprint `CITE_Helpdesk_Design_Blueprint.md` — sistem IT Helpdesk/ITSM
(Single Point of Contact) untuk grup 3 perusahaan (Company A/B/C, masing-masing Head Office + Site).
Prinsip: native-first (Helpdesk Enterprise, Maintenance, Rating, Website, Knowledge) + custom ringan.

**Status: SELESAI & BERJALAN di localhost. Terinstall di database `cite_helpdesk`, 16/16 unit test lulus.**

## 2. Fitur yang sudah diimplementasi

- **Penomoran tiket** `IT-YYYY-XXXXX` (ir.sequence, reset tahunan, global lintas company).
- **Auto-priority matrix**: Impact (company/site/department/individual) × Urgency (site_down/dept_down/multi_user/single_user/request) → Priority Low/Medium/High/Critical; computed server-side, readonly.
- **Double approval**: kategori tertentu wajib Approval L1 (group *IT Administrator*) lalu L2 (group *Heidi Approver* — Heidi Lianawaty Lisan). Guard anti-bypass di `write()`, segregation of duty (tidak bisa approve tiket sendiri), reject wizard dengan alasan wajib, tiket Rejected/Closed/Cancelled terkunci, unlink hanya System Admin.
- **10 stages** (Draft dihapus, tiket langsung mulai di Open): Open, Awaiting Admin Approval, Awaiting Final Approval, Assigned, In Progress, Waiting User, Resolved, Closed, Cancelled, Rejected (+field `is_close`). Tiap tiket menampilkan **Time in Stage** (lama di stage saat ini) di list/form/kanban.
- **Master data riil (sudah di DB lokal)**: 3 company = PT Stargate Pasific Resources / PT Rajawali Sigi Lestari / PT Stargate Mineral Asia; **2 lokasi generik** (field "Lokasi" = cite.site) = Head Office (HO) & Site (ST), berlaku lintas company (company_id kosong); 15 departemen = CITE, ENGI, MPMA, MEMD, HCGS, CFAT, CPMD, CSUS, MIOP, EXPL, QLAB, LEGL, CDRE, GOVREL, SMDE; **8 kategori** (Procurement Request dihapus). Data demo helpdesk (tim Customer Care/VIP Support, 23 tiket furniture, stage New/Solved/Canceled) sudah DIHAPUS dari DB. Field Asset dihapus dari form tiket; **Sub Category disembunyikan dari portal** (diisi tim IT di backend); **lampiran portal maks 5 file** tampil di komentar tiket (preview gambar + link dokumen); label Impact/Urgency bahasa awam; requester auto-terisi user login; dashboard membuka form CITE (bukan form native).
- **Paket production**: `cite_helpdesk_production.zip` (root workspace) = modul tanpa folder `demo/` & tanpa `__pycache__`, manifest sudah dilepas blok demo. Fresh-install tanpa demo terverifikasi bersih (10 stage, hanya CITE team, 8 kategori, lokasi HO/Site).
- **8 SLA policies** native (Response per priority: Critical 1j/High 2j/Medium 4j/Low 4j; Resolution: Critical 3hari/High 4hari/Medium 5hari/Low 5hari — jam kerja), exclude stage Waiting User. Gauge SLA Compliance di dashboard bisa difilter periode (Day/Week/Month/Year).
- **4 cron**: SLA warning 75%/90% + breach alert (tiap 10 menit), auto-close Resolved+3 hari, reminder approval >24 jam, alert garansi aset ≤30 hari.
- **Balasan requester saat Waiting User** otomatis kembali ke In Progress.
- **Asset registry**: extend `maintenance.equipment` (asset_code unik, brand, site, warranty_end_date, asset_status, riwayat tiket per aset).
- **14 email template** (ET-01…ET-15; ET-10 pakai notifikasi follower native). Lokal tanpa SMTP → email hanya antre di Settings → Technical → Emails.
- **Security**: 6 groups (IT Support, Infrastructure, Application, IT Administrator, Heidi Approver, IT Manager), record rules, ACL.
- **Master data**: 9 category + 38 subcategory (flag `require_approval` per category/subcategory = approval matrix yang bisa diubah admin tanpa coding), sites.
- **Portal website** (pakai `website.layout`, bisa diedit Website Builder):
  - `/citehelpdesk2` — landing (auth login)
  - `/citehelpdesk2/new` — form tiket; **dropdown Company hanya menampilkan company yang boleh diakses akun login** (default = company aktif, ada guard server-side anti-manipulasi POST), upload lampiran ≤25MB
  - `/citehelpdesk2/my-tickets` — **halaman "My Tickets" khusus CITE** (hanya tiket tim CITE milik user), terpisah dari `/my/tickets` bawaan (Stargo) + detail tiket portal + panel status approval 2 level
  - `/helpdesk` Help Center + `/knowledge` (modul knowledge terpasang)
- **Team**: CITE Helpdesk Team, alias email `cite` (terpisah dari helpdesk Stargo), assign balanced, rating CSAT aktif, Help Center Knowledge aktif.
- **Email routing** (lihat §7): setiap tiket baru tembusan ke **cite@aspire.id** (CC + follower); **approval L1 → cite@aspire.id**, **approval L2 → heidi.lianawaty@aspire.id** (anggota grup *Heidi Approver*).
- **Dashboard "Overview"** (menu pertama app CITE Helpdesk; client action OWL `cite_helpdesk.dashboard`):
  6 KPI cards (Total Open, Need Response, On Progress, Almost Overdue, Overdue, Solved Today — klik-tembus ke list),
  3 tabel operasional, donut Tickets by Status (Chart.js), line Tickets Trend 14 hari (Created vs Solved),
  Top Ticket Solvers bulan ini, gauge SLA Compliance Response/Resolution, auto-refresh 60 detik + Last Updated.
  Data dari method `helpdesk.ticket.get_cite_dashboard_data()`; file di `static/src/dashboard/`.
- **Unit tests**: tests/ — priority matrix (20 kombinasi), sequence, approval flow/guard/lock/segregation.

## 3. Lingkungan lokal (Windows 11)

| Komponen | Detail |
|---|---|
| Odoo | 17.0 **Enterprise** installer di `C:\Program Files\Odoo 17.0e.20260609`; service Windows `odoo-server-17.0`, port **8069** (gevent 8072) |
| odoo.conf | `C:\Program Files\Odoo 17.0e.20260609\server\odoo.conf` — `addons_path` sudah memuat `d:\CITE Helpdesk Module`; master password database: `admin` |
| PostgreSQL | v18, service `postgresql-x64-18`, port 5432; role **openpg / openpgpwd** |
| Database | `cite_helpdesk` (terinstall modul + demo data: Company B/C, 6 site, contoh aset LT-001/PRN-005/SRV-002) |
| Jalankan CLI terpisah | pakai python bawaan: `"C:\Program Files\Odoo 17.0e.20260609\python\python.exe" "C:\Program Files\Odoo 17.0e.20260609\server\odoo-bin" -d cite_helpdesk ... --http-port=8070 --gevent-port=8073 --data-dir=%LOCALAPPDATA%\OdooCite` |
| Upgrade modul | tambah `-u cite_helpdesk --stop-after-init`, lalu **restart service** `odoo-server-17.0` (butuh admin/UAC) |
| Jalankan test | tambah `--test-tags /cite_helpdesk --stop-after-init` |

**Keanehan penting (PG18 + Windows):** Odoo TIDAK bisa membuat database sendiri
(error "collations with different collate and ctype"). Buat manual dulu:
`CREATE DATABASE namadb OWNER openpg ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0;`

## 4. Akun (lokal, untuk testing)

| Peran | Login | Password |
|---|---|---|
| Odoo Administrator | `admin` | `admin` |
| Approver L1 (IT Administrator) | `itadmin` | `itadmin123` |
| Approver L2 (Heidi) | `heidi.lisan` | `heidi123` |
| Karyawan portal (requester) | `karyawan` | `karyawan123` |

Alur uji: login `karyawan` → buat tiket kategori **Access** di `/citehelpdesk2/new` →
login `itadmin` → CITE Helpdesk → Approval Waiting List → **Approve (Admin)** →
login `heidi.lisan` → **Approve (Heidi)** → tiket otomatis *Assigned*.

## 5. Bug yang ditemukan & solusinya (sudah diperbaiki di kode)

1. Service Odoo bawaan gagal konek DB sejak install → role `openpg` dibuat ulang
   (via pg_hba trust sementara; backup `pg_hba.conf.bak-cite` masih ada di data dir PG).
2. Tree view tiket: `stage_id` punya domain merujuk `team_id` → wajib ada
   `<field name="team_id" column_invisible="1"/>` di tree.
3. `create()` native helpdesk SELALU menimpa `vals['ticket_ref']` dengan sequence
   `helpdesk.ticket` → nomor CITE harus ditulis SETELAH `super().create()`.
4. PowerShell pipe ke `odoo-bin shell` rusak encoding → tulis skrip ke file lalu
   `cmd /c "type file | odoo-bin shell -d cite_helpdesk --no-http"`.

## 6. Struktur modul

```
cite_helpdesk/
├── __manifest__.py        # depends: helpdesk, maintenance, hr, portal, website,
│                          #          website_helpdesk, website_helpdesk_knowledge
├── controllers/portal.py  # /citehelpdesk2, /citehelpdesk2/new, /citehelpdesk2/submit
├── data/                  # sequence, team, 11 stages, 3 ticket types, 8 SLA,
│                          # master data, 2 activity types, 14 mail templates, 4 cron
├── demo/demo_data.xml     # Company B/C, sites, user Heidi, contoh aset
├── models/                # cite_site, cite_category(+sub), helpdesk_stage (is_close),
│                          # helpdesk_ticket (inti), maintenance_equipment
├── security/              # security.xml (groups+rules), ir.model.access.csv
├── static/src/            # js/portal_form.js (dependent dropdown), scss/portal.scss
├── tests/                 # common, test_priority_matrix, test_sequence, test_approval_flow
├── views/                 # ticket views (standalone, bukan inherit), master data,
│                          # maintenance, portal_templates (website.layout), menu
└── wizard/                # ticket_reject_wizard (+views)
```

Catatan desain: view tiket dibuat **standalone** (bukan inherit form native) agar tahan
perubahan; logika stage pakai field computed-stored `cite_stage_code` yang dipetakan dari
XML id stage; konteks `cite_bypass_lock` untuk write internal pada tiket terkunci.

**Jawaban review vendor — `unique(code)` di `cite.site` & `cite.category`:** dipertahankan
**global** (bukan `unique(code, company_id)`) **dengan sengaja**, karena site & category =
master data yang dipakai bersama lintas 3 company (`company_id` boleh kosong). `unique(code, company_id)`
justru akan jadi bug: PostgreSQL menganggap `company_id` NULL sebagai nilai berbeda sehingga
dua kode sama bisa lolos. Sesuai catatan vendor sendiri ("bisa diabaikan jika berlaku global").
Sudah diberi komentar penjelas di `models/cite_site.py` & `models/cite_category.py`.

## 7. Email routing — cite@aspire.id & Heidi (sudah di kode + yang vendor set di produksi)

**Yang sudah otomatis di modul (tanpa konfigurasi tambahan):**

- Kontak **`partner_cite_mailbox`** (`data/cite_mail_routing.xml`) = "CITE Helpdesk" email `cite@aspire.id`.
  Pada `create()` tiap tiket: email *Ticket Created* di-**CC** ke alamat ini **dan** mailbox dijadikan
  **follower** tiket → seluruh tiket masuk + percakapan publik tembusan ke `cite@aspire.id`.
  Ganti alamat cukup edit kontak ini (Contacts / Studio), tanpa ubah kode.
- **Approval L2** dikirim hanya ke anggota grup *Heidi Approver* (`group_heidi_approver`).
  Email Heidi disetel ke `heidi.lianawaty@aspire.id`. Mailbox `cite@` **tidak** ikut menerima
  email approval (terverifikasi terpisah). Approval L1 → email user di grup *IT Administrator*.

**Yang HARUS vendor pastikan di produksi (stargo.odoo.com / Odoo.sh):**

1. **User asli Heidi** ada di grup *Heidi Approver* dengan email `heidi.lianawaty@aspire.id`
   (di lokal akun `heidi.lisan` sudah diset; di produksi pakai akun Heidi yang sebenarnya).
2. **User IT Administrator** asli ada di grup *IT Administrator* dengan email yang benar
   (lokal masih `itadmin@company.com` — ganti ke alamat IT yang sah, mis. domain @aspire.id).
3. **SMTP keluar** terkonfigurasi (Settings → Technical → Outgoing Mail) agar email benar-benar terkirim;
   tanpa ini email hanya antre di Settings → Technical → Emails.
4. **(Opsional) Incoming `cite@aspire.id`**: agar email yang dikirim ke `cite@aspire.id` otomatis jadi
   tiket CITE, set **Alias Domain** `aspire.id` (Settings → Technical → Email → Alias Domains) lalu
   pastikan MX/routing `aspire.id` mengarah ke server mail Odoo. Alias tim sudah `cite`, sehingga
   alamatnya menjadi `cite@<alias-domain>`. Ini infra di luar modul.

## 7b. Perbaikan coexistence dgn helpdesk Stargo (v17.0.1.1.0 — penting saat 2 helpdesk hidup bersama)

Saat di staging ternyata modul (yang awalnya mengasumsikan dirinya satu-satunya
helpdesk) bocor/bentrok dengan helpdesk Stargo. Sudah diperbaiki:

- **Penanda `cite_team`** (Boolean baru di `helpdesk.team`, True hanya untuk tim CITE).
  Semua action backend (Tickets/Approval/SLA), **dashboard**, dan cron SLA kini
  difilter `('team_id.cite_team','=',True)` → tiket Stargo **tidak lagi nyasar** ke CITE.
- **Route portal ter-namespace**: detail tiket CITE pakai **`/citehelpdesk2/ticket/<id>`**
  (template `portal_cite_ticket` sendiri: detail + panel approval + percakapan + form balas),
  **bukan** `/my/ticket` bawaan yang membuang ke `/my` saat cek akses gagal. Submit & link
  "My Tickets" sudah diarahkan ke route CITE ini.
- **Pemisahan TOTAL dari portal helpdesk bawaan** (class `CiteHelpdeskNativeSeparation`
  di `controllers/portal.py`, override `helpdesk` CustomerPortal):
  (a) tiket CITE **disembunyikan** dari `/my/tickets` & hitungan kartu Tickets bawaan
  (`_prepare_helpdesk_tickets_domain` + filter `team_id.cite_team = False`);
  (b) akses `/my/ticket/<id>` untuk tiket CITE **otomatis dialihkan** ke
  `/citehelpdesk2/ticket/<id>`. Jadi CITE benar-benar terpisah dari helpdesk Stargo.
- **Backfill `<function>`** (`_cite_post_deploy_sync` di `models/helpdesk_team.py`, dipanggil
  `data/cite_post_deploy.xml`): menegaskan `cite_team` + ikon kategori **setiap upgrade**.
  Perlu karena record awal `noupdate=1` → update `<record>` biasa diabaikan Odoo (flag noupdate
  tersimpan di `ir.model.data`). `<function>` jalan via Python, kebal noupdate.
- Versi modul kini **17.0.1.3.0** agar Odoo.sh pasti menjalankan upgrade saat di-push.
  Riwayat: 1.1.0 = pemisahan total dari helpdesk bawaan + routing email cite@aspire.id;
  **1.2.0** = nilai SLA baru (Response 1/2/4/4 jam, Resolution 3/4/5/5 hari) via
  `migrations/17.0.1.2.0/`, filter periode (Day/Week/Month/Year) pada gauge SLA
  Compliance dashboard, perbaikan Send Reply & Need Response (urut terbaru→terlama,
  termasuk tiket pending approval);
  **1.3.0** = kolom **Time in Stage** di tiket, nama stage approval diperbarui
  (Awaiting Admin / Awaiting Final Approval), notifikasi approval **L1 → cite@aspire.id**
  & **L2 → heidi.lianawaty@aspire.id**;
  **1.3.1** = **fix multi-company** — `company_id` tiket di-override jadi field biasa
  (lepas dari company tim, native memaksa `related=team_id.company_id`), jadi pilihan
  company di portal benar-benar tersimpan; constraint partner-company di-relax untuk
  tim CITE (requester boleh lintas company); dashboard Overview kini lintas-company;
  **1.4.0** = **Department wajib di form portal** & dibatasi hanya 15 kode CITE
  (flag `cite_department` di hr.department, global lintas company), auto-compute
  departemen dari employee dihapus (dipilih manual);
  **1.4.1** = **dashboard Overview kini mengikuti company switcher** — centang 1
  company hanya menampilkan tiket company itu (override `allowed_company_ids`
  dihapus; gauge SLA difilter `ticket_id.company_id` agar konsisten).

> Diverifikasi end-to-end via HTTP lokal: submit → `/citehelpdesk2/ticket/<id>` (bukan /my),
> My Tickets memuat tiket & link benar, halaman detail + balas berfungsi, ikon & filter tim benar.

## 8. Pekerjaan tersisa (belum dikerjakan)

- Isi Knowledge Base ≥20 artikel & publish ke website.
- (Opsional) dashboard manajemen tambahan 17 widget via Dashboards/Spreadsheet — dashboard operasional "Overview" sudah built-in.
- Styling landing portal via Website Builder (logo, warna korporat, menu navbar).
- Lepas stage generik bawaan team (New/Solved dll.) bila muncul ganda di kanban.
- Konfigurasi SMTP + alias email masuk bila ingin uji email sungguhan.
- Untuk produksi: deploy ke **Odoo.sh** (Odoo Online tidak mendukung modul Python custom);
  ikuti checklist go-live di `cite_helpdesk/README.md`.
