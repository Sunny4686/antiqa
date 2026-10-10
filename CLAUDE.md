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
- Följ varje källas robots.txt och villkor. Läs dem på nytt innan en ny källa eller sökväg används.

- Ingen inloggning. Inget kringgående av CAPTCHA/blockering, ingen proxy- eller IP-rotation.
- Vid 403/429/CAPTCHA: backoff, stoppa källan och larma ägaren.
- Auctionet (öppet JSON-API) högst 1 förfrågan per 5 s. Blocket-takten (1 sökanrop per 2–5 min) gäller
  först om tillstånd ges.
- Spara aldrig säljares namn, telefon eller profil-id. Lokala bildkopior raderas efter 7 dagar.

## Kommandon

Fylls i när stommen finns (installera, testa, köra lokalt, eval, driftsätta).
