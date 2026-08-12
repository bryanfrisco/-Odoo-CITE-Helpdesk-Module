"""Replika rumus CIF Price Calculation - Ore Type Limonite (basis Ni 1,20%).

Python murni, tanpa Odoo. Dipakai untuk memverifikasi angka Odoo terhadap
Excel finance sebelum/ sesudah update dinaikkan ke production.

Setiap baris pada tab Calculate berbentuk (Unit, USD) -> USD / WMT:

    Ni 1.20% FOB Price   = unit * price
    Ni > 1.30% Bonus     = unit / 0,01 * price      (= unit * 100 * price)
    Ni > 1.20% Bonus     = unit / 0,01 * price      <-- baris BARU
    Ni < 1.20% Penalty   = unit / 0,01 * price
    Ni < 1.00% Penalty   = unit / 0,01 * price
    Co Bonus             = unit * price * 100
    H2O Penalty          = unit * price             (price diisi negatif)
    Custom (opsional)    = unit / 0,01 * price      (hanya jika label diisi)

    Final FOB Price      = jumlah semua baris di atas
    Freight              = unit * price
    Total CIF Price      = Final FOB Price + Freight
    Unit Price (IDR)     = Total CIF Price * BI Rate

Rumus di atas SAMA dengan yang sudah berjalan di Odoo; update ini hanya
mengganti label dan menambah satu tier bonus (Ni > 1.20% Bonus).
"""

from dataclasses import dataclass


def line_amount(unit, price):
    """Baris biasa: Unit x USD."""
    return unit * price


def bonus_amount(unit, price):
    """Baris bonus/penalty berbasis persen: =Unit/0,01*USD."""
    return (unit * 100) * price


@dataclass
class LimoniteInput:
    # Ni 1.20% FOB Price
    ni_fob_qty: float = 0.0
    ni_fob_price: float = 0.0
    # Ni > 1.30% Bonus
    ni_bonus_13_qty: float = 0.0
    ni_bonus_13_price: float = 0.0
    # Ni > 1.20% Bonus (baru)
    ni_bonus_12_qty: float = 0.0
    ni_bonus_12_price: float = 0.0
    # Ni < 1.20% Penalty
    ni_penalty_12_qty: float = 0.0
    ni_penalty_12_price: float = 0.0
    # Ni < 1.00% Penalty
    ni_penalty_10_qty: float = 0.0
    ni_penalty_10_price: float = 0.0
    # Co Bonus
    co_bonus_qty: float = 0.0
    co_bonus_price: float = 0.0
    # H2O Penalty (price diisi negatif)
    h2o_penalty_qty: float = 0.0
    h2o_penalty_price: float = 0.0
    # Baris custom opsional
    custom_label: str = ""
    custom_qty: float = 0.0
    custom_price: float = 0.0
    # Freight
    freight_qty: float = 0.0
    freight_price: float = 0.0
    # Kurs
    bi_rate: float = 0.0


def calculate(inp: LimoniteInput) -> dict:
    ni_fob = line_amount(inp.ni_fob_qty, inp.ni_fob_price)
    ni_bonus_13 = bonus_amount(inp.ni_bonus_13_qty, inp.ni_bonus_13_price)
    ni_bonus_12 = bonus_amount(inp.ni_bonus_12_qty, inp.ni_bonus_12_price)
    ni_penalty_12 = bonus_amount(inp.ni_penalty_12_qty, inp.ni_penalty_12_price)
    ni_penalty_10 = bonus_amount(inp.ni_penalty_10_qty, inp.ni_penalty_10_price)
    co_bonus = inp.co_bonus_qty * inp.co_bonus_price * 100.0
    h2o_penalty = line_amount(inp.h2o_penalty_qty, inp.h2o_penalty_price)
    custom = bonus_amount(inp.custom_qty, inp.custom_price)

    fob = (
        ni_fob
        + ni_bonus_13
        + ni_bonus_12
        + ni_penalty_12
        + ni_penalty_10
        + co_bonus
        + h2o_penalty
        + custom
    )
    freight = line_amount(inp.freight_qty, inp.freight_price)
    cif = fob + freight

    return {
        "Ni 1.20% FOB Price": ni_fob,
        "Ni > 1.30% Bonus": ni_bonus_13,
        "Ni > 1.20% Bonus": ni_bonus_12,
        "Ni < 1.20% Penalty": ni_penalty_12,
        "Ni < 1.00% Penalty": ni_penalty_10,
        "Co Bonus": co_bonus,
        "H2O Penalty": h2o_penalty,
        inp.custom_label or "Custom": custom,
        "Final FOB Price": fob,
        "Freight": freight,
        "Total CIF Price": cif,
        "Unit Price (IDR)": cif * inp.bi_rate,
    }


# Angka acuan dari Excel finance:
# TB. BUANA MARINE XXXVI / BG. BUANA JAYA 3336, BL 04-Jul-26
# Ni 1,35% - Co 0,12% - MgO 4,05% - SiO2 15,67% - H2O 41,42%
# Draft Survey Weight 11.505,25 WMT - BI Rate 17.994,00
EXCEL_REFERENCE = LimoniteInput(
    ni_fob_qty=1.00,
    ni_fob_price=21.90,
    ni_bonus_13_qty=0.05,
    ni_bonus_13_price=0.50,
    ni_bonus_12_qty=0.10,
    ni_bonus_12_price=0.20,
    ni_penalty_12_qty=0.00,
    ni_penalty_12_price=0.20,
    ni_penalty_10_qty=0.00,
    ni_penalty_10_price=0.20,
    co_bonus_qty=0.00,
    co_bonus_price=1.00,
    h2o_penalty_qty=1.00,
    h2o_penalty_price=-2.41,
    freight_qty=1.00,
    freight_price=11.10,
    bi_rate=17994.00,
)


if __name__ == "__main__":
    for label, value in calculate(EXCEL_REFERENCE).items():
        print(f"{label:<22} {value:>15,.2f}")
