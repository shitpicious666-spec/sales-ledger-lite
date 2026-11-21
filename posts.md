# Draf unggahan distribusi (E2) — untuk repo sales-ledger-lite

Aturan yang dipakai di ketiganya:
- **Sebutkan bahwa Anda penulisnya.** Menyembunyikan itu = alasan ban, bukan alasan engagement.
- **Jangan menjual di judul.** Yang ditawarkan adalah kode yang bisa dipakai, bukan produk.
- Tautan ke versi berbayar hanya di README repo, bukan di badan post — kecuali komunitasnya mengizinkan.
- Setiap post menyebut satu masalah nyata, bukan "saya membuat X, tolong lihat".

---

## 1. r/selfhosted (flair [Project])

**Judul:** A sales ledger that refuses to count a webhook twice

**Badan:**

> I sell a couple of small digital products through different platforms and kept hitting the same
> two problems in my own spreadsheet: a webhook that gets retried inflates the day's revenue, and
> float arithmetic turns totals into `0.30000000000000004`.
>
> So the ledger I run now is one SQLite table with two rules baked in:
>
> - `UNIQUE(platform, external_id)` — the duplicate insert is rejected by the database, so the
>   receiving script does not have to remember anything between deliveries. It still answers `200`,
>   because a sender that gets an error will retry forever.
> - amounts are `Decimal`, stored as text — no float anywhere near money.
>
> Monthly rollup uses the sale's own timestamp, and totals are grouped per currency instead of
> summed into one meaningless number.
>
> The lite version (MIT, stdlib only, no dependencies) is here: `<repo URL>`.
> It deliberately ships without an HTTP server so it drops into whatever you already run — Flask,
> FastAPI, a cron job reading an export, a Lambda.
>
> I am the author. Happy to answer questions about the schema, and genuinely interested if you have
> a webhook source I have not handled (the full version adds per-platform fee profiles and a digest
> endpoint; that one is paid, and it is linked from the README, not from this post).

---

## 2. Komunitas n8n / forum otomasi

**Judul:** Recording sales into SQLite without double-counting retries

**Badan:**

> If you use n8n to catch payment webhooks, the awkward part is not parsing the payload — it is the
> retry. Stripe, Gumroad and most local rails will re-deliver a webhook when your workflow times out,
> and a naive Insert node then records the same sale twice.
>
> What works for me: let the database enforce it. One table with `UNIQUE(platform, external_id)`,
> and the workflow does a plain insert. The duplicate fails at the constraint, the workflow still
> returns `200`, and nothing inflates.
>
> The second half is money types. `Decimal` in, text in SQLite, never float — otherwise your monthly
> total drifts by a few rupiah and you spend an evening hunting it.
>
> The lite library (stdlib Python, MIT): `<repo URL>`. It pairs fine with an n8n HTTP Request node —
> the workflow posts to your endpoint, the library records; the README shows the handler shape.
> I wrote it for my own shop, sharing in case it saves someone the same evening.

---

## 3. Show HN

**Judul:** Show HN: A sales ledger that treats a retried webhook as a no-op

**Badan:**

> I sell small digital products on more than one platform. Each platform reports a different "net"
> and a different idea of when the month starts, and every webhook integration I tried counted
> retried deliveries twice — which you notice only on your best day.
>
> The ledger is one SQLite table. Two decisions did the work:
>
> 1. `UNIQUE(platform, external_id)`. Duplicate deliveries are rejected by the database, and the
>    endpoint still returns `200` because erroring makes senders retry harder.
> 2. Money is `Decimal`, stored as text. No float touches an amount.
>
> Plus: monthly rollup keyed on the sale timestamp, and totals grouped per currency rather than
> summed across them (a $29 sale and a Rp30.000 sale are not numbers you can add).
>
> Lite version is MIT, stdlib only, no server included on purpose: `<repo URL>`.
> The paid version adds per-platform fee profiles (Gumroad, Etsy, Lynk, Mayar), a webhook receiver
> and a daily digest — linked in the README.
>
> What I would like feedback on: how you handle refunds and partial refunds in a ledger that is
> append-only. I currently record a negative row with its own id, which keeps history honest but
> makes "revenue this month" a sum instead of a constant.

---

## Urutan dan waktu

| Hari | Kanal | Catatan |
|---|---|---|
| Sab 22 Nov | r/selfhosted | Posting pagi WIB = malam US (audiens terbesar sub ini) |
| Sen 24 Nov | forum n8n | Hari kerja; pertanyaan teknis cepat dijawab di thread |
| Sel 25 Nov | Show HN | 07.00–09.00 PT (22.00–24.00 WIB) — jam terbaik HN |

**Aturan balasan:** jawab pertanyaan teknis, jangan menyanjung, jangan menautkan produk berbayar
kecuali ditanya. Satu balasan per komentar, tanpa template.
