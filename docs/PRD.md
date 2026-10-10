# PRD: Fyndjakt (helautomatisk version)

> **Ändring 2026-10-10 (efter M0):** Blockets villkor och robots.txt förbjuder uttryckligen automatiserad
> åtkomst utan skriftligt tillstånd. Ägaren har beslutat att inte skrapa otillåtet. Blocket-pollern, och
> reservvägen med en poller hemma, är **pausade tills skriftligt tillstånd finns**. Fram till dess kommer
> Blocket-annonser in via bevakningspush, delning eller passivt webbläsartillägg till `/ingest/listing`.
> Auctionet (öppet JSON-API, tillåtande villkor) gäller oförändrat. Se `docs/recon/RESULTAT.md`.

Ersätter PRD-prompten i `reports/Fyndjakt svenska designmöbler.md` på en punkt: insamlingen sker
**helautomatiskt genom skrapning** av Blocket och Auctionet i stället för via bevakningar, push och
manuell delning. Beslutet är ägarens, taget med kännedom om att det sannolikt bryter mot sajternas
användarvillkor (avtalsrisk, risk för IP-blockering). Allt annat i rapporten gäller.

## Mål

En intern tjänst för 1–3 användare som, utan manuellt arbete:

1. Hittar nya möbelannonser på Blocket inom ett par minuter efter publicering.
2. Bedömer med bildanalys om möbeln är en värdefull skandinavisk designmodell (eller en kopia).
3. Värderar den mot automatiskt insamlade slutpriser från Auctionet och egna affärer.
4. Räknar nettomarginal och avstånd i ren kod.
5. Skickar Telegram-larm när marginal, ROI och geografi klarar ägarens trösklar.

Effektmått: realiserad nettovinst i kr per månad. Styrsignaler: precision på larm, fynd per vecka,
latens publicering → larm, AI-kostnad per månad.

## Icke-mål (MVP)

Andra kategorier än möbler, flera användarroller, mobilapp, egen ML-träning, automatiska köp eller
kontakt med säljare.

## Skyddsräcken (hårda krav, gäller trots skrapbeslutet)

- **Ingen inloggning** mot Blocket eller Auctionet. Bara öppet tillgängliga sidor och endpoints.
- **Inget kringgående:** vid CAPTCHA, 403/429 eller annan blockering stoppar källan med exponentiell
  backoff och larmar ägaren. Ingen proxy- eller IP-rotation, inga headless-trick för att dölja bot.
- **Måttlig takt:** Blocket-pollern högst 1 sökanrop per 2–5 minuter (slumpad jitter) plus hämtning
  av enskilda annonser för nya träffar; högst 1 samtidig förfrågan per källa. Auctionet-crawlern
  högst 1 förfrågan per 5 s, inkrementell och nattlig.
- **Ingen persondata:** spara aldrig säljarens namn, telefon eller profil-id.
- **Bilder:** spara bild-URL:er. Lokala kopior för analys raderas efter 7 dagar. Auctionet-bilder
  används bara för analys/embeddings och sparas inte varaktigt. Visa aldrig andras bilder publikt.
- **Allt bakom privat inloggning** (Cloudflare Access).

## Stack

- Python 3.12, uv, ruff, pytest.
- FastAPI + Jinja2 + HTMX (ingen SPA, inget npm-bygge).
- SQLite (WAL) via SQLAlchemy 2 + Alembic; schemat ska tåla byte till Postgres + pgvector.
- httpx för hämtning. Playwright endast om en källa kräver det, och då efter att ägaren tillfrågats.
- Anthropic Python SDK. Modell-id i config: `MODEL_FAST` (Haiku-klass) och `MODEL_STRONG`
  (Sonnet-klass). Verifiera aktuella modell-id och priser i Anthropics dokumentation.
- Telegram Bot API för larm.
- Docker Compose: `app` (web + schemalagda jobb i samma process, jobbkö i SQLite-tabell) och
  `cloudflared`. Ingen Redis, ingen Celery.
- Drift: liten EU-VPS. Om Blocket blockerar VPS:ens datacenter-IP körs pollern i stället på en
  maskin hemma (t.ex. Raspberry Pi) som postar till VPS:en via `/ingest/listing` med token.

## Fas 0: rekognosering (före all kod för skrapor)

Blocket bytte plattform 18 nov 2025 (Finn/Vend-teknik). Gamla skrapor och URL-mönster gäller inte.

1. Läs och spara (med datum) `robots.txt` och användarvillkoren för Blocket och Auctionet i
   `docs/recon/`. Sammanfatta vad de säger om automatiserad åtkomst och visa ägaren.
2. Blocket: hitta hur möbelkategorin listas sorterad på nyast: finns en JSON-endpoint bakom
   sökningen (inspektera nätverksanrop i sidan), inbäddad JSON i HTML, eller bara HTML? Dokumentera
   URL, parametrar, sidstorlek, fält (id, titel, pris, ort, publiceringstid, bild-URL:er) och
   hur man hämtar en enskild annons. Spara 3–5 anonymiserade svar som fixtures i `tests/fixtures/`.
3. Mät volym: hur många nya möbelannonser per timme/dygn.
4. Auctionet: hur listas avslutade objekt per kategori/formgivare, och vilka fält finns (titel,
   formgivare, tillverkare, klubbslag, datum, skick, bild-URL:er). Spara fixtures.
5. Skriv `docs/recon/RESULTAT.md` och stäm av med ägaren innan skraporna byggs.

## Datamodell (minimum)

- `listings`: id, source, external_id (unik), url, title, price_sek, description, municipality,
  lat, lon, published_at, first_seen_at, image_urls, status.
- `models` (bevakningslistan, byggs automatiskt): id, designer, manufacturer, model_name, period,
  category, aliases, identifying_features, replica_traps, marks, active, auto_generated (bool).
- `comps`: id, model_id (nullable), designer, source ('auctionet'|'tradera'|'own_sale'|…),
  external_id, title, sold_at, hammer_sek, condition_text, condition ('utmärkt'|'gott'|'slitet'|
  'renoveringsobjekt'), url, image_urls.
- `assessments`: listing_id, stage, model_candidate_id, match ('yes'|'uncertain'|'no'), evidence,
  contradictions, replica_signals, label_ocr, condition_guess, needs_underside_photo,
  value_p25/median/p75, n_comps, value_level ('model'|'designer_category'|'none'), transport_sek,
  net_margin_sek, roi, distance_km, confidence ('låg'|'medel'|'hög'), llm_model, tokens_in,
  tokens_out, cost_usd, created_at.
- `feedback`: listing_id, label ('köpt'|'ej_intressant'|'fel_modell'|'replika'|'bra_men_såld').
- `deals` (affärsliggare): köp, kostnader, försäljning, avgifter, nettoresultat, timmar.
  Sålda affärer blir automatiskt `comps` med source='own_sale'.
- `settings`: home_lat, home_lon, max_distance_km, allowed_regions, min_net_margin_sek (1500),
  min_roi (0.5), net_ratio (0.78), fixed_fees_sek (500), transport_base_sek (300),
  transport_sek_per_km (3.0), max_listing_price_sek (30000), daily_ai_budget_usd (2.0), quiet_hours.
- `source_health`: källa, senaste lyckade körning, antal fel i rad, senaste fel.
- `ai_calls`: tid, modell, tokens, kostnad.

## Insamling

**Blocket-poller** (var 2–5:e min med jitter): hämta första sidan av möbelkategorin sorterad på
nyast, fortsätt bläddra tills ett redan sett `external_id` påträffas (max N sidor). Nya annonser
sparas och köas för bedömning. Annonser över `max_listing_price_sek` hoppas över. Prisändringar på
kända annonser ger ombedömning.

**Auctionet-crawler** (nattligen, inkrementellt): avslutade objekt i möbelkategorierna, från
senaste körningen och bakåt till en konfigurerbar gräns (standard 3 år vid första körningen).
Spara fakta enligt `comps`. Parsning av formgivare/tillverkare/modell ur titeln görs först med
regler; det som inte går tolkas med `MODEL_FAST` i batch (Batches API för halva priset).

**Automatisk bevakningslista:** ett veckojobb grupperar comps per (formgivare, modell), räknar
antal och medianpris, och föreslår/uppdaterar `models` för grupper med ≥ 3 försäljningar och
median ≥ 3000 kr. `MODEL_STRONG` skriver identifying_features, marks och replica_traps per modell
(med kända licensutgåvor och kopior). Ägaren kan redigera men behöver inte.

**Hälsokontroll:** 3 misslyckade körningar i rad eller 0 nya annonser på 2 timmar dagtid →
Telegram "Källan trasig: <källa>".

## Bedömningspipeline (en ren, testbar funktion per steg)

1. **Förfilter (kod):** pris, kategori, textregler. Plussignaler: formgivare/tillverkare/alias
   från `models`, "stämplad", "märkt", "dödsbo", "60-tal", "teak", "palisander" m.fl.
   Minussignaler som sätter replica-flagga: "replika", "kopia", "i stil med", "à la",
   "inspirerad av", "-stil". Inga annonser kastas enbart på text: de mest undervärderade saknar
   ofta formgivarnamn.
2. **Bildscreening (`MODEL_FAST`, alla annonser som passerat pris):** första bilden nedskalad till
   max 512 px + titel. Frågan: "kan detta vara en skandinavisk designmöbel av samlarvärde, och i så
   fall vilken formgivare/tillverkare/modell?" Strikt JSON via tool use, prompt caching på den
   fasta instruktionen. Grovt mål: under 0,001 USD per annons.
3. **Kandidatval (kod):** max 8 kandidatmodeller från `models` utifrån steg 1–2.
4. **Verifiering (`MODEL_FAST`):** upp till 4 bilder (max 784 px), annonstext, kandidater med
   identifying_features och replica_traps. Välj kandidat-id eller NONE, lista bevis och motbevis
   FÖRE beslut, läs av etiketter/stämplar, ange om foto av undersidan behövs.
5. **Värdering (kod):** comps för modellen, skicksmultiplikatorer (1.0 / 0.85 / 0.7 / 0.55,
   konfigurerbara). n ≥ 5: P25/median/P75 på modellnivå. n = 1–4: krympning i log-pris mot
   formgivare × kategori. n = 0: value_level='none'.
6. **Geografi (kod):** kommun → centroid (CSV med Sveriges 290 kommuner från öppen data),
   haversine från hemmet, transport_sek = base + per_km × 2 × avstånd.
7. **Marginal (kod):** net = P25 × net_ratio − fixed_fees − transport − pris; roi = net / pris.
8. **Eskalering:** om match ∈ {yes, uncertain} och net ≥ 2 × min_net_margin, kör steg 4 med
   `MODEL_STRONG`. Oenighet → confidence='låg'.
9. **Larmbeslut:** FYND om net ≥ min_net_margin OCH roi ≥ min_roi OCH (avstånd ≤ max ELLER län
   tillåtet) OCH confidence ≥ medel. KOLLA SJÄLV (tyst) vid bevakad formgivare med låg confidence
   eller value_level='none' och stor möjlig uppsida. Quiet hours gäller inte FYND.
10. **Budgetvakt:** varje AI-anrop loggas; när dagsbudgeten nås körs bara steg 1 och ägaren
    meddelas.

Budgetmål totalt (drift + AI): under 1 500 kr/mån vid uppmätt volym. Justera steg 2 (t.ex. bara
annonser som passerar textsignaler eller ett pris-/kategorifilter) om volymen gör det dyrare.

## Telegram

Foto (bästa bilden) + titel, pris, värde "P25–P75 (median), n=X", nettomarginal och ROI, avstånd
och ort, confidence, kandidatmodell, 1–2 bevis och 1 motbevis, ev. "Be om foto av undersidan".
Knappar: [Öppna annons] [Köpt] [Ej intressant] [Fel modell] [Replika] [Bra men såld].
Knapptryck → `feedback` och meddelandet märks som hanterat.

## Webb-UI (svenska, bakom Cloudflare Access)

`/inkorg`, `/annons/{id}`, `/bevakningslista` (inkl. CSV-import/export), `/comps`,
`/installningar`, `/affarer`, `/statistik` (larm/vecka, precision, latens, AI-kostnad, vinst/mån,
källhälsa), `/health` (öppen, ingen data). `/telegram/webhook` och `/ingest/*` undantas från Access
och skyddas med hemliga tokens.

## Utvärdering

- `tests/`: enhetstester för alla rena funktioner och parser-tester mot fixtures. Inga nätanrop.
- `eval/`: `uv run python -m eval.run` kör pipelinen mot en märkt mängd (startas automatiskt från
  Auctionet-comps med kända modeller som positiva och slumpade Blocket-annonser som negativa,
  kompletteras med feedback från Telegram) och rapporterar precision, recall, falska positiva per
  typ, kostnad och latens. Varje promptändring körs mot eval.

## Leveransordning

- **M0:** fas 0-rekognosering, `docs/recon/RESULTAT.md`, avstämning med ägaren.
- **M1:** repo-stomme, schema, Blocket-poller, pipeline steg 1–9, Telegram-larm, inkorg,
  inställningar, budgetvakt, hälsokontroll. Klart när en ny Blocket-annons ger larm eller loggat
  "inget larm" inom 5 min från publicering och alla tester är gröna.
- **M2:** Auctionet-crawler, automatisk bevakningslista, värdering mot riktiga comps, eval.
- **M3:** Docker Compose + cloudflared + driftsättning på VPS, nattlig backup, affärsliggare,
  statistik.
- **M4 (om M3 lönar sig):** embeddings (SigLIP 2 + pgvector) för bildlikhet mot comps, Tradera-API.

## Kill-kriterier

Vecka 4: precision på FYND < 15 % eller 0 handlingsbara larm på 2 veckor → pausa och se över.
Vecka 8: < 1 lönsam affär → stoppa eller pivotera.
