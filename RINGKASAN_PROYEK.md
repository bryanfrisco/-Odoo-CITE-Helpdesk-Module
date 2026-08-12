# CITE Helpdesk — Laporan Proyek & Dokumentasi Teknis

**Sistem IT Helpdesk & IT Service Management (ITSM) berbasis Odoo 17 Enterprise**
untuk Grup Stargate: PT Stargate Pasific Resources · PT Rajawali Sigi Lestari · PT Stargate Mineral Asia

| | |
|---|---|
| **Nama modul** | `cite_helpdesk` |
| **Versi** | 17.0.1.5.0 |
| **Platform** | Odoo 17.0 Enterprise + PostgreSQL |
| **Status** | Selesai & terverifikasi — 16/16 unit test lulus, fresh install bersih |
| **Portal pengguna** | `/citehelpdesk2` |

> **Cara memakai dokumen ini.**
> **Bagian I** ditulis naratif untuk **sosialisasi (campaign), laporan akademik (skripsi), dan bahan presentasi**.
> **Bagian II** adalah **lampiran teknis** untuk developer/vendor (lingkungan, struktur kode, konfigurasi, riwayat versi).
> Panduan langkah-demi-langkah untuk pengguna akhir ada di dokumen terpisah: `PANDUAN_PENGGUNA_CITE_HELPDESK.md`.

---

## RINGKASAN EKSEKUTIF

Sebelum CITE Helpdesk, kebutuhan IT di Grup Stargate disampaikan secara *ad-hoc* — telepon, pesan pribadi, atau lisan. Akibatnya permintaan tidak tercatat, prioritas ditentukan berdasarkan siapa yang paling mendesak menghubungi, tidak ada janji waktu layanan, dan manajemen tidak punya data untuk mengukur kinerja tim IT.

**CITE Helpdesk** menjadikan seluruh kebutuhan IT tiga perusahaan masuk lewat **satu pintu (Single Point of Contact)**. Setiap permintaan menjadi **tiket bernomor** dengan prioritas yang **dihitung otomatis**, **target waktu (SLA)** yang terukur, **persetujuan berjenjang** untuk permintaan sensitif, serta **jejak audit** yang lengkap.

**Angka kunci:**

| Aspek | Capaian |
|---|---|
| Perusahaan terlayani | **3** (satu sistem, data tetap terpisah) |
| Tahapan siklus tiket | **10 stage** (Open → Closed, termasuk 2 tahap approval) |
| Kombinasi prioritas otomatis | **20** (Impact × Urgency) |
| Kebijakan SLA | **8** (4 Response + 4 Resolution) |
| Peran/role terdefinisi | **6 group** dengan hak berjenjang |
| Template notifikasi email | **16** |
| Unit test otomatis | **16 — seluruhnya lulus** |

---

# BAGIAN I — LAPORAN PROYEK

## 1. Latar Belakang

Grup Stargate menjalankan operasi pertambangan melalui tiga badan usaha (PT Stargate Pasific Resources, PT Rajawali Sigi Lestari, PT Stargate Mineral Asia) dengan lokasi kerja tersebar di **Head Office** dan **Site**. Dukungan teknologi informasi untuk ketiganya ditangani oleh satu tim IT bersama (*shared service*) bernama CITE.

Sebelum sistem ini dibangun, permintaan layanan IT disampaikan melalui saluran tidak resmi: telepon, pesan pribadi, atau permintaan lisan. Kondisi tersebut menimbulkan beberapa persoalan nyata:

1. **Tidak terdokumentasi** — permintaan yang disampaikan lisan mudah terlupakan dan tidak dapat ditelusuri kembali.
2. **Prioritas tidak objektif** — pekerjaan didahulukan berdasarkan kedekatan atau intensitas menghubungi, bukan berdasarkan dampak terhadap operasional.
3. **Tanpa janji waktu layanan** — pengguna tidak tahu kapan permintaannya akan ditangani.
4. **Permintaan sensitif tanpa kendali** — permintaan hak akses, server, dan pengadaan aset tidak melewati mekanisme persetujuan yang tercatat.
5. **Beban kerja tidak merata** — tidak ada mekanisme distribusi tugas antar anggota tim.
6. **Manajemen tanpa data** — tidak tersedia informasi terukur mengenai volume, kecepatan, dan kualitas layanan IT.

Organisasi telah menggunakan **Odoo 17 Enterprise** sebagai sistem informasi utama. Karena itu, membangun helpdesk di atas platform yang sama menjadi pilihan rasional: pengguna tidak perlu aplikasi baru, data terpusat, dan biaya lisensi tambahan dapat ditekan.

## 2. Rumusan Masalah

1. Bagaimana merancang layanan IT terpusat (*Single Point of Contact*) bagi tiga perusahaan dalam satu sistem, tanpa data antarperusahaan saling tercampur?
2. Bagaimana menentukan prioritas penanganan tiket secara **objektif dan konsisten**, tidak bergantung penilaian subjektif?
3. Bagaimana memastikan permintaan sensitif (hak akses, server, aset) melewati **persetujuan berjenjang** yang tercatat dan tidak dapat dilangkahi?
4. Bagaimana menetapkan dan **mengukur kualitas layanan** melalui SLA?
5. Bagaimana sistem baru dapat **hidup berdampingan** dengan modul helpdesk lain yang sudah berjalan di database yang sama?

## 3. Tujuan

**Tujuan umum:** membangun sistem IT Helpdesk & ITSM sebagai pintu tunggal layanan IT Grup Stargate di atas Odoo 17 Enterprise.

**Tujuan khusus:**

1. Menyediakan portal mandiri (*self-service*) agar karyawan dapat melaporkan kendala dan memantau statusnya.
2. Menerapkan **matriks prioritas otomatis** berbasis Impact × Urgency.
3. Menerapkan **persetujuan dua tingkat** dengan pemisahan tugas (*segregation of duty*).
4. Menerapkan **SLA** beserta peringatan dini dan notifikasi pelanggaran.
5. Menyediakan **dashboard** operasional sebagai dasar pengambilan keputusan manajemen.
6. Menjamin **pemisahan data multi-perusahaan** dan koeksistensi dengan helpdesk lain.

## 4. Manfaat

| Pemangku kepentingan | Manfaat |
|---|---|
| **Karyawan** | Satu pintu yang jelas; status permintaan transparan; tidak perlu mengejar petugas IT |
| **Tim IT** | Antrean kerja terstruktur; beban terdistribusi otomatis; prioritas jelas; dokumentasi penyelesaian terjaga |
| **Approver / Manajemen** | Kendali atas permintaan sensitif; jejak audit lengkap; data kinerja terukur (volume, kecepatan, kepatuhan SLA) |
| **Organisasi** | Tata kelola IT lebih baik, memanfaatkan investasi Odoo yang sudah ada tanpa aplikasi tambahan |

## 5. Batasan Masalah

1. Dikembangkan khusus untuk **Odoo 17 Enterprise**; memerlukan modul Helpdesk Enterprise dan tidak dapat berjalan di Odoo Community.
2. Cakupan **tiga perusahaan** dengan dua tipe lokasi (Head Office & Site).
3. **Manajemen aset IT tidak termasuk** — inventaris aset dikelola pada aplikasi terpisah (**SnipeIT**); sistem ini hanya mencatat tiket layanan.
4. Target penerapan adalah **Odoo.sh** atau *on-premise*; Odoo Online (SaaS) tidak mendukung modul Python kustom.
5. Konfigurasi infrastruktur email (SMTP dan *alias domain* untuk email masuk) berada **di luar lingkup modul**.
6. Sistem menangani proses **Incident** dan **Service Request**; proses ITIL lain (Problem, Change, Release Management) belum dicakup.

## 6. Landasan Teori

### 6.1 IT Service Management (ITSM) dan ITIL

ITSM adalah pendekatan pengelolaan layanan TI yang berorientasi pada nilai bagi pengguna. Kerangka **ITIL** membedakan dua jenis permintaan yang keduanya diterapkan dalam sistem ini:

- **Incident** — gangguan atas layanan yang seharusnya berjalan (contoh: printer rusak, jaringan putus). Ditangani melalui *Incident Management* dan memiliki **akar penyebab** (*root cause*).
- **Service Request** — permintaan layanan rutin yang bukan gangguan (contoh: permintaan hak akses, permintaan aset baru). Ditangani melalui *Request Fulfillment* dan **tidak memiliki akar penyebab kerusakan**, namun umumnya memerlukan **persetujuan**.

### 6.2 Matriks Prioritas (Impact × Urgency)

ITIL menetapkan prioritas sebagai fungsi dua dimensi:

- **Impact (Dampak)** — luas pihak yang terpengaruh: seluruh perusahaan, satu lokasi, satu departemen, atau individu.
- **Urgency (Urgensi)** — seberapa cepat penanganan dibutuhkan.

Kombinasi keduanya menghasilkan prioritas **Low / Medium / High / Critical**. Pendekatan ini menghilangkan subjektivitas karena prioritas **dihitung sistem**, bukan dipilih pengguna.

### 6.3 Service Level Agreement (SLA)

SLA adalah kesepakatan target waktu layanan. Sistem ini menerapkan dua jenis target:

- **Response Time** — batas waktu tiket mulai ditangani.
- **Resolution Time** — batas waktu tiket selesai.

Perhitungan menggunakan **jam kerja** (bukan jam kalender) dan **dihentikan sementara** ketika tiket menunggu jawaban pengguna, agar penilaian adil bagi tim IT.

### 6.4 Kontrol Akses Berbasis Peran & Pemisahan Tugas

**RBAC** (*Role-Based Access Control*) memberikan hak berdasarkan peran, bukan per individu. **Segregation of duty** memastikan satu orang tidak memegang dua peran yang berpotensi konflik — dalam sistem ini, pemohon tidak boleh menyetujui permintaannya sendiri.

### 6.5 Arsitektur Multi-Perusahaan pada Odoo

Odoo menerapkan pemisahan data antarperusahaan melalui **record rule**. Setiap pengguna memiliki daftar perusahaan yang boleh diakses, dan data difilter otomatis. Perilaku ini menjadi pertimbangan desain penting karena satu tim IT melayani tiga perusahaan sekaligus.

## 7. Metodologi Pengembangan

Pengembangan menggunakan pendekatan **iteratif-inkremental berbasis blueprint**:

| Tahap | Kegiatan | Keluaran |
|---|---|---|
| **1. Analisis kebutuhan** | Identifikasi masalah, pemangku kepentingan, alur kerja eksisting | Daftar kebutuhan fungsional & non-fungsional |
| **2. Perancangan** | Penyusunan *design blueprint*: model data, alur status, matriks prioritas, matriks approval, RBAC | Dokumen blueprint |
| **3. Implementasi** | Pengembangan modul Odoo secara bertahap (*native-first*) | Modul `cite_helpdesk` |
| **4. Pengujian** | Unit test otomatis, uji instalasi bersih, uji fungsional *end-to-end* | Laporan pengujian |
| **5. UAT & perbaikan** | Uji coba di *staging*, perbaikan berdasarkan temuan nyata | 12 rilis perbaikan (v1.1.0 → v1.5.0) |
| **6. Deployment** | Penerapan ke produksi melalui Odoo.sh | Paket produksi (`.zip`) |

**Prinsip perancangan — *native-first*:** fitur yang sudah tersedia pada Odoo (tiket, SLA, rating, portal, *knowledge base*) **digunakan apa adanya**; kode kustom hanya ditulis untuk kebutuhan yang tidak tersedia secara bawaan. Prinsip ini menekan risiko, mempermudah pemeliharaan, dan menjaga kompatibilitas saat Odoo diperbarui.

## 8. Analisis dan Perancangan Sistem

### 8.1 Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│  PENGGUNA                                                   │
│  Karyawan (Portal Web)   ·   Tim IT & Approver (Backend)     │
└───────────────┬─────────────────────────┬───────────────────┘
                │                         │
┌───────────────▼─────────────┐  ┌────────▼────────────────────┐
│  LAPIS PRESENTASI           │  │  LAPIS PRESENTASI           │
│  Portal QWeb /citehelpdesk2 │  │  Backend views + Dashboard  │
│  (website.layout)           │  │  OWL (Chart.js)             │
└───────────────┬─────────────┘  └────────┬────────────────────┘
                │                         │
┌───────────────▼─────────────────────────▼───────────────────┐
│  LAPIS APLIKASI (Odoo Framework)                            │
│  Controller HTTP · Model ORM · Guard & Constraint           │
│  Priority Engine · Approval Engine · SLA Engine · Cron       │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  LAPIS DATA — PostgreSQL                                    │
│  Record Rules (isolasi multi-company) · ACL per group        │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Rancangan Data Utama

| Entitas | Keterangan |
|---|---|
| `helpdesk.ticket` (diperluas) | Entitas inti: nomor tiket, perusahaan, lokasi, departemen, kategori, impact/urgency, status approval, root cause, catatan resolusi |
| `cite.site` | Lokasi kerja — Head Office & Site (berlaku lintas perusahaan) |
| `cite.category` / `cite.subcategory` | Klasifikasi masalah + penanda wajib-approval + **tim penanggung jawab** |
| `hr.department` (diperluas) | Penanda 15 departemen resmi CITE |
| `helpdesk.team` (diperluas) | Penanda `cite_team` sebagai pemisah dari helpdesk lain |

### 8.3 Alur Status Tiket (10 Stage)

```
                    ┌── (perlu approval) ──┐
                    │                      ▼
                    │        Awaiting Admin Approval (L1)
                    │                      │
  Tiket dibuat ─────┤                      ▼ approve
                    │        Awaiting Final Approval (L2)
                    │                      │
                    │                      ▼ approve
                    └──────► Open ────► Assigned ────► In Progress
                                                    │      ▲
                                          ┌─────────┘      │ balasan
                                          ▼                │ pengguna
                                    Waiting User ──────────┘
                                          │
                                          ▼
                                      Resolved ────► Closed
                                                (otomatis 3 hari)

  Status akhir lain: Cancelled · Rejected (terkunci, tidak dapat diubah)
```

### 8.4 Matriks Prioritas

Prioritas dihitung otomatis dari 20 kombinasi Impact × Urgency:

| Impact ↓ / Urgency → | Lokasi lumpuh | Departemen lumpuh | Beberapa orang | Satu orang | Permintaan rutin |
|---|---|---|---|---|---|
| **Seluruh perusahaan** | Critical | Critical | High | High | Medium |
| **Satu lokasi** | High | High | Medium | Medium | Low |
| **Satu departemen** | High | High | Medium | Medium | Low |
| **Individu** | Medium | Medium | Medium | Medium | Low |

### 8.5 Rancangan SLA

| Priority | Response | Resolution |
|---|---|---|
| Critical | 1 jam | 3 hari kerja |
| High | 2 jam | 4 hari kerja |
| Medium | 4 jam | 5 hari kerja |
| Low | 4 jam | 5 hari kerja |

Berbasis jam kerja; dihentikan sementara pada status *Waiting User*. Peringatan otomatis pada **75%** dan **90%** waktu terpakai, serta notifikasi saat **terlampaui**.

### 8.6 Rancangan Peran (RBAC)

| Group | Peran | Hak utama | Warisan |
|---|---|---|---|
| **IT Support (Agent L1)** | Agen garda depan | Mengelola & mengerjakan tiket; tidak dapat approve/menghapus | helpdesk user |
| **Infrastructure Team** | Spesialis jaringan/server/CCTV | Hak IT Support; penanggung jawab kategori Network/Server/CCTV | IT Support |
| **Application Team** | Spesialis aplikasi/software | Hak IT Support; penanggung jawab kategori Software | IT Support |
| **IT Administrator (Approver L1)** | Persetujuan tingkat 1 + admin master data | Approve/Reject L1; kelola kategori, lokasi, SLA | IT Support |
| **Department Head (Approver L2)** | Persetujuan final | Approve/Reject L2; membaca seluruh tiket lintas perusahaan | helpdesk user |
| **IT Manager** | Pimpinan IT | Dashboard/KPI, penugasan ulang, konfigurasi; penerima notifikasi pelanggaran SLA | IT Administrator |

Hierarki diterapkan melalui pewarisan hak: IT Manager → IT Administrator → IT Support. **Department Head sengaja tidak mewarisi hak IT Support** agar berperan murni sebagai pemberi persetujuan, namun diberi hak baca menyeluruh untuk menilai tiket lintas perusahaan.

### 8.7 Kanal Akses dan Visibilitas Aplikasi

Sistem melayani **dua kanal berbeda** sesuai peran pengguna:

| Aktor | Kanal akses | Aplikasi CITE Helpdesk tampil di menu? |
|---|---|---|
| Karyawan (seluruh staf) | **Portal** `/citehelpdesk2` | **Tidak** |
| IT Support (Agen L1) | Backend | Ya |
| Infrastructure Team | Backend | Ya |
| Application Team | Backend | Ya |
| IT Administrator (Approver L1) | Backend | Ya |
| Department Head (Approver L2) | Backend | Ya |
| IT Manager | Backend | Ya |

**Prinsip pemisahan kanal.** Karyawan cukup memakai portal untuk melaporkan dan memantau tiket miliknya sendiri; mereka tidak memerlukan — dan tidak seharusnya memiliki — akses ke data tiket seluruh organisasi melalui backend. Karena itu menu aplikasi dibatasi hanya kepada pengguna yang terdaftar pada **grup CITE**.

**Catatan implementasi yang penting.** Pembatasan menu **tidak boleh** menggunakan grup Helpdesk bawaan Odoo (`helpdesk.group_helpdesk_user`). Pada database yang juga menjalankan modul helpdesk lain, grup tersebut umumnya telah diberikan kepada hampir seluruh karyawan, sehingga aplikasi CITE Helpdesk ikut tampil bagi semua orang meskipun mereka tidak berkepentingan. Pembatasan karena itu diarahkan ke grup internal modul (`group_it_support` dan `group_heidi_approver`); keempat grup lain — Infrastructure, Application, IT Administrator, dan IT Manager — tercakup otomatis melalui pewarisan hak. Pembatasan ini bersifat *visibilitas menu*; keamanan data tetap ditegakkan berlapis melalui ACL dan *record rule*.

## 9. Implementasi

### 9.1 Fitur Utama

| No | Fitur | Penjelasan |
|---|---|---|
| 1 | **Penomoran tiket** | Format `IT-YYYY-XXXXX`, berurutan, direset tiap tahun, unik lintas perusahaan |
| 2 | **Prioritas otomatis** | 20 kombinasi Impact × Urgency; dihitung server, tidak dapat diubah manual |
| 3 | **Persetujuan dua tingkat** | L1 (IT Administrator) → L2 (Department Head); dilengkapi *guard* anti-pelangkahan, pemisahan tugas, dan alasan penolakan wajib |
| 4 | **SLA & peringatan dini** | 8 kebijakan; peringatan 75%/90%; notifikasi pelanggaran ke IT Manager |
| 5 | **Portal mandiri** | `/citehelpdesk2` — buat tiket, pantau status, balas percakapan, unggah lampiran (maks. 5 berkas @25 MB) |
| 6 | **Dashboard Overview** | 6 kartu KPI, 3 tabel operasional, grafik tren 14 hari, donat status, *gauge* kepatuhan SLA, penyegaran otomatis 60 detik |
| 7 | **Distribusi beban otomatis** | Tiket disetujui langsung ditugaskan ke agen dengan beban paling ringan (dihitung lintas perusahaan) |
| 8 | **Notifikasi tim penanggung jawab** | Tiap kategori memiliki tim penanggung jawab (mis. CCTV → Infrastructure Team) yang diberi tahu saat tiket masuk/disetujui |
| 9 | **Otomasi siklus hidup** | Balasan pengguna mengaktifkan kembali tiket; tiket Resolved ditutup otomatis setelah 3 hari |
| 10 | **Isolasi multi-perusahaan** | Tiket hanya tampil pada perusahaan yang berhak; tetap dapat dilayani satu tim bersama |
| 11 | **Koeksistensi** | Terpisah total dari modul helpdesk lain pada database yang sama |
| 12 | **Jejak audit** | Seluruh perubahan status & keputusan approval tercatat permanen; tiket final terkunci; penghapusan dibatasi |

### 9.2 Keputusan Teknis Penting

1. **Pemisahan dari helpdesk lain** — penanda `cite_team` pada tim dan `cite_ticket` pada tiket, disimpan langsung di tabel tiket. Penyimpanan penanda (bukan penelusuran relasi) diperlukan karena penelusuran memicu *record rule* multi-perusahaan yang dapat menyembunyikan seluruh tiket ketika perusahaan pemilik tim tidak diaktifkan.
2. **Perusahaan per tiket** — bawaan Odoo mengunci perusahaan tiket mengikuti perusahaan tim. Karena satu tim melayani tiga perusahaan, atribut ini diubah menjadi kolom mandiri agar pilihan pengguna di portal benar-benar tersimpan.
3. **Portal ber-*namespace* sendiri** — rute `/citehelpdesk2/*` dipakai agar tidak berbenturan dengan portal helpdesk bawaan.
4. **Sinkronisasi pasca-*deploy*** — data awal ditandai `noupdate`, sehingga pembaruan nilai memerlukan fungsi sinkronisasi yang dijalankan setiap kali modul diperbarui.

## 10. Pengujian dan Hasil

### 10.1 Metode Pengujian

| Jenis | Cakupan | Hasil |
|---|---|---|
| **Unit test otomatis** | 16 pengujian: matriks prioritas (20 kombinasi), penomoran tiket, alur approval, *guard* anti-pelangkahan, pemisahan tugas, penguncian tiket final | **16/16 lulus** |
| **Uji instalasi bersih** | Instalasi dari nol pada database baru tanpa data contoh (skenario produksi) | **Berhasil, tanpa galat** |
| **Uji pembaruan** | Pembaruan modul pada database lama berisi data | **Berhasil, tanpa galat** |
| **Uji fungsional *end-to-end*** | Pembuatan tiket dari portal → approval L1 → approval L2 → penugasan otomatis | **Sesuai rancangan** |
| **Uji multi-perusahaan** | Berbagai kombinasi perusahaan aktif pada *company switcher* | **Isolasi data sesuai rancangan** |
| **UAT di *staging*** | Pengujian oleh pengguna sesungguhnya | **12 temuan, seluruhnya diperbaiki** (v1.1.0–v1.5.0) |

### 10.2 Hasil terhadap Rumusan Masalah

| Rumusan masalah | Penyelesaian | Bukti |
|---|---|---|
| Layanan terpusat 3 perusahaan tanpa data tercampur | Satu tim bersama + isolasi berbasis *record rule* & penanda tersimpan | Uji multi-perusahaan lolos |
| Prioritas objektif | Matriks Impact × Urgency dihitung server, tidak dapat diubah manual | 20 kombinasi teruji |
| Persetujuan berjenjang tidak dapat dilangkahi | Approval 2 tingkat + *guard* pada operasi tulis + pemisahan tugas | Uji *guard* & pemisahan tugas lolos |
| Kualitas layanan terukur | 8 kebijakan SLA + peringatan dini + *gauge* kepatuhan | Dashboard SLA berjalan |
| Koeksistensi dengan helpdesk lain | Pemisahan penuh data & rute portal | Terverifikasi di *staging* |

### 10.3 Keterbatasan

Pengujian antarmuka berbasis peramban (*browser test*) bawaan Odoo tidak dijalankan pada lingkungan pengembangan lokal karena keterbatasan perkakas; pengujian tersebut dijalankan pada lingkungan integrasi Odoo.sh. Pengujian fungsional sistem dilakukan secara manual dan terdokumentasi.

## 11. Kesimpulan dan Saran

### 11.1 Kesimpulan

1. Sistem IT Helpdesk terpusat bagi tiga perusahaan **berhasil dibangun** di atas Odoo 17 Enterprise dengan pendekatan *native-first*, sehingga kode kustom minimal dan pemeliharaan lebih ringan.
2. Prioritas penanganan **berhasil diobjektifkan** melalui matriks Impact × Urgency yang dihitung sistem.
3. Kendali atas permintaan sensitif **tercapai** melalui persetujuan dua tingkat yang dilengkapi pengaman anti-pelangkahan dan pemisahan tugas.
4. Kualitas layanan **menjadi terukur** melalui penerapan SLA beserta peringatan dini dan dashboard kepatuhan.
5. Sistem **terbukti dapat hidup berdampingan** dengan modul helpdesk lain pada database yang sama.
6. Seluruh pengujian otomatis **lulus (16/16)** dan instalasi bersih terverifikasi, sehingga modul siap diterapkan ke produksi.

### 11.2 Saran Pengembangan Lanjutan

1. **Knowledge Base** — menyusun minimal 20 artikel solusi mandiri untuk menurunkan volume tiket berulang.
2. **Integrasi SnipeIT** — menghubungkan tiket dengan data aset agar riwayat gangguan per perangkat dapat ditelusuri.
3. **Laporan manajemen lanjutan** — analisis tren jangka panjang dan biaya layanan.
4. **Perluasan proses ITIL** — Problem Management untuk menangani gangguan berulang.
5. **Kanal alternatif** — integrasi WhatsApp/Telegram sebagai jalur pelaporan tambahan.
6. **Survei kepuasan lanjutan** — pemanfaatan data rating untuk evaluasi berkala.

---

# BAGIAN II — LAMPIRAN TEKNIS

> Bagian ini ditujukan untuk developer dan vendor pelaksana *deployment*. Tidak diperlukan untuk keperluan presentasi atau sosialisasi.

## A. Lingkungan Pengembangan Lokal (Windows 11)

| Komponen | Detail |
|---|---|
| Odoo | 17.0 **Enterprise** di `C:\Program Files\Odoo 17.0e.20260609`; service `odoo-server-17.0`, port **8069** (gevent 8072) |
| odoo.conf | `...\server\odoo.conf` — `addons_path` memuat `d:\CITE Helpdesk Module`; master password: `admin` |
| PostgreSQL | v18, service `postgresql-x64-18`, port 5432; role **openpg / openpgpwd** |
| Database | `cite_helpdesk` (modul + data contoh) |
| CLI terpisah | `"...\python\python.exe" "...\server\odoo-bin" -d cite_helpdesk --http-port=8070 --gevent-port=8073 --data-dir=%LOCALAPPDATA%\OdooCite` |
| Upgrade modul | tambah `-u cite_helpdesk --stop-after-init`, lalu restart service (butuh UAC) |
| Jalankan test | tambah `--test-tags /cite_helpdesk --stop-after-init` |

**Keanehan PG18 + Windows:** Odoo tidak dapat membuat database sendiri (galat *"collations with different collate and ctype"*). Buat manual lebih dulu:

```sql
CREATE DATABASE namadb OWNER openpg ENCODING 'UTF8'
  LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0;
```

## B. Akun Pengujian (lokal — bukan kredensial produksi)

| Peran | Login | Password |
|---|---|---|
| Odoo Administrator | `admin` | `admin` |
| Approver L1 (IT Administrator) | `itadmin` | `itadmin123` |
| Approver L2 (Department Head) | `heidi.lisan` | `heidi123` |
| Karyawan portal (requester) | `karyawan` | `karyawan123` |

**Alur uji:** login `karyawan` → buat tiket kategori **Access** di `/citehelpdesk2/new` → login `itadmin` → *Approval Waiting List* → **Approve (Admin)** → login `heidi.lisan` → **Approve (Dept Head)** → tiket otomatis *Assigned*.

## C. Struktur Modul

```
cite_helpdesk/
├── __manifest__.py        # depends: helpdesk, hr, portal, website,
│                          #          website_helpdesk, website_helpdesk_knowledge
├── controllers/portal.py  # /citehelpdesk2, /new, /submit, /my-tickets, /ticket/<id>
├── data/                  # sequence, team, 10 stages, 3 ticket types, 8 SLA,
│                          # master data, 2 activity types, 16 mail templates, 3 cron
├── demo/demo_data.xml     # Company B/C, sites, user Department Head
├── migrations/17.0.1.2.0/ # post-migrate: penerapan nilai SLA baru
├── models/                # cite_site, cite_category(+sub), hr_department,
│                          # helpdesk_team, helpdesk_stage, helpdesk_ticket (inti)
├── security/              # security.xml (groups+rules), ir.model.access.csv
├── static/src/            # portal JS/SCSS + dashboard OWL
├── tests/                 # common, priority_matrix, sequence, approval_flow
├── views/                 # ticket views (standalone), master data,
│                          # portal_templates (website.layout), menu
└── wizard/                # ticket_reject_wizard (+views)
```

**Catatan desain:** view tiket dibuat **standalone** (bukan mewarisi form bawaan) agar tahan perubahan versi; logika status memakai field tersimpan `cite_stage_code` yang dipetakan dari XML id stage; konteks `cite_bypass_lock` dipakai untuk penulisan internal pada tiket terkunci.

**Jawaban review vendor — `unique(code)` pada `cite.site` & `cite.category`:** dipertahankan **global** (bukan `unique(code, company_id)`) secara sengaja, karena keduanya adalah master data lintas perusahaan (`company_id` boleh kosong). Penggunaan `unique(code, company_id)` justru menimbulkan celah: PostgreSQL memperlakukan `NULL` sebagai nilai berbeda sehingga dua kode identik dapat lolos. Penjelasan telah dicantumkan sebagai komentar pada kedua model.

## D. Email Routing & Konfigurasi Produksi

**Sudah otomatis di modul:**

- Kontak **`partner_cite_mailbox`** (`data/cite_mail_routing.xml`) = "CITE Helpdesk" `cite@aspire.id`. Saat tiket dibuat, email *Ticket Created* di-**CC** ke alamat ini dan mailbox dijadikan **follower** → seluruh tiket & percakapan publik tembusan ke sana. Mengganti alamat cukup lewat kontak, tanpa ubah kode.
- **Approval L1** → email ke mailbox pusat `cite@aspire.id`; **Approval L2** → anggota grup *Department Head (Approver L2)*.
- **Notifikasi tim penanggung jawab** → anggota grup pada `responsible_group_id` kategori.

**Yang harus dipastikan vendor di produksi:**

1. **User Department Head** berada di grup *Department Head (Approver L2)* dengan email `heidi.lianawaty@aspire.id`.
2. **User IT Administrator** berada di grup *IT Administrator* dengan email resmi (lokal masih `itadmin@company.com`).
3. **Anggota grup tim spesialis** (Infrastructure/Application/IT Support) terisi — bila kosong, notifikasi tim tidak terkirim.
4. **SMTP keluar** dikonfigurasi (Settings → Technical → Outgoing Mail); tanpa ini email hanya mengantre.
5. **(Opsional) Email masuk** — agar email ke `cite@aspire.id` otomatis menjadi tiket: set **Alias Domain** `aspire.id` dan arahkan MX ke server mail Odoo (infrastruktur, di luar modul).
6. **Approver wajib mengaktifkan ketiga perusahaan** pada *company switcher* agar dapat membuka/menyetujui tiket dari perusahaan mana pun (perilaku standar multi-company Odoo, bukan galat).
7. **Keanggotaan grup CITE menentukan siapa yang melihat aplikasi.** Menu root dibatasi ke `cite_helpdesk.group_it_support` + `cite_helpdesk.group_heidi_approver`. Pastikan seluruh anggota tim IT sudah terdaftar pada grup CITE **sebelum** perubahan diterapkan — bila belum, mereka ikut kehilangan menu. Karyawan biasa tidak terpengaruh karena melapor lewat portal.

> **Catatan bila mengubah visibilitas menu lewat antarmuka Odoo** (Settings → Technical → User Interface → Menu Items): nilai `groups` akan **ditulis ulang dari berkas XML modul setiap kali modul diperbarui**. Agar perubahan bersifat permanen, ubah pada `views/menu.xml`, bukan hanya melalui antarmuka.

## E. Catatan Bug & Solusi Selama Pengembangan

1. Service Odoo gagal terkoneksi database → role `openpg` dibuat ulang (via `pg_hba` trust sementara; cadangan `pg_hba.conf.bak-cite` tersimpan di data dir PG).
2. Tree view tiket: `stage_id` memiliki domain merujuk `team_id` → wajib menambahkan `<field name="team_id" column_invisible="1"/>`.
3. `create()` bawaan helpdesk **selalu** menimpa `vals['ticket_ref']` → nomor CITE harus ditulis **setelah** `super().create()`.
4. PowerShell pipe ke `odoo-bin shell` merusak *encoding* → gunakan `cmd /c "type file | odoo-bin shell -d <db> --no-http"`.

## F. Riwayat Versi

| Versi | Perubahan utama |
|---|---|
| **1.1.0** | Pemisahan total dari helpdesk bawaan; routing email `cite@aspire.id` |
| **1.2.0** | Nilai SLA baru (Response 1/2/4/4 jam, Resolution 3/4/5/5 hari) via migration; filter periode gauge SLA; perbaikan Send Reply & urutan Need Response |
| **1.3.0** | Kolom **Time in Stage**; penamaan ulang stage approval; notifikasi approval L1/L2 |
| **1.3.1** | **Fix multi-company** — `company_id` tiket menjadi kolom mandiri; constraint partner-company dilonggarkan untuk tim CITE |
| **1.4.0** | **Department wajib** di portal & dibatasi 15 kode CITE (flag `cite_department`) |
| **1.4.1** | Dashboard mengikuti *company switcher* |
| **1.4.2** | **Fix tiket hilang** saat perusahaan tim tidak diaktifkan — penanda tersimpan `cite_ticket` menggantikan penelusuran relasi |
| **1.4.3** | **Fix Access Error** pada gauge SLA (pembacaan kebijakan SLA sebagai `sudo`, hasil tetap difilter per perusahaan) |
| **1.4.4** | **Fix keadilan distribusi beban** lintas perusahaan pada penugasan otomatis |
| **1.5.0** | **(a)** IT Asset registry dihapus total (aset dikelola SnipeIT); **(b)** penamaan ulang "Heidi Approver" → **"Department Head (Approver L2)"** pada seluruh teks pengguna; **(c)** **notifikasi tim penanggung jawab** per kategori (`responsible_group_id`) dengan nilai bawaan cerdas |

> Diverifikasi *end-to-end*: pengiriman tiket dari portal, halaman detail & balasan berfungsi, penyaringan tim benar, instalasi bersih tanpa galat, 16/16 unit test lulus.

## G. Paket Deliverable

| Berkas | Isi | Untuk |
|---|---|---|
| `cite_helpdesk/` | Kode sumber modul (siap salin ke repo Odoo.sh) | Vendor / repositori |
| `cite_helpdesk_production.zip` | Modul siap pasang — **tanpa** folder `demo/`, tanpa `__pycache__`, manifest dengan `"demo": []` | Instalasi produksi |
| `RINGKASAN_PROYEK.md` | Dokumen ini — laporan proyek + lampiran teknis | Akademik / manajemen / vendor |
| `PANDUAN_PENGGUNA_CITE_HELPDESK.md` | Panduan pengguna akhir + materi sosialisasi | Karyawan / sosialisasi |
| `CITE_Helpdesk_Pitchdeck.html` | Pitch deck presentasi (mandiri, dapat diekspor PDF) | Presentasi |
| `cite_helpdesk/README.md` | Dokumentasi teknis modul + checklist *go-live* | Developer / vendor |

Paket produksi diverifikasi bersih: instalasi dari nol tanpa data contoh berhasil tanpa galat, tidak memuat berkas *cache* maupun data demo.

## H. Pekerjaan Tersisa

- Mengisi Knowledge Base ≥20 artikel dan mempublikasikannya.
- Penataan tampilan portal melalui Website Builder (logo, warna korporat, navbar).
- Melepas stage generik bawaan tim bila muncul ganda pada kanban.
- Konfigurasi SMTP + alias email masuk untuk pengujian email sesungguhnya.
- Deployment produksi ke **Odoo.sh**; mengikuti checklist *go-live* pada `cite_helpdesk/README.md`.
