"""Test rumus CIF Limonite 1,20% terhadap angka Excel finance.

Jalankan:  python test_limonite_calc.py      (tanpa Odoo, tanpa pytest)
"""

from limonite_calc import EXCEL_REFERENCE, LimoniteInput, bonus_amount, calculate

TOL = 0.005
results = []


def check(name, actual, expected, tol=TOL):
    ok = abs(actual - expected) <= tol
    results.append((ok, name, actual, expected))
    return ok


def main():
    r = calculate(EXCEL_REFERENCE)

    # --- Angka acuan Excel (kolom USD / WMT) ---
    check("Ni 1.20% FOB Price", r["Ni 1.20% FOB Price"], 21.90)
    check("Ni > 1.30% Bonus", r["Ni > 1.30% Bonus"], 2.50)
    check("Ni > 1.20% Bonus (baru)", r["Ni > 1.20% Bonus"], 2.00)
    check("Ni < 1.20% Penalty", r["Ni < 1.20% Penalty"], 0.00)
    check("Ni < 1.00% Penalty", r["Ni < 1.00% Penalty"], 0.00)
    check("Co Bonus", r["Co Bonus"], 0.00)
    check("H2O Penalty", r["H2O Penalty"], -2.41)
    check("Final FOB Price", r["Final FOB Price"], 23.99)
    check("Freight", r["Freight"], 11.10)
    check("Total CIF Price", r["Total CIF Price"], 35.09)
    check("Unit Price (IDR)", r["Unit Price (IDR)"], 35.09 * 17994.00, tol=0.5)

    # --- Rumus bonus = Unit / 0,01 * USD (formula Excel G41) ---
    check("Rumus =E41/0.01*F41", bonus_amount(0.10, 0.20), 2.00)

    # --- Regresi: invoice lama (tanpa tier 1,20%) hasilnya tidak berubah ---
    lama = LimoniteInput(
        ni_fob_qty=1.00,
        ni_fob_price=19.04,
        ni_bonus_13_qty=0.15,
        ni_bonus_13_price=0.50,
        freight_qty=1.00,
        freight_price=8.96,
    )
    r_lama = calculate(lama)
    check("Invoice lama - Final FOB", r_lama["Final FOB Price"], 26.54)
    check("Invoice lama - Total CIF", r_lama["Total CIF Price"], 35.50)

    # --- Baris custom hanya ikut kalau diisi ---
    custom = LimoniteInput(
        ni_fob_qty=1.00,
        ni_fob_price=20.00,
        custom_label="Adjustment",
        custom_qty=0.05,
        custom_price=1.00,
    )
    check("Custom row ikut FOB", calculate(custom)["Final FOB Price"], 25.00)

    passed = sum(1 for ok, *_ in results if ok)
    for ok, name, actual, expected in results:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name:<28} hasil={actual:,.2f}  harusnya={expected:,.2f}")
    print(f"\n{passed}/{len(results)} PASS")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
