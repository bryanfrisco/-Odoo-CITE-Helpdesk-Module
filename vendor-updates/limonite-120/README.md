# Update: Label CIF Price Calculation — Ore Type Limonite (basis Ni 1,20%)

Paket update untuk modul **asb_invoice_stargate** (Odoo 17).

- **Baseline patch:** `eb35b79` (`arkana/17.0` — https://github.com/ArkanaDigital/stargate.git)
- **Commit update:** `c5c5ab6` — branch `17.0-feat-limonite-120`
- **Tanggal:** Agustus 2026

> Paket ini **berdiri sendiri**. Tidak ada hubungannya dengan paket
> `vendor-update-saprolite` maupun update "Saprolite HPM Baru" — tidak perlu
> menunggu atau memasang paket-paket itu lebih dulu. Patch sudah diuji apply
> bersih di atas `arkana/17.0` **maupun** di atas branch internal `17.0`
> (yang sudah berisi Saprolite HPM Baru).

---

## 1. Ringkasan Perubahan

Menyesuaikan **Tab Calculate → CIF Price Calculation** untuk Ore Type
**Limonite** dengan format Excel finance (basis Ni **1,20%**).

| Label lama (Odoo) | Label baru (ikut Excel) |
|---|---|
| Ni 1.3% FOB | **Ni 1.20% FOB Price** |
| Ni > 1.3% Bonus | **Ni > 1.30% Bonus** |
| — (tidak ada) | **Ni > 1.20% Bonus** ← baris **baru** |
| Ni < 1.3% Pinalty | **Ni < 1.20% Penalty** |
| Ni < 1% Pinalty | **Ni < 1.00% Penalty** |
| CO Bonus | **Co Bonus** |
| H2O Pinalty | **H2O Penalty** |
| FOB Amount | **Final FOB Price** |
| CIF Amount | **Total CIF Price** |

**Rumusnya tidak diubah sama sekali.** Baris bonus/penalty tetap
`Unit / 0,01 × USD` (persis formula Excel `=E41/0.01*F41`), FOB tetap
penjumlahan semua baris, CIF tetap `Final FOB Price + Freight`.

Yang benar-benar baru cuma satu baris — **Ni > 1.20% Bonus** — dengan tiga
field: `lm_ni_bonus_12_qty`, `lm_ni_bonus_12_price`, `lm_ni_bonus_12`
(computed, store=True), dan baris itu ikut dijumlah ke Final FOB Price.

**Nama field lama sengaja dipertahankan** supaya data invoice Limonite lama
tidak perlu dimigrasi sedikit pun. Jadi perlu diingat saat baca kode:

- `lm_ni_penalty_13*` sekarang berlabel **Ni < 1.20% Penalty**
- `lm_ni_penalty_10*` sekarang berlabel **Ni < 1.00% Penalty**

## 2. File yang Berubah

Hanya **2 file**, keduanya di satu modul. Tidak ada perubahan
`__manifest__.py`, security, data XML, maupun modul lain:

```
asb_invoice_stargate/models/account_move.py
asb_invoice_stargate/views/account_move_views.xml
```

Ore type **Saprolite**, **Saprolite HPM Baru**, invoice **Provisional**, dan
seluruh printout **tidak tersentuh**.

## 3. Cara Deploy

### Opsi A — patch (disarankan)

```bash
cd /path/to/stargate
git checkout -b 17.0-feat-limonite-120        # opsional
git am /path/ke/paket/patch/0001-feat-final-invoice-label-CIF-Price-Calculation-Limon.patch
```

Kalau mau dicek dulu tanpa mengubah apa pun:

```bash
git apply --check --verbose /path/ke/paket/patch/0001-*.patch
```

### Opsi B — copy file manual

Isi folder `files/` adalah versi utuh kedua file di atas, **hasil dari baseline
`arkana/17.0` (eb35b79)**. Sebelum copy, pastikan file di server memang masih
sesuai baseline itu:

```bash
grep -c saprolite_hpm /path/to/addons/asb_invoice_stargate/models/account_move.py
```

- hasil **0** → aman, silakan copy:
  `cp -r files/asb_invoice_stargate/ /path/to/addons/`
- hasil **> 0** → server sudah memuat update Saprolite HPM Baru.
  **Jangan copy** (nanti update itu ketimpa) — pakai Opsi A.

### Upgrade modul (wajib, apa pun opsinya)

```bash
odoo -c /etc/odoo/odoo.conf -d NAMA_DATABASE \
     -u asb_invoice_stargate --stop-after-init
```

lalu restart service Odoo. Upgrade wajib karena ada kolom baru
(`lm_ni_bonus_12`, `lm_ni_bonus_12_qty`, `lm_ni_bonus_12_price`) dan perubahan
label field.

## 4. Dampak ke Data Lama

- **Tidak ada field yang dihapus atau di-rename.** Semua angka invoice
  Limonite lama tetap apa adanya.
- Field baru default `0.0`, jadi `Final FOB Price` dan `Total CIF Price`
  invoice lama **tidak berubah nilainya** setelah upgrade.
- Yang berubah pada invoice lama hanya **teks label** di form, misal baris yang
  dulu tertulis "Ni 1.3% FOB" sekarang tertulis "Ni 1.20% FOB Price".
  Angkanya sama.
- Printout PDF invoice lama **tidak berubah sama sekali** (label di PDF
  hardcoded terpisah, dan belum disentuh di update ini).

## 5. Catatan Penting — Printout Belum Ikut

Printout Limonite (`asb_report_stargate`) **belum** diupdate di paket ini
(menyusul di update terpisah). Konsekuensinya:

1. Label di PDF masih format lama (mis. "Ni 1.30% FOB Price").
2. Baris **Ni > 1.20% Bonus belum dicetak di PDF**. Jadi kalau baris itu diisi,
   `Final FOB Price` di PDF akan lebih besar dari jumlah baris yang tercetak —
   angka totalnya benar, tapi rinciannya tidak lengkap.

**Rekomendasi sementara:** untuk invoice yang perlu dicetak, tunda pemakaian
baris Ni > 1.20% Bonus sampai update printout "Final Invoices Lim 1.20%" naik.
Kalau di form saja (belum print), aman dipakai sekarang.

## 6. Verifikasi

Angka acuan dari Excel finance (TB. BUANA MARINE XXXVI / BG. BUANA JAYA 3336,
BL 04-Jul-26 · Ni 1,35% · Co 0,12% · H2O 41,42% · DSW 11.505,25 WMT ·
BI Rate 17.994,00):

| Label | Unit | USD | USD / WMT |
|---|---|---|---|
| Ni 1.20% FOB Price | 1,00 | 21,90 | **21,90** |
| Ni > 1.30% Bonus | 0,05 | 0,50 | **2,50** |
| Ni > 1.20% Bonus | 0,10 | 0,20 | **2,00** |
| Ni < 1.20% Penalty | 0,00 | 0,20 | **0,00** |
| Ni < 1.00% Penalty | 0,00 | 0,20 | **0,00** |
| Co Bonus | 0,00 | 1,00 | **0,00** |
| H2O Penalty | 1,00 | −2,41 | **−2,41** |
| **Final FOB Price** | | | **23,99** |
| Freight | 1,00 | 11,10 | **11,10** |
| **Total CIF Price** | | | **35,09** |

Regresi invoice lama (INVF-20260209-012001-25852-086): Ni FOB 1,00 × 19,04 +
bonus 0,15 × 0,50 + freight 1,00 × 8,96 → Final FOB **26,54**, Total CIF
**35,50** — sama seperti sebelum update.

### Test logika tanpa Odoo

```bash
cd test-logic
python test_limonite_calc.py   # 15 test, harus 15/15 PASS
python limonite_calc.py        # kalkulator, default = angka acuan Excel di atas
```

## 7. Rollback

```bash
cd /path/to/stargate
git revert c5c5ab6
odoo -c /etc/odoo/odoo.conf -d NAMA_DATABASE \
     -u asb_invoice_stargate --stop-after-init
```

Kolom `lm_ni_bonus_12*` akan hilang saat rollback. Kalau sudah terlanjur ada
invoice yang mengisinya, backup dulu:

```sql
SELECT id, name, lm_ni_bonus_12_qty, lm_ni_bonus_12_price, lm_ni_bonus_12
FROM account_move WHERE lm_ni_bonus_12 != 0;
```

## 8. Isi Paket

```
README.md                     <- dokumen ini
patch/0001-...-Limon.patch    <- patch siap `git am`
files/asb_invoice_stargate/   <- versi utuh 2 file yang berubah (Opsi B)
test-logic/                   <- replika rumus + 15 test, tanpa Odoo
```
