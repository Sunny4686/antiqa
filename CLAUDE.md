# Fyndjakt

Intern tjänst som tar in nya möbelannonser från Blocket (via tillåtna vägar), bedömer dem med bildanalys
mot slutpriser från Auctionet och skickar Telegram-larm om undervärderade skandinaviska designmöbler.
En ägare, internt bruk, budget 500–5000 kr/mån. Princip: lean and mean, få rörliga delar.

## Styrdokument

- `docs/PRD.md`: gällande kravspecifikation. Följ den.
- `reports/Fyndjakt svenska designmöbler.md`: bakgrundsanalys (marknad, juridik, teknik, kostnader).
  Dess PRD-prompt är ersatt av `docs/PRD.md` vad gäller insamling.
- `research_notes/`: källanteckningar bakom rapporten.

## Konventioner

- Python 3.12, uv, ruff, pytest. FastAPI + Jinja2 + HTMX. SQLite (WAL) via SQLAlchemy 2 + Alembic.
- UI-text på svenska; kod, identifierare och kommentarer på engelska.
- Rena funktioner för regler, värdering, marginal och larmbeslut; testa dem utan nätanrop.
- Parsers testas mot sparade fixtures i `tests/fixtures/`.
- Hemligheter i `.env` (aldrig i repo). Modell-id och trösklar i config.
- Små commits. Fråga ägaren innan nya beroenden, nya tjänster eller nya källor läggs till.

## Skyddsräcken för skrapning (hårda krav)

- **Ingen automatiserad hämtning från blocket.se** (sök, annonssidor, API) utan Blockets skriftliga
  tillstånd. Villkoren och robots.txt förbjuder det (se `docs/recon/RESULTAT.md`). Blocket-data kommer in
  bara via push, delning eller passivt tillägg till `/ingest/*`. Att byta adress (VPS/Pi/proxy) ändrar
  inget och räknas som kringgående.
- Webbläsartillägget (`extension/`) är passivt: det tar en skärmbild av det ägaren själv bläddrar förbi och
  skickar den till Fyndjakt. Det får aldrig scrolla, klicka, öppna sidor eller göra egna anrop till sajterna.
  Skärmbilder raderas när de lästs (senast efter ett dygn).
- Följ varje källas robots.txt och villkor. Läs dem på nytt innan en ny källa eller sökväg används.
- Ingen inloggning. Inget kringgående av CAPTCHA/blockering, ingen proxy- eller IP-rotation.
- Vid 403/429/CAPTCHA: backoff, stoppa källan och larma ägaren.
- Auctionet (öppet JSON-API) högst 1 förfrågan per 5 s. Blocket-takten (1 sökanrop per 2–5 min) gäller
  först om tillstånd ges.
- Spara aldrig säljares namn, telefon eller profil-id. Lokala bildkopior raderas efter 7 dagar.

## Kommandon

- Installera: `uv sync` (kopiera `.env.example` till `.env`)
- Testa: `uv run pytest` · Lint: `uv run ruff check src tests && uv run ruff format --check src tests`
- Köra lokalt (webb + jobb): `uv run fyndjakt serve` → http://127.0.0.1:8000/inkorg
- Migrera: `uv run fyndjakt migrate` (körs även vid start). Ny migration: ändra `models.py`, autogenerera via
  `alembic.command.revision(fyndjakt.migrate.alembic_config(), autogenerate=True, ...)`.
- Första fyllningen av Auctionet-comps: `uv run fyndjakt auctionet-backfill [--designer "Bruno Mathsson"]`
  (köar jobb, körs av `serve`, ~1,5 h för de 10 underkategorierna).
- Eval: `uv run python -m eval.run --dry-run` / `--limit 40` (kräver `ANTHROPIC_API_KEY`). Kör efter varje promptändring.
- Drift (VPS, Docker Compose, Cloudflare Tunnel/Access, Telegram-webhook): se `docs/DRIFT.md`.
- Webbläsartillägget: Chrome → `chrome://extensions` → Utvecklarläge → "Läs in okomprimerat" → `extension/`.
  Det postar till `POST /ingest/screenshot` (jobb `screen_capture`, `capture.py`).
- Import från filer (ägarens egna exporter): lägg mappar/CSV/JSON/zip i `data/inbox/` (läses varje minut,
  flyttas till `_klart`/`_fel`), ladda upp på `/importera`, eller `uv run fyndjakt import <sökväg>`. Format: `importer.py`.
- Annonser in: `POST /ingest/listing` med `Authorization: Bearer $INGEST_TOKEN` (se `IngestListing` i `services.py`).

## Struktur

`src/fyndjakt/`: `pipeline/` (rena funktioner, steg 1, 3, 5–9), `ai/` (steg 2, 4, budget), `sources/auctionet.py`,
`notify/telegram.py`, `assess.py` (kör stegen för en annons), `jobs.py` (SQLite-jobbkö + worker),
`web/` (FastAPI + Jinja2/HTMX), `migrations/` (Alembic), `watchlist.py` (automatisk bevakningslista),
`ai/enrich.py` (titeltolkning i Batches, modellanteckningar), `images.py` (nedskalning, radering efter 7 dagar),
`eval/` (precision/recall/kostnad), `data/kommuner.csv` (tätorter + kommuner, Wikidata CC0).
