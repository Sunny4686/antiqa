# Drift

En EU-VPS (t.ex. Hetzner CX22 i Helsingfors/Nürnberg, ~50 kr/mån) med Docker. Webben exponeras bara via
Cloudflare Tunnel; ingen port öppnas mot internet.

## Engångsuppsättning

1. **VPS:** installera Docker och Docker Compose, klona repot.
2. **`.env`:** kopiera `.env.example` och fyll i:
   - `ANTHROPIC_API_KEY` (console.anthropic.com)
   - `TELEGRAM_BOT_TOKEN` (skapa bot hos @BotFather), `TELEGRAM_CHAT_ID` (din chatt med boten),
     `TELEGRAM_WEBHOOK_SECRET` (valfri lång slumpsträng)
   - `INGEST_TOKEN` (lång slumpsträng; samma i telefonens vidarebefordran)
   - `CLOUDFLARE_TUNNEL_TOKEN` (steg 3)
   - Slumpsträngar: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
3. **Cloudflare:** Zero Trust → Networks → Tunnels → skapa tunnel, kopiera token. Public hostname,
   t.ex. `fyndjakt.<din-domän>` → `http://app:8000`.
4. **Cloudflare Access:** skapa en Self-hosted-applikation för hostnamnet med policy "Allow" för din e-post.
   Lägg till en **Bypass**-policy för sökvägarna `/health`, `/ingest/*` och `/telegram/webhook`. De skyddas
   i stället av sina egna tokens.
5. **Starta:** `docker compose up -d --build`
6. **Telegram-webhook:** `docker compose exec app uv run --no-sync fyndjakt telegram-webhook https://fyndjakt.<din-domän>`
7. **Inställningar:** öppna `/installningar` och sätt hemmets latitud och longitud, max avstånd och trösklar.
8. **Auctionet-comps:** `docker compose exec app uv run --no-sync fyndjakt auctionet-backfill` (≈ 1,5 h i
   bakgrunden). Sedan tolkas titlar nattligen i Batches, och bevakningslistan byggs på söndagar.
   Kör `fyndjakt auctionet-backfill --designer "Namn"` för extra djup bakåt per formgivare.

## Löpande

| Tid (svensk) | Jobb |
|---|---|
| var 15:e min | hälsokontroll, larmar "Källan trasig" |
| 02:00 | backup av SQLite till `data/backups/` (14 senaste sparas) |
| 03:00 | Auctionet: nya avslutade möbelobjekt |
| 04:00 | titeltolkning av nya comps (Batches, inom dagsbudgeten) |
| 06:00 | radera lokala bildkopior äldre än 7 dagar |
| sön 05:00 | bevakningslistan uppdateras och nya modeller får kännetecken/replikafällor |

**Backup utanför servern:** kopiera `data/backups/` vidare, t.ex. med `rclone` till en
lagringsbucket. Det kräver ett konto och har inte satts upp.

**Uppdatera:** `git pull && docker compose up -d --build` (migreringar körs vid start).

**Loggar:** `docker compose logs -f app`

## Blocket

Ingen egen hämtning från blocket.se. Annonser kommer in via `POST /ingest/listing`. Se
`docs/recon/RESULTAT.md` och `docs/recon/blocket_tillstand.md`.
`AI_SEND_LISTING_IMAGES` och `BLOCKET_ENABLED` ligger kvar på `false` tills tillståndet täcker det.
