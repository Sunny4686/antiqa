# M0 – Rekognosering: resultat (2026-10-10)

Underlag i denna mapp: `blocket.se_robots_2026-10-10.txt`, `blocket.se_anvandarvillkor_2026-10-10.{html,txt}`,
`auctionet.com_robots_2026-10-10.txt`, `auctionet.com_terms_of_use_2026-10-10.{html,txt}`.
Totalt gjordes ca 20 förfrågningar under rekognoseringen, med öppen User-Agent och ≥ 5 s mellanrum.

## Sammanfattning

| Källa | robots.txt | Användarvillkor | Teknisk väg | Beslut |
|---|---|---|---|---|
| Blocket | "Crawling blocket.se is prohibited unless you have written permission." Spärrar `/*?sort=` och `/*&sort=` | Uttryckligt förbud: "Användning av automatiserade tjänster såsom robotar, spindlar, indexering eller liknande, samt andra metoder för systematisk användning av innehållet på Webbplatsen är inte tillåtet utan föregående skriftligt tillstånd från Blocket." | Ej kartlagd (medvetet) | **Ingen automatiserad hämtning utan skriftligt tillstånd.** Se *Blocket: väg framåt*. |
| Auctionet | Tillåtande: spärrar bara `/admin/` och `/*/my*` | Gäller registrerade kunder (budgivning, konto). Inget om automatiserad åtkomst, skrapning eller TDM | Öppet JSON-API `/api/v2/items.json` | **Grönt** med PRD:ns takt (≤ 1 förfrågan / 5 s), nattligt, inkrementellt |

Ägarens beslut 2026-10-10: vi skrapar inte otillåtet. PRD:ns helautomatiska Blocket-poller byggs inte
förrän Blocket gett skriftligt tillstånd. Att flytta trafiken till en annan IP-adress (VPS, Raspberry Pi,
proxy) ändrar inget, eftersom förbudet gäller oavsett adress. Att byta adress för att undgå spärr är
dessutom kringgående enligt CLAUDE.md. PRD:ns reservväg "pollern hemma på en Pi" stryks därför.

## Blocket

### Vad villkoren och robots.txt säger
- Villkoren förbjuder robotar och "systematisk användning av innehållet" utan skriftligt tillstånd. Klausulen
  står i alla versioner som finns på villkorssidan, även den nu gällande.
- Blocket och Blockets licensgivare har de immateriella rättigheterna till text och bild. Material "får inte
  användas på annat sätt än inom ramen för normal användning av Tjänsterna".
- robots.txt inleds med samma förbud. Dessutom spärras just sorteringsparametern `sort=`, som PRD:ns
  "nyast först"-poller bygger på.

### Vad som inte undersöktes
Sökningens endpoints, fält och volym kartlades inte, eftersom kartläggning i sig är automatiserad åtkomst
mot ett uttryckligt förbud. Startsidan (en tillåten sökväg) hämtades en gång för att hitta villkorslänken.
Den bäddar in sin data som JSON (`data-react-query-state`, Finn/Vend-plattformen). Det tyder på att en
sök-JSON finns, men den har inte rörts. **Volym per timme/dygn är därför inte uppmätt.**

### Blocket: väg framåt (i prioritetsordning)
1. **Be om skriftligt tillstånd** (utkast: `blocket_tillstand_mejl.md`). Begär låg takt (1 sökanrop per
   2–5 min), internt bruk, ingen vidarepublicering, inga personuppgifter. Fråga också om Vend/Finn har ett
   partner-API. Ett ja ger PRD:ns poller precis som specificerad. Ett nej eller inget svar ger punkterna nedan.
2. **Blockets egna bevakningar plus push på din telefon** (rapportens ursprungliga väg). 20–50 bevakningar
   gör grovfiltreringen. En notislyssnare på Android (`NotificationListenerService`) postar titel, pris och
   länk till `/ingest/listing`. Ingen ny trafik mot Blocket: datan skickas till dig.
3. **Dela-länk / klistra in i Telegram-boten** för annonser du själv öppnat. Bedömningen görs på det du
   skickar in (text och skärmdump/foton du delar), inte genom att servern hämtar sidan.
4. **Webbläsartillägg (passivt)** som läser annonssidor du själv öppnar och skickar fälten till backend.
   Inga egna förfrågningar mot Blocket.
5. **Tradera officiella API** (10 000 anrop per dygn och metod) som kompletterande annonskälla. Det är en
   ny källa och kräver ditt ja.

Öppen gråzon: att servern hämtar *en* enskild annonssida som du explicit delat (för fler bilder). Den är
fortfarande automatiserad hämtning, men den är användarinitierad och inte systematisk. **Ingår inte** tills
du beslutat det eller Blocket svarat.

Konsekvens för PRD:n: Blocket-poller, hälsoregeln "0 nya annonser på 2 h" och latensmålet "inom ett par
minuter" gäller bara om tillstånd ges. Med push-vägen styrs latensen av Blockets push och ska mätas
(rapportens vecka 1-test).

## Auctionet

### Endpoint
`GET https://auctionet.com/api/v2/items.json` (JSON, ingen inloggning).

| Parameter | Betydelse | Verifierat |
|---|---|---|
| `is=ended` | avslutade objekt, nyast avslutade först | ja |
| `category_id` | 16 = Möbler (alla underkategorier) | ja |
| `q` | fritext, t.ex. formgivare (`q=mathsson` gav 8 810 träffar 2013–2026) | ja |
| `per_page` | upp till 100 | ja |
| `page` | **tak: 100 sidor × 100 = 10 000 objekt per fråga**; sida 101 ger 302 | ja |

Underkategorier (från `/api/v2/categories.json`): 18 Fåtöljer & stolar, 24 Byråer, 280 Soffbord, 23 Skåp &
hyllor, 279 Skrivbord, 22 Matsalsmöbler, 281 Matbord, 17 Övrigt, 20 Soffor, 19 Bord.

Enskilt objekt: `/api/v2/items/{id}.json` finns **inte** (404). Listorna innehåller redan alla fält, så det
behövs inte.

### Fält per objekt (urval)
`id`, `title`, `description` (HTML), `condition` (HTML, fritext om skick), `state` (`sold`/`unsold`),
`bids[]` (`amount`, `timestamp`; budgivare anonymiserade som löpnummer, inga personuppgifter),
`estimate`, `upper_estimate`, `reserve_met`, `ends_at` (unix), `published_at`, `category_id`, `house`,
`location`, `url`, `images[]` (`thumb`, `mini`, `w640`, `hd`).

- **Klubbslag** = högsta `bids[].amount` när `state == "sold"`. Fältet `hammered` är `false` även för sålda
  onlineobjekt och ska inte användas.
- **Formgivare/tillverkare/modell** finns inte som egna fält. De tolkas ur `title`, som oftast följer mönstret
  "FORMGIVARE. Typ \"Modell\", Tillverkare, ort år". Det passar regelparsning bra, med `MODEL_FAST` för resten.
- **Språk**: titlar kom ibland på engelska (översatta) och ibland på originalspråket. Ska undersökas i M2
  (troligen styrt av en locale-parameter eller header).

### Volym (uppmätt 2026-10-07 22:58 → 10-10 15:37)
- 800 avslutade möbelobjekt på 64,7 h, alltså **ca 300 per dygn** (~110 000 per år). Totalt 643 061 i arkivet.
- Klubbslag: median **1 000 kr**, 23 % ≥ 3 000 kr.

### Crawlplan (M2)
- **Nattligt inkrementellt**: `is=ended&category_id=16`, bläddra tills senast sedda `id`. Ca 3 förfrågningar
  per natt.
- **Första fyllningen (3 år, ~330 000 objekt)**: 10 000-taket per fråga kräver uppdelning. Kör per
  underkategori (10 × 10 000 = senaste ~1 år) och per formgivare/tillverkare (`q=`) för djupet bakåt. Med
  ≤ 1 förfrågan per 5 s tar ~3 300 förfrågningar ca 4,6 h, utspritt över några nätter.
- Bilder: spara bara URL:er. Hämta tillfälligt för analys, radera därefter (PRD-krav).

### Fixtures
- `tests/fixtures/auctionet_items_ended_furniture.json`: 3 sålda objekt plus `pagination`.
- `tests/fixtures/auctionet_items_query_mathsson.json`: 2 sålda och 1 osålt objekt (formgivarfråga).

Inga personuppgifter: budgivare är löpnummer, och säljaren är auktionshuset.

## Föreslagen mappstruktur

```
fyndjakt/
  config.py            # pydantic-settings: MODEL_FAST, MODEL_STRONG, trösklar, tokens
  db.py, models.py     # SQLAlchemy 2
  sources/
    auctionet.py       # API-klient + parser (ren funktion över JSON)
    blocket_ingest.py  # tar emot push/delning/tillägg – ingen egen hämtning
  pipeline/            # prefilter, screen, candidates, verify, value, geo, margin, decide (rena funktioner)
  ai/                  # Anthropic-anrop, budgetvakt, ai_calls-loggning
  notify/telegram.py
  web/                 # FastAPI-rutter + Jinja2/HTMX-mallar
  jobs/                # SQLite-jobbkö, schemaläggare
migrations/            # Alembic
data/kommuner.csv
tests/ (fixtures/)
eval/
```

## Databasschema

Enligt PRD:ns datamodell, med dessa ändringar:
- `listings.source`: `'blocket_push' | 'blocket_share' | 'blocket_ext' | 'tradera'` (vägen in, inte bara sajten).
- `comps`: lägg till `estimate_sek`, `auction_house`, `category_id`, `state` (spara även osålda: de är signal),
  `raw_title`. Unik nyckel (`source`, `external_id`). `hammer_sek` beräknas som högsta bud.
- `source_health`: lägg till `stopped_reason` (t.ex. `'403'`, `'429'`, `'captcha'`) och `stopped_until`.
- Behåll typer som tål Postgres: JSON-kolumner för `image_urls`/`aliases`, ISO-tid i UTC.

## Kostnadsuppskattning för AI-steget

Priser enligt Anthropics modellöversikt (cachad 2026-09-25): `claude-haiku-4-5` 1 / 5 USD per MTok in/ut,
`claude-sonnet-5-5` 2 / 10 USD per MTok. Batches −50 %. Cacheläsning ≈ 0,1× inpris.
**Rättelse till rapporten:** "Haiku 5.5 för 0,10 USD/MTok" finns inte. Aktuell Haiku är 10 gånger dyrare
än rapporten räknade med. Bildtokens är uppskattade.

| Steg | Antagande | Per anrop | Per månad |
|---|---|---|---|
| Auctionet titeltolkning, första fyllningen | 330 000 objekt, ~40 % kräver LLM, ~300 in / 80 ut, Haiku Batches | ~0,00035 USD | **~45 USD engångs** |
| Auctionet titeltolkning, nattligt | ~120 objekt/dygn | ~0,00035 USD | ~1,3 USD |
| Steg 2 bildscreening (512 px + titel, cachad instruktion) | 200 annonser/dygn (push-vägen, **ej uppmätt**) | ~0,001 USD | ~6 USD |
| Steg 4 verifiering (4 × 784 px + text + kandidater) | ~30 % av screenade, ~5 300 in / 400 ut | ~0,007 USD | ~13 USD |
| Steg 8 eskalering till Sonnet 5.5 | ~10/dygn | ~0,015 USD | ~4,5 USD |
| **Summa löpande** | | | **~25 USD ≈ 250–275 kr/mån** |

Slutsats: väl under budgetmålet 1 500 kr/mån inklusive drift (VPS ~50–100 kr). PRD:ns mål "< 0,001 USD per
annons" i steg 2 nås ungefär, inte med marginal. Om Blocket ger tillstånd för full poller och möbelkategorin
ger tusentals annonser per dygn spräcker steg 2 dagsbudgeten 2 USD. Då behövs ett textfilter före
bildscreeningen, som PRD:n redan förutser.

## Beslut som behövs från ägaren innan M1
1. Skicka tillståndsmejlet till Blocket (eller ändra det först).
2. Godkänn Blocket-ingest via push, delning och tillägg (punkterna 2–4) som M1:s väg in.
3. Ja eller nej till Tradera-API som ny källa.
4. Gör GitHub-repot privat. Det är publikt i dag.
