#!/usr/bin/env python3
"""sales-ledger-lite: catat penjualan dari webhook apa pun ke satu SQLite, tanpa duplikat.

Versi ringkas (MIT). Untuk versi lengkap — profil fee per platform, rollup bulanan, digest
harian, dan 16 test — lihat tautan di README.

Contoh:
    import ledger_lite
    db = ledger_lite.connect("sales.db")
    ledger_lite.record(db, "gumroad", "GR-1", "My Kit", 29.00, "USD")
    print(ledger_lite.summary(db))
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal

SCHEMA = """
CREATE TABLE IF NOT EXISTS sales (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    platform     TEXT NOT NULL,
    external_id  TEXT NOT NULL,
    product      TEXT NOT NULL,
    amount       TEXT NOT NULL,
    currency     TEXT NOT NULL,
    occurred_at  TEXT NOT NULL,
    received_at  TEXT NOT NULL,
    raw          TEXT,
    UNIQUE(platform, external_id)
);
"""


def connect(path: str = "sales.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=10)
    conn.executescript(SCHEMA)
    return conn


def record(conn, platform: str, external_id: str, product: str, amount, currency: str = "USD",
           occurred_at: str | None = None, raw: dict | None = None) -> bool:
    """Simpan satu penjualan. False bila (platform, external_id) sudah ada — webhook diulang."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    amount = str(Decimal(str(amount)).quantize(Decimal("0.01")))
    try:
        conn.execute(
            "INSERT INTO sales (platform, external_id, product, amount, currency,"
            " occurred_at, received_at, raw) VALUES (?,?,?,?,?,?,?,?)",
            (platform, str(external_id), product, amount, currency.upper(),
             occurred_at or now, now, json.dumps(raw or {})[:2000]),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def summary(conn) -> dict:
    rows = conn.execute(
        "SELECT platform, product, currency, COUNT(*), SUM(CAST(amount AS REAL))"
        " FROM sales GROUP BY platform, product, currency ORDER BY 5 DESC"
    ).fetchall()
    return {
        "total_sales": sum(r[3] for r in rows),
        "by_product": [
            {"platform": p, "product": pr, "currency": c, "count": n, "gross": round(g or 0, 2)}
            for p, pr, c, n, g in rows
        ],
    }


def month(conn, year: int, month: int) -> dict:
    prefix = f"{year:04d}-{month:02d}"
    rows = conn.execute(
        "SELECT platform, product, currency, COUNT(*), SUM(CAST(amount AS REAL))"
        " FROM sales WHERE substr(occurred_at,1,7) = ?"
        " GROUP BY platform, product, currency", (prefix,)
    ).fetchall()
    return {
        "period": prefix,
        "total_sales": sum(r[3] for r in rows),
        "by_product": [
            {"platform": p, "product": pr, "currency": c, "count": n, "gross": round(g or 0, 2)}
            for p, pr, c, n, g in rows
        ],
    }
