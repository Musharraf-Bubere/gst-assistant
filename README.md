---
title: GST Assistant
emoji: 🧾
colorFrom: green
colorTo: blue
sdk: docker
app_port: 8501
pinned: false
---

# GST Assistant

Ask about the GST on a product in everyday words ("paan leaves", "gud", "chai patti") and get an answer from the official CBIC rate and exemption notifications for goods, with the source entry shown.

> Not tax advice. This is an information tool built on public notifications. It is not affiliated with CBIC.

**Live demo:** _add the link after deployment_

## What it covers

- Goods only: Notification 9/2025-Central Tax (Rate) and 10/2025-Central Tax (Rate), both dated 17 September 2025 and effective 22 September 2025. 1,367 entries: 1,195 taxable and 172 exempt.
- Every answer cites the notification entry it came from, and the page shows the source.

## How it works

```text
question
  -> guard rules (block prompt-injection attempts, empty or very long input)
  -> query rewrite: Gemini adds the notification's wording for everyday Indian words, plus a small glossary
  -> map check: clearly unrelated questions stop here
  -> hybrid search: keyword (BM25 with stemming) + vector (BAAI/bge-small-en-v1.5), combined by
     Reciprocal Rank Fusion, top 8 entries
  -> Gemini answers only from those entries and must cite their ids
  -> output checks: cited ids must be retrieved entries, every percentage must be on a cited entry
  -> answer, sources, thumbs up/down; every request is logged to SQLite
```

The notifications are parsed from the PDFs by my own row parser, which checks its output against known row counts (516, 640, 13, 15, 3, 2 and 6 rows in the seven schedules of notification 9/2025, and 172 in notification 10/2025).

## Evaluation

Questions are kept in separate sets. Sets I tuned on are marked **development**. **Frozen** sets were written before the fix they test and were run once.

| Set | Questions | Result | Note |
|---|---|---|---|
| Practice | 22 | 22/22 | development |
| Hard | 16 | 16/16 | development |
| Everyday words (`hard_own`) | 8 | 8/8 | development; first score before any fix was 1/8 |
| Frozen set 1 (`fresh`) | 10 | glossary only 0/10, with LLM rewrite 10/10 | |
| Frozen set 2 (`fresh2`) | 10 | 8/10 first run | two failures traced and fixed; now development |
| Frozen set 3 (`fresh3`) | 10 | 10/10 | run once on the final retrieval version |
| Retrieval stability (rewrite repeated 5 times per question) | 50 runs | 44/50 at 5 entries, 50/50 at 8 | |

An answer passes only if the status is right, the cited entry is the expected one, and the stated value (exempt or the rate) is right.

What this does **not** show: the sets are small, written by the developer, food-heavy, and mostly single Hindi words. A perfect score on them is not a claim of 100% accuracy.

## Known limitations

- Goods only. Services notifications (15/2025 and 16/2025 amend older notifications) are not loaded.
- The GST rate is derived as twice the CGST rate in notification 9/2025. The IGST notification is not yet used as a cross-check.
- Corrigenda issued after these notifications are not applied.
- The output checks cannot detect a real but wrong entry. The tests catch some of these, not all.
- It depends on an LLM API: about 2 seconds per question, rate limits, and answers can vary slightly between runs.
- Logs are stored in the container and are lost when it restarts.

## Tech stack

Python 3.13 and uv, PyMuPDF, rank-bm25 with Snowball stemming, fastembed, Google Gemini (behind a swappable interface), FastAPI, Streamlit, SQLite, Docker.

## Run it

```bash
uv sync
cp .env.example .env     # then fill in GEMINI_API_KEY and GEMINI_MODEL (no quotes)
uv run streamlit run app.py
```

Docker:

```bash
docker build -t gst-assistant .
docker run --rm -p 127.0.0.1:8501:8501 --env-file .env gst-assistant
```

Evaluation:

```bash
uv run python -m scripts.eval_answers eval/hard.json
uv run python -m scripts.retrieval_summary
uv run python -m scripts.stability eval/fresh.json 5 8
```

API: `uv run uvicorn gst_assistant.api:app`

## Repository map

- `gst_assistant/core`: reusable parts (LLM interface, keyword, vector and hybrid search, logbook, rate limiter)
- `gst_assistant/domains/gst`: row parser, glossary, guards, query rewrite, answer pipeline
- `scripts`: parsing checks, evaluation, reports
- `eval`: question sets
- `notes`: decision log (`decisions.md`) and scoreboard (`scoreboard.md`)
- `data/raw`: source PDFs. `data/processed/records.json`: parsed entries
