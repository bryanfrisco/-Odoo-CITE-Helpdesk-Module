# 📘 PANDUAN PENGGUNA — CITE HELPDESK

Sistem layanan IT terpusat untuk seluruh karyawan grup Stargate
(PT Stargate Pasific Resources, PT Rajawali Sigi Lestari, PT Stargate Mineral Asia).
Semua kebutuhan IT — komputer, jaringan, software, akses, printer, CCTV, dll. —
dilayani lewat satu pintu: **CITE Helpdesk**.

> Versi panduan 2.0 (modul v17.0.1.5.0) • Untuk sosialisasi internal, materi presentasi & handout

---

## DAFTAR ISI
0. [Kenapa CITE Helpdesk? (untuk sosialisasi)](#bagian-0--kenapa-cite-helpdesk)
1. [Untuk Karyawan — Membuat & Memantau Tiket](#bagian-1--untuk-karyawan)
2. [Untuk Tim IT — Menangani Tiket](#bagian-2--untuk-tim-it-agen)
3. [Untuk Approver — Menyetujui Permintaan](#bagian-3--untuk-approver)
4. [Untuk Tim Spesialis — Infrastructure & Application](#bagian-4--untuk-tim-spesialis)
5. [Untuk IT Manager — Memantau & Mengendalikan](#bagian-5--untuk-it-manager)
6. [Penjelasan Istilah Penting](#bagian-6--penjelasan-istilah)
7. [Pertanyaan yang Sering Ditanyakan (FAQ)](#bagian-7--faq)
8. [Kartu Ringkas — 1 Halaman](#bagian-8--kartu-ringkas)

---

# BAGIAN 0 — KENAPA CITE HELPDESK?

## 0.1 Masalahnya dulu

Selama ini kendala IT dilaporkan lewat **telepon, japri, atau lisan**. Akibatnya:

- ❌ Laporan **mudah terlupakan** — tidak ada catatan
- ❌ Yang dikerjakan duluan adalah **yang paling sering menagih**, bukan yang paling penting
- ❌ Pelapor **tidak tahu kapan** akan ditangani
- ❌ Permintaan sensitif (akses, server, aset) **tanpa persetujuan tercatat**
- ❌ Manajemen **tidak punya data** kinerja layanan IT

## 0.2 Sesudah ada CITE Helpdesk

| Dulu | Sekarang |
|---|---|
| Telepon/japri, tidak tercatat | **Satu pintu**, semua jadi tiket bernomor `IT-2026-00123` |
| Prioritas berdasarkan siapa yang paling mendesak | **Prioritas dihitung otomatis** dari dampak × urgensi |
| Tidak tahu kapan ditangani | **Ada target waktu (SLA)** yang jelas per prioritas |
| Permintaan akses tanpa kontrol | **Persetujuan berjenjang** 2 tingkat, tercatat permanen |
| Tidak ada laporan | **Dashboard real-time** untuk manajemen |

## 0.3 Poin sosialisasi (untuk pembawa materi)

Lima kalimat kunci yang bisa dipakai saat presentasi:

1. **"Satu pintu untuk semua kebutuhan IT."** Tidak perlu bingung menghubungi siapa — cukup buat tiket.
2. **"Tiket Anda tidak akan hilang."** Setiap laporan punya nomor dan bisa dipantau sendiri kapan saja.
3. **"Prioritas ditentukan sistem, bukan perasaan."** Semakin luas dampaknya, semakin cepat ditangani — adil untuk semua.
4. **"Ada janji waktu."** Tiket Critical direspon ≤1 jam; setiap prioritas punya target yang terukur.
5. **"Permintaan sensitif tetap terkendali."** Akses dan aset melewati persetujuan berjenjang yang tercatat.

## 0.4 Angka yang bisa ditampilkan di slide

| Aspek | Angka |
|---|---|
| Perusahaan terlayani | **3** (SPR · RSL · SMA) |
| Departemen terdaftar | **15** |
| Kategori layanan | **8** |
| Tahapan siklus tiket | **10 stage** |
| Kombinasi prioritas otomatis | **20** |
| Kebijakan SLA | **8** |
| Respon tercepat (Critical) | **1 jam** |

## 0.5 Siapa saja penggunanya? (peta aktor & hak akses)

Sistem ini punya **7 jenis pengguna**. Cari peran Anda, lalu baca bagian yang sesuai:

| Aktor | Yang dikerjakan | Aksesnya lewat | Lihat app **CITE Helpdesk** di menu? | Baca bagian |
|---|---|---|---|---|
| **Karyawan** (semua staf) | Melapor & memantau tiket sendiri | Portal `/citehelpdesk2` | ❌ Tidak | [Bagian 1](#bagian-1--untuk-karyawan) |
| **IT Support** (Agen L1) | Mengerjakan & menyelesaikan tiket | Backend | ✅ Ya | [Bagian 2](#bagian-2--untuk-tim-it-agen) |
| **Infrastructure Team** | Tiket Network · Server · CCTV | Backend | ✅ Ya | [Bagian 4](#bagian-4--untuk-tim-spesialis) |
| **Application Team** | Tiket Software / Odoo | Backend | ✅ Ya | [Bagian 4](#bagian-4--untuk-tim-spesialis) |
| **IT Administrator** (Approver L1) | Persetujuan tingkat 1 + kelola Master Data | Backend | ✅ Ya | [Bagian 3](#bagian-3--untuk-approver) |
| **Department Head** (Approver L2) | Persetujuan final | Backend | ✅ Ya | [Bagian 3](#bagian-3--untuk-approver) |
| **IT Manager** | Memantau KPI, penugasan ulang, konfigurasi | Backend | ✅ Ya | [Bagian 5](#bagian-5--untuk-it-manager) |

> 🔒 **Kenapa karyawan biasa tidak melihat aplikasi CITE Helpdesk di menu?**
> Itu **disengaja**. Karyawan cukup memakai **portal** untuk melapor dan memantau
> tiket — mereka tidak perlu (dan tidak boleh) membuka data tiket seluruh
> perusahaan di backend. Aplikasi CITE Helpdesk hanya tampil bagi pengguna yang
> terdaftar di **grup CITE** (IT Support ke atas + Department Head).
> Jadi: **tidak melihat menu ≠ tidak bisa melapor.** Semua karyawan tetap dapat
> membuat tiket lewat `/citehelpdesk2`.

**Hierarki hak akses** — makin ke kanan makin luas, dan otomatis mewarisi yang di kirinya:

```
IT Support  →  IT Administrator  →  IT Manager
    ↑                                    
    └── Infrastructure Team & Application Team (spesialisasi, hak = IT Support)

Department Head (Approver L2) — jalur terpisah: murni memberi persetujuan,
tidak ikut mengerjakan tiket, tetapi dapat membaca seluruh tiket lintas perusahaan.
```

---

# BAGIAN 1 — UNTUK KARYAWAN

Sebagai karyawan, Anda menggunakan **Portal** untuk melaporkan kendala IT atau
meminta layanan. Tidak perlu telepon atau japri — cukup buat tiket, dan tim IT
akan menanganinya sesuai prioritas.

## 1.1 Cara Masuk ke Portal

1. Buka browser, ketik alamat portal:
   **`https://stargo.odoo.com/citehelpdesk2`**
   *(saat masih uji coba lokal: `http://localhost:8069/citehelpdesk2`)*
2. Login dengan akun kantor Anda (sama dengan akun Odoo).
3. Anda akan melihat halaman utama: tombol **+ Create Ticket**, **📋 My Tickets**, dan
   kartu **Popular Help Categories** (klik kartu kategori untuk langsung mengisi
   kategori di formulir).

## 1.2 Cara Membuat Tiket Baru

1. Klik **+ Create Ticket**.
2. Isi formulir:

| Kolom | Penjelasan |
|---|---|
| **Subject** | Judul singkat masalah Anda. Contoh: *"Printer lantai 2 tidak bisa mencetak"* |
| **Jenis Tiket** | Boleh dibiarkan *otomatis* — sistem menentukan sendiri |
| **Company** | Pilihan otomatis mengikuti akun Anda — hanya menampilkan perusahaan yang Anda miliki aksesnya |
| **Department** *(wajib)* | Pilih departemen Anda — hanya 15 kode: CITE, ENGI, MPMA, MEMD, HCGS, CFAT, CPMD, CSUS, MIOP, EXPL, QLAB, LEGL, CDRE, GOVREL, SMDE |
| **Lokasi** | Pilih **Head Office** atau **Site** |
| **Category** | Pilih jenis kendala: Software, Hardware, Network, Server, Printer, CCTV, Access, atau Asset Request |
| **Siapa yang terdampak?** | Hanya saya / satu departemen / satu lokasi / seluruh perusahaan |
| **Seberapa mendesak?** | Dari "hanya saya terganggu" sampai "lokasi lumpuh total" |
| **Description** | Jelaskan detail masalah: apa yang terjadi, kapan, dan apa yang sudah dicoba |
| **Lampiran** | Foto/screenshot/dokumen pendukung (maksimal **5 file**, masing-masing maks 25 MB) |

3. Klik **Submit Ticket**.
4. Anda akan mendapat **Nomor Tiket** (contoh: `IT-2026-00123`) dan email konfirmasi.

> 💡 **Tips:** Pilihan "Siapa yang terdampak?" dan "Seberapa mendesak?" dipakai
> sistem untuk **menghitung prioritas otomatis**. Jawablah dengan jujur supaya
> tiket Anda ditangani sesuai tingkat kepentingannya.

## 1.3 Memantau Tiket Anda

- Klik **📋 My Tickets** (atau buka `/citehelpdesk2/my-tickets`) untuk melihat semua
  tiket CITE Helpdesk Anda. *(Halaman ini khusus CITE — terpisah dari helpdesk lain.)*
  Daftar menampilkan Nomor, Subjek, Tanggal, Status, Approval, dan Priority.
- Klik **nomor tiket** untuk membuka **halaman detail tiket** yang berisi:
  - **Detail** — Category, Lokasi, Company, Requester, tanggal, dan deskripsi.
  - **Status** terkini (Open, In Progress, Resolved, dll.) di pojok kanan atas.
  - **Approval Status** (jika permintaan Anda butuh persetujuan) — 2 level.
  - **Conversation** — riwayat percakapan & lampiran dengan tim IT.
  - **Reply** — kolom balasan di bawah: ketik pesan, lampirkan file bila perlu,
    lalu klik **Send Reply** untuk berkomunikasi dengan tim IT.

## 1.4 Jika Tiket Butuh Persetujuan

Sebagian permintaan (misalnya **Access**, **Server**, **Asset Request**) harus
disetujui dulu sebelum dikerjakan. Anda akan melihat panel **Status Approval**
dengan 2 tingkat:
- **Level 1 — IT Administrator**
- **Level 2 — Department Head**

Anda tidak perlu melakukan apa-apa — cukup menunggu. Status berubah otomatis dan
Anda mendapat email di setiap tahap (disetujui / ditolak beserta alasannya).

## 1.5 Setelah Tiket Selesai

- Saat tim IT menyelesaikan tiket, statusnya menjadi **Resolved** dan Anda
  mendapat email.
- Anda dipersilakan memberi **rating/penilaian** atas layanan.
- Jika masalah belum tuntas, **balas komentar** di tiket — tiket akan otomatis
  dibuka kembali. Tanpa balasan, tiket akan ditutup otomatis dalam **3 hari**.

---

# BAGIAN 2 — UNTUK TIM IT (AGEN)

Tim IT bekerja di **backend** (bukan portal).

## 2.1 Masuk Backend

1. Buka `https://stargo.odoo.com` → login akun IT Anda.
2. Klik aplikasi **CITE Helpdesk** di menu utama.

## 2.2 Menu Utama

| Menu | Fungsi |
|---|---|
| **Overview** | Dashboard real-time: jumlah tiket open, perlu respon, overdue, tren, SLA, dll. (auto-refresh 60 detik) |
| **Tickets** | Semua tiket — tampilan Kanban/List. Termasuk *Approval Waiting List* & *SLA Breached* |
| **Master Data** | Pengaturan kategori (termasuk *Tim Penanggung Jawab*), lokasi, SLA (khusus IT Administrator) |

## 2.3 Alur Menangani Tiket

```
Open  →  [Start Progress]  →  In Progress  →  [Resolve]  →  Resolved  →  [Close]  →  Closed
                                   ↑↓
                            [Waiting User]  (jika menunggu info dari pelapor)
```

Langkah demi langkah:
1. Buka tiket dari **Tickets** (atau klik kartu di **Overview**).
2. Klik **▶ Start Progress** — menandai Anda mulai mengerjakan (mencatat waktu
   respon pertama untuk SLA).
3. Jika butuh informasi dari pelapor, klik **⏸ Waiting User**. Saat pelapor
   membalas, tiket otomatis kembali ke *In Progress*.
4. Setelah selesai, buka tab **Resolution**, isi **wajib**:
   - **Root Cause** (akar penyebab)
   - **Resolution Notes** (langkah penyelesaian)
5. Klik **✔ Resolve**. Pelapor mendapat email + undangan memberi rating.
6. Tiket akan otomatis **Closed** setelah 3 hari, atau klik **Close** manual.

> ⚠️ **Penting:** Tombol **Resolve/Close tidak bisa diklik** jika *Root Cause*
> dan *Resolution Notes* belum diisi. Ini wajib untuk dokumentasi/audit.

## 2.4 Tools Tambahan
- **Assign to Me** / **Escalate to Manager** — dari menu Action di daftar tiket.
- **Reopen** — membuka kembali tiket yang sudah Resolved/Closed bila perlu.

---

# BAGIAN 3 — UNTUK APPROVER

Hanya untuk **IT Administrator** (Level 1) dan **Department Head** (Level 2).

> ⚠️ **Wajib dicek sebelum mulai kerja:** di pojok kanan atas, pastikan
> **ketiga company** (PT Stargate Pasific Resources, PT Stargate Mineral Asia,
> PT Rajawali Sigi Lestari) **dicentang** di company switcher. Tiket yang
> company-nya tidak dicentang **tidak akan terlihat sama sekali** — ini
> perlindungan data multi-company bawaan Odoo, bukan gangguan sistem.

## 3.1 Kapan Approval Muncul?
Approval otomatis aktif untuk kategori: **Access**, **Server**, **Asset Request**,
serta sub-kategori tertentu (Software Installation, Software License Request,
CCTV Access Request — diset tim IT).

## 3.2 Cara Menyetujui / Menolak
1. Buka **CITE Helpdesk → Tickets → Approval Waiting List**.
2. Buka tiket yang berstatus *Awaiting Admin Approval* (untuk L1) atau
   *Awaiting Final Approval* (untuk L2).
3. Klik tombol di header:
   - **✔ Approve** — meneruskan ke tahap berikutnya (atau langsung Assigned jika L2).
   - **✘ Reject** — wajib mengisi **alasan penolakan**; tiket terkunci sebagai *Rejected*.

## 3.3 Aturan Penting
- Urutan wajib: **Level 1 dulu**, baru **Level 2**.
- Anda **tidak bisa menyetujui tiket yang Anda buat sendiri** (pemisahan
  tugas/segregation of duty).
- Semua keputusan approval tercatat permanen di riwayat tiket (audit trail).

---

# BAGIAN 4 — UNTUK TIM SPESIALIS

Untuk anggota **Infrastructure Team** dan **Application Team**.

## 4.1 Apa bedanya dengan IT Support biasa?

Hak Anda **sama persis** dengan IT Support (Agen L1) — seluruh cara kerja di
[Bagian 2](#bagian-2--untuk-tim-it-agen) berlaku untuk Anda. Bedanya hanya satu:
Anda otomatis menjadi **Tim Penanggung Jawab** untuk kategori tertentu, sehingga
**mendapat notifikasi** saat ada tiket di bidang Anda.

| Tim | Kategori yang jadi tanggung jawab |
|---|---|
| **Infrastructure Team** | Network · Server · CCTV |
| **Application Team** | Software (termasuk Odoo) |
| **IT Support** | Hardware · Printer · Access · Asset Request (dan kategori lain yang belum ditetapkan) |

## 4.2 Kapan Anda dapat notifikasi?

| Jenis tiket | Kapan tim Anda diberi tahu |
|---|---|
| **Tiket biasa** (tanpa approval) | **Begitu tiket masuk** — langsung bisa dikerjakan |
| **Tiket butuh approval** (Access, Server, Asset Request) | **Setelah disetujui penuh** (L1 + L2) — supaya Anda tidak mengerjakan tiket yang ternyata ditolak |

## 4.3 Cara menemukan tiket bidang Anda

1. Buka **CITE Helpdesk → Tickets → All Tickets**.
2. Klik **Group By → Category**, atau gunakan pencarian untuk memfilter kategori
   yang jadi tanggung jawab tim Anda.
3. Kerjakan seperti biasa: **▶ Start Progress → ✔ Resolve** (isi *Root Cause* &
   *Resolution Notes* dulu).

> 💡 Tim penanggung jawab tiap kategori **dapat diubah** oleh IT Administrator di
> *Master Data → Categories → field **Tim Penanggung Jawab***. Jadi bila pembagian
> bidang berubah, tidak perlu mengubah program.

---

# BAGIAN 5 — UNTUK IT MANAGER

Untuk pemegang peran **IT Manager** — memantau kinerja layanan dan mengambil
keputusan, bukan mengerjakan tiket sehari-hari.

## 5.1 Hak Anda

IT Manager otomatis memiliki **seluruh hak IT Administrator dan IT Support**,
ditambah kewenangan:

- Melihat **Dashboard/KPI** seluruh layanan
- **Menugaskan ulang** (reassign) tiket antar agen
- **Membuka kembali** (reopen) tiket yang sudah selesai
- Mengubah **konfigurasi team & SLA**
- Menerima **notifikasi pelanggaran SLA** (SLA Breach)

## 5.2 Yang dipantau setiap hari — menu Overview

| Panel | Gunanya |
|---|---|
| **6 KPI Cards** | Total Open · Need Response · On Progress · **Almost Overdue** · **Overdue** · Solved Today — semuanya bisa diklik untuk melihat daftar tiketnya |
| **Tabel operasional** | Tiket yang belum direspon, hampir melewati SLA, dan sudah terlambat |
| **Tickets by Status** | Sebaran tiket per tahapan — melihat di mana antrean menumpuk |
| **Tickets Trend 14 hari** | Perbandingan tiket masuk vs selesai — apakah tim sanggup mengimbangi beban |
| **Top Ticket Solvers** | Kontribusi tiap agen bulan ini |
| **SLA Compliance** | Persentase kepatuhan Response & Resolution — dapat difilter Day/Week/Month/Year |

Dashboard **menyegarkan diri otomatis tiap 60 detik**.

## 5.3 Rutinitas yang disarankan

**Harian** — cek **Overdue** dan **Almost Overdue** lebih dulu; bila ada tiket
menumpuk pada satu agen, lakukan penugasan ulang.

**Mingguan** — perhatikan **Tickets Trend**: bila garis "Created" terus berada di
atas "Solved", beban melebihi kapasitas tim.

**Bulanan** — evaluasi **SLA Compliance** (pilih periode *Month*) dan **Top
Solvers** sebagai bahan penilaian kinerja serta perencanaan kebutuhan tim.

## 5.4 Tindakan yang sering dipakai

| Tindakan | Cara |
|---|---|
| **Menugaskan ulang** | Buka tiket → ubah field *Assigned to* |
| **Membuka kembali tiket** | Tombol **Reopen** pada tiket Resolved/Closed |
| **Eskalasi** | Menu *Action → Escalate to Manager* pada daftar tiket |
| **Ubah target SLA** | *Master Data → SLA Policies* |
| **Ubah tim penanggung jawab kategori** | *Master Data → Categories* |

> ⚠️ **Multi-company:** pastikan **ketiga perusahaan dicentang** di *company
> switcher* (pojok kanan atas) agar dashboard dan daftar tiket menampilkan data
> seluruh grup, bukan sebagian.

---

# BAGIAN 6 — PENJELASAN ISTILAH

| Istilah | Arti sederhana |
|---|---|
| **Tiket** | Catatan satu laporan/permintaan IT, punya nomor unik `IT-TAHUN-XXXXX` |
| **SLA** | *Service Level Agreement* — janji waktu layanan. Mis. tiket prioritas High harus direspon ≤2 jam |
| **SLA Breached** | SLA terlewati — tiket tidak ditangani tepat waktu (ditandai merah) |
| **Priority** | Tingkat kepentingan (Low/Medium/High/Critical), **dihitung otomatis** dari Impact × Urgency |
| **Impact** | Seberapa luas dampaknya (saya / departemen / lokasi / perusahaan) |
| **Urgency** | Seberapa mendesak (terganggu sedikit s/d lumpuh total) |
| **Approval** | Persetujuan berjenjang sebelum permintaan dikerjakan |
| **Root Cause** | Akar penyebab masalah |
| **Resolution Notes** | Catatan solusi yang dilakukan |

### Target Waktu Respon (SLA)
| Priority | Respon (mulai ditangani) | Penyelesaian |
|---|---|---|
| Critical | 1 jam | 3 hari kerja |
| High | 2 jam | 4 hari kerja |
| Medium | 4 jam | 5 hari kerja |
| Low | 4 jam | 5 hari kerja |

---

# BAGIAN 7 — FAQ

**T: Saya tidak tahu harus pilih Category apa?**
J: Pilih yang paling mendekati. Tim IT akan menyesuaikan bila perlu. Untuk
masalah aplikasi pilih *Software*, perangkat fisik *Hardware*, internet/WiFi
*Network*, minta akun/akses *Access*.

**T: Kenapa tiket saya belum dikerjakan?**
J: Tiket ditangani sesuai prioritas. Jika butuh approval, tiket menunggu
persetujuan dulu. Cek panel *Status Approval* di tiket Anda.

**T: Saya salah buat tiket / sudah tidak perlu.**
J: Beri komentar di tiket atau hubungi IT; tiket bisa dibatalkan (*Cancelled*).

**T: Lampiran saya tidak terlihat?**
J: Lampiran muncul di **kolom komentar** tiket (foto langsung tampil, dokumen
sebagai tautan unduh). Maksimal 5 file per pengiriman.

**T: Kontak darurat?**
J: **cite@aspire.id** (untuk gangguan kritikal yang melumpuhkan pekerjaan).

---

# BAGIAN 8 — KARTU RINGKAS

> Bagian ini dirancang untuk dicetak **1 halaman** dan ditempel di meja kerja,
> atau dijadikan **satu slide penutup** saat sosialisasi.

### 🎫 CARA BUAT TIKET (3 langkah)

| 1️⃣ | Buka **stargo.odoo.com/citehelpdesk2** → login akun kantor |
| :--- | :--- |
| 2️⃣ | Klik **+ Create Ticket** → isi Subject, Department, Lokasi, Category, dampak & urgensi, Description |
| 3️⃣ | Klik **Submit Ticket** → dapat nomor `IT-2026-XXXXX` + email konfirmasi |

### ⏱️ TARGET WAKTU LAYANAN (SLA)

| Priority | Direspon | Diselesaikan |
| :--- | :--- | :--- |
| 🔴 Critical | 1 jam | 3 hari kerja |
| 🟠 High | 2 jam | 4 hari kerja |
| 🟡 Medium | 4 jam | 5 hari kerja |
| ⚪ Low | 4 jam | 5 hari kerja |

*Prioritas dihitung otomatis dari **dampak × urgensi** — jawab jujur agar penanganan tepat.*

### 🔐 BUTUH PERSETUJUAN?

Kategori **Access · Server · Asset Request** (dan beberapa sub-kategori) melewati
**2 tingkat persetujuan**: Level 1 *IT Administrator* → Level 2 *Department Head*.
Anda cukup menunggu — status & email berjalan otomatis.

### ✅ YANG PERLU DIINGAT

- Pantau tiket kapan saja di **📋 My Tickets**
- Balas di kolom **Reply** bila tim IT butuh info tambahan
- Tiket *Resolved* akan **tertutup otomatis dalam 3 hari** bila tidak ada balasan
- Masalah muncul lagi? **Balas tiket** — otomatis dibuka kembali
- Gangguan kritikal: **cite@aspire.id**

---

*Dokumen ini dapat dijadikan bahan presentasi, handout sosialisasi, maupun lampiran
laporan. Dokumen teknis & laporan proyek lengkap tersedia di `RINGKASAN_PROYEK.md`.*
