# Fyndjakt

Intern tjänst som helautomatiskt skrapar nya möbelannonser på Blocket, bedömer dem med bildanalys
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

- Ingen inloggning. Inget kringgående av CAPTCHA/blockering, ingen proxy- eller IP-rotation.
- Vid 403/429/CAPTCHA: backoff, stoppa källan och larma ägaren.
- Blocket högst 1 sökanrop per 2–5 min (jitter); Auctionet högst 1 förfrågan per 5 s.
- Spara aldrig säljares namn, telefon eller profil-id. Lokala bildkopior raderas efter 7 dagar.

## Kommandon

Fylls i när stommen finns (installera, testa, köra lokalt, eval, driftsätta).
