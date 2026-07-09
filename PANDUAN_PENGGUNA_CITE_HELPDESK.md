                # 📘 PANDUAN PENGGUNA — CITE HELPDESK

Sistem layanan IT terpusat untuk seluruh karyawan grup Stargate
(PT Stargate Pasific Resources, PT Rajawali Sigi Lestari, PT Stargate Mineral Asia).
Semua kebutuhan IT — komputer, jaringan, software, akses, printer, CCTV, dll. —
dilayani lewat satu pintu: **CITE Helpdesk**.

> Versi panduan 1.0 • Untuk sosialisasi internal

---

## DAFTAR ISI
1. [Untuk Karyawan — Membuat & Memantau Tiket](#bagian-1--untuk-karyawan)
2. [Untuk Tim IT — Menangani Tiket](#bagian-2--untuk-tim-it-agen)
3. [Untuk Approver — Menyetujui Permintaan](#bagian-3--untuk-approver)
4. [Penjelasan Istilah Penting](#bagian-4--penjelasan-istilah)
5. [Pertanyaan yang Sering Ditanyakan (FAQ)](#bagian-5--faq)

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
- **Level 2 — Heidi Lianawaty Lisan**

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
| **IT Assets** | Daftar aset IT (laptop, printer, server, dll.) |
| **Master Data** | Pengaturan kategori, lokasi, SLA (khusus IT Administrator) |

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

Hanya untuk **IT Administrator** (Level 1) dan **Heidi Lianawaty Lisan** (Level 2).

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

# BAGIAN 4 — PENJELASAN ISTILAH

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

# BAGIAN 5 — FAQ

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

*Dokumen ini dapat dijadikan bahan presentasi/handout sosialisasi CITE Helpdesk.*
