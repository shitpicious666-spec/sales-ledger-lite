# sales-ledger-lite

One SQLite table for sales that arrive from more than one platform — with a retried webhook
counted once, not twice.

```python
import ledger_lite

db = ledger_lite.connect("sales.db")
ledger_lite.record(db, "gumroad", "GR-1", "My Kit", 29.00, "USD")
ledger_lite.record(db, "gumroad", "GR-1", "My Kit", 29.00, "USD")   # retried delivery → False
print(ledger_lite.summary(db))
# {'total_sales': 1, 'by_product': [{'platform': 'gumroad', ..., 'count': 1, 'gross': 29.0}]}
```

No dependencies. Python 3.9+, standard library only.

## Why this exists

If you sell on Gumroad *and* a local checkout *and* a card processor, you have three dashboards
that disagree — and a webhook that fires twice when the first delivery times out. The usual
spreadsheet fix inflates revenue on exactly the days you are busiest.

Two ideas do most of the work here:

1. **`UNIQUE(platform, external_id)`** — a duplicate delivery is rejected by the database, not by
   a script that has to remember what it already saw.
2. **Money as `Decimal`, stored as text** — no float arithmetic, so `0.1 + 0.2` never becomes
   `0.30000000000000004` in a revenue report.

## What you get here (MIT)

| Feature | Lite (this repo) | Full kit |
|---|---|---|
| Ledger + idempotent keys | ✓ | ✓ |
| Dedupe on retried webhooks | ✓ | ✓ |
| Monthly rollup | ✓ | ✓ |
| Net-of-fee calculation per platform | — | ✓ (Gumroad, Etsy, Lynk, Mayar) |
| Webhook receiver (`POST /webhook/<platform>`) | — | ✓ |
| Daily digest endpoint for cron | — | ✓ |
| Number-format parsing (`Rp30.000`, `$29.00`) | — | ✓ |
| Tests | smoke test | 16 unit tests + live run |

The full kit is the same code with the fee profiles, the HTTP receiver and the digest:
`https://picious.gumroad.com/l/kmiwol` — single-buyer commercial licence, no support calls,
no customisation.

## Quickstart

```bash
python3 selftest.py          # proves dedupe and totals on an in-memory database
```

Then point your platform's webhook at a tiny handler of your own — the lite version deliberately
ships without an HTTP server so it can drop into whatever you already run (Flask, FastAPI, a cron
job that reads an export, a Lambda):

```python
from http.server import BaseHTTPRequestHandler

class Hook(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        data = json.loads(body)
        new = ledger_lite.record(db, "gumroad", data["sale_id"], data["product_name"],
                                 data["price"], "USD", raw=data)
        self.send_response(200); self.end_headers()
        self.wfile.write(b'{"ok":true}')
        # 200 even when new is False: a sender that gets an error retries forever.
```

## Licence

MIT. Use it, fork it, ship it inside your own product. Attribution appreciated, not required.
