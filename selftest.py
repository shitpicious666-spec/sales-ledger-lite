#!/usr/bin/env python3
"""selftest.py — bukti bahwa versi lite benar-benar bekerja. Jalankan: python3 selftest.py"""
import sys

import ledger_lite


def main() -> int:
    db = ledger_lite.connect(":memory:")

    first = ledger_lite.record(db, "gumroad", "GR-1", "Kit", "29.00", "USD")
    again = ledger_lite.record(db, "gumroad", "GR-1", "Kit", "29.00", "USD")
    assert first is True and again is False, "webhook ulang harus ditolak"

    ledger_lite.record(db, "lynk", "LY-7", "Kas Harian", "30000", "IDR")
    s = ledger_lite.summary(db)
    assert s["total_sales"] == 2, s

    # mata uang tidak boleh dijumlah jadi satu angka
    currencies = {row["currency"] for row in s["by_product"]}
    assert currencies == {"USD", "IDR"}, currencies

    # pembulatan uang tidak lewat float
    row = db.execute("SELECT amount FROM sales WHERE external_id='GR-1'").fetchone()
    assert row[0] == "29.00", row

    # rollup bulanan memakai occurred_at, bukan jam sekarang
    ledger_lite.record(db, "gumroad", "GR-2", "Kit", "10.00", "USD",
                       occurred_at="2026-11-05T10:00:00+00:00")
    nov = ledger_lite.month(db, 2026, 11)
    assert nov["total_sales"] == 1, nov

    print(f"selftest lulus: {s['total_sales']} penjualan tercatat, "
          f"duplikat ditolak, mata uang terpisah, rollup bulanan benar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
