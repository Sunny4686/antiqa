# Cloud architecture, hosting and prior art for a small furniture-listing alert service (2026)

Method note: WebFetch could not resolve most vendor domains in this session (DNS errors for supabase.com, cloudflare.com, developers.cloudflare.com, wz-it.com). Most prices below therefore come from search-result snippets of official pages, or from third-party aggregators. They are flagged as such. Before the final report commits to any figure, verify it against the vendor pricing page. Currency conversions use approximate rates (1 EUR ≈ 11 SEK, 1 USD ≈ 10 SEK). These rates are assumptions and were not sourced.

## Hosting options and monthly cost (poller + web UI + Postgres/pgvector + image storage + ML inference)

### Takeaway
One small EU VPS (Hetzner, Germany or Finland) running Docker Compose can host the poller, the web UI, Postgres with pgvector and a local image cache for roughly €5–15/month (about 55–165 SEK). That leaves almost the whole 500–5000 SEK budget for AI API calls. A managed alternative is Supabase Pro ($25/month) plus a Cloudflare Workers paid plan ($5/month), which needs no server patching but costs more and adds vendor coupling. No GPU is needed: hosted multimodal embedding APIs cost about $0.12 per million tokens, and CPU inference of a small CLIP-type model is also feasible.

### Cited Findings
- **Hetzner April 2026 increase:** cloud prices rose 30–43% from 1 April 2026, for existing customers too. CX22 and CAX11 went from €3.29 to €4.49 in the EU. — [igorslab](https://www.igorslab.de/en/hetzner-to-significantly-increase-prices-for-cloud-and-dedicated-servers-from-april-2026/); [agentdeals summary](https://agentdeals.dev/hetzner-pricing-2026)
- **Hetzner June 2026 increase:** a second round took effect 15 June 2026, for new orders and rescales only. CAX11 (ARM) went from €4.49 to €5.99 in Germany and Finland. CX23, the successor to CX22, went from €3.99 to €5.49. CPX and CCX lines rose by up to +176%. — [wz-it blog (search snippet)](https://wz-it.com/en/blog/hetzner-price-increase-june-2026-cpx-ccx-alternatives/); [privatedevops](https://privatedevops.com/news/hetzner-june-2026-cloud-price-increase-what-to-do)
- **Hetzner availability:** an August 2026 analysis reports that Hetzner's cloud page labelled the Cost-Optimized plans (CX/CAX) "Currently not available", with a "Limited availability of cloud instances" notice since 26 June 2026. This was not verified against Hetzner directly. — [findstack](https://www.findstack.com/resources/hetzner-price-increase-2026); [capitalandcompute](https://capitalandcompute.net/blog/hetzner-price-increase-2026/)
- **Supabase free tier:** 2 active projects, 500 MB database, 1 GB file storage, 5 GB egress. Free projects pause after 7 days without activity. — [automationatlas](https://automationatlas.io/answers/supabase-free-tier-limits-2026/); [jetadmin 2026 guide](https://www.jetadmin.io/blog/supabase-pricing-2026-guide-to-plans-limits-and-real-world-costs/)
- **Supabase Pro:** $25/month per organization plus usage, with a $10 compute credit that covers one Micro instance (1 GB RAM). Sources disagree on Pro's included quotas: one lists 8 GB DB / 100 GB storage / 250 GB egress, another gives different egress splits. — [toolradar](https://toolradar.com/blog/supabase-pricing-2026); [activepieces](https://www.activepieces.com/blog/supabase-pricing-free-tier-limits-pro-costs-egress.md)
- **Cloudflare Workers Paid plan:** $5/month minimum per account. It includes Workers, KV, Hyperdrive and Durable Objects usage, with no egress charges. — [Cloudflare docs (preview mirror)](https://69edd8d5.previews.developers.cloudflare.com/workers/platform/pricing/index.md)
- **Cloudflare Browser Rendering ("Browser Run"):** the free tier gives 10 minutes/day. Workers Paid includes 10 browser-hours/month, then $0.09 per extra hour. 10 concurrent browsers are included, then $2 per extra browser. — [Cloudflare docs](https://developers.cloudflare.com/browser-rendering/pricing/)
  - A third-party report says the concurrency ceiling was raised to 200 on 20 August 2026, with 10 still included. — [ecorpit](https://ecorpit.com/cloudflare-browser-run-200-concurrent-browsers-billing-gap-2026/)
- **Cohere Embed v4:** aggregators list about $0.12 per million input tokens for text. The image variant on Azure is listed at about $0.47 per million. No official per-image price was found. — [cloudprice.net](https://cloudprice.net/models/embed-v4.0); [cloudprice.net img](https://cloudprice.net/models/cohere-embed-4-img)
- **Voyage multimodal-3.5:** aggregators list about $0.12 per million input tokens, a 32K context and vision input. — [getmaxim](https://www.getmaxim.ai/bifrost/llm-cost-calculator/provider/voyage/model/voyage-multimodal-3.5)
- **Self-hosted ntfy:** Railway offers one-click ntfy templates, so Railway is a viable PaaS for small always-on containers. — [railway](https://railway.com/deploy/ntfy-push-notifications)

### Inferences
- **Recommended baseline stack (about 100–400 SEK/month for infrastructure):**
  - Compute: one Hetzner ARM or x86 VPS with 4–8 GB RAM, in Falkenstein, Nuremberg or Helsinki. Hetzner is EU-owned, which simplifies GDPR.
  - Services: Docker Compose running Postgres 16/17 with pgvector, a Python poller/worker (Playwright where needed), a small web UI (FastAPI + HTMX, or Next.js) and Caddy.
  - Backups: nightly `pg_dump` to Hetzner Object Storage or Cloudflare R2. Cloudflare's EU jurisdiction setting is an option for R2; not verified this session.
  - Access: put Cloudflare Tunnel + Access in front for login, so no ports need to be open.
- **Image volume:** at a plausible volume of a few hundred to a few thousand new listings/day, images total only single-digit GB/month. Storing thumbnails plus the original image URL is enough. Full-resolution archiving is unnecessary.
- **AI cost dominates.** Embedding volume is small. For example, 3,000 images/day at roughly 1,000 tokens/image ≈ 90M tokens/month ≈ $11/month at $0.12/M. The token-per-image figure is an assumption. Vision-LLM scoring of shortlisted items (e.g. Claude or GPT-class models) is the real cost driver. Gate it behind cheap filters (keyword, price, category, embedding similarity to a "wanted" gallery) so only roughly 5–10% of listings reach the LLM.
- **CPU inference vs. hosted embeddings:** an open CLIP/SigLIP model on a 4–8 vCPU VPS can embed a few thousand images/day on CPU, at roughly 0.2–1 s per image (an estimate, not sourced). A GPU (Modal, Replicate) is only worth it for bulk backfills.
- **Avoid Supabase Free for an always-on service.** The pause-after-7-days rule matters less with a constant poller, but the 500 MB DB limit will fill with embeddings plus listing history.
- **Pure-Cloudflare stack (Workers + Cron + Queues + D1/Vectorize + R2):** cheap, at about $5–10/month. But D1 is not Postgres/pgvector, and polling sites with Browser Rendering is metered. This suits an e-mail-ingest design better than a scraping design.
- **Fly.io, Render, Railway, Neon, Vercel:** all workable, but each adds a second vendor for the database or has per-service pricing. For 1–3 users a single VPS is simplest and cheapest.

### Gaps
- Official current prices for Fly.io, Railway, Render, Neon and Vercel were not retrieved: fetches failed and searches were not run due to budget.
- Exact current Hetzner prices and stock status: the Hetzner site was not reachable.
- Hetzner Object Storage pricing, and R2 free tier and storage price: not confirmed this session.
- Official per-image pricing for Cohere Embed v4 and Voyage multimodal: only aggregator figures were found. Jina, Modal and Replicate pricing was not researched.

## Private login with own domain for 1–3 users

### Takeaway
Cloudflare Zero Trust Access (free for up to 50 users) in front of a Cloudflare Tunnel is the lowest-effort option. It needs no auth code in the app, accepts an e-mail one-time PIN or Google login, and keeps the origin off the public internet. App-level auth (Supabase Auth, Clerk, passkeys) is only needed if the PWA must work with web push and offline sessions in ways an Access cookie complicates.

### Cited Findings
- **Free plan:** Cloudflare Zero Trust is free for teams under 50 users with no time limit. Pay-as-you-go is $7/user/month. — [Cloudflare Access product page](https://www.cloudflare.com/en-au/products/cloudflare-access); [costbench](https://costbench.com/software/business-vpn/cloudflare-zero-trust/free-plan/)
- **Free-plan limits:** 24-hour log retention and community support only. — [Cloudflare blog (teams plans)](https://blog.cloudflare.com:8443/teams-plans); [costbench](https://www.costbench.com/software/business-vpn/cloudflare-zero-trust/)
- **Setup:** "Self-hosted" apps on your own domain or subdomain are added under Access > Applications. Google login can be added as an identity provider. — [domainindia KB](https://domainindia.com/support/kb/cloudflare-zero-trust-access-internal-apps); [shoutmeloud](https://www.shoutmeloud.com/cloudflare-zero-trust-google-login-web-app.html)

### Inferences
- **Pros of Cloudflare Access:** zero code, MFA via the identity provider, and the origin is hidden behind a Tunnel.
- **Cons of Cloudflare Access:**
  - The Access session cookie expires, which can interrupt PWA usage and service-worker fetches.
  - The web-push endpoint and any notification action callback URL (e.g. "mark as bought") need either a bypass policy with signed tokens or a service-token.
  - Callbacks from Telegram, ntfy or Pushover must reach a webhook path excluded from Access, authenticated with a secret instead.
- **Self-hosted alternatives (Authelia, Authentik):** add a component to maintain. Not worth it for 1–3 users when Cloudflare Access is free.
- **Clerk and Supabase Auth:** sensible only if the app is built on that ecosystem anyway.
- **Passkeys:** a nice addition through a library such as SimpleWebAuthn, but they mean writing your own user and session handling.

### Gaps
- Clerk free-tier limits, Supabase Auth specifics and Authelia passkey support in 2026 were not verified.
- How Cloudflare Access interacts with PWA install and service-worker push on iOS was not verified; no source found.

## Push notifications: options, iOS status, rich content and actions

### Takeaway
For 1–3 users, a Telegram bot or ntfy gives the richest, most reliable notifications with the least work: image, text and action buttons that call back into the app. Pushover ($4.99 one-time per platform) is a very reliable alternative with images; its action-button support was not verified this session. iOS PWA Web Push works when the app is installed to the Home Screen, but sources report flaky subscriptions and conflicting claims about EU status, so it should not be the only channel.

### Cited Findings
- **iOS web push baseline:** iOS 16.4 (March 2023) added Web Push for Home-Screen web apps. Users must install the app and grant permission. — [MagicBell guide](https://www.magicbell.com/blog/pwa-ios-limitations-safari-support-complete-guide); [Apple dev forum](https://developers.apple.com/forums/thread/745414?page=2)
- **EU status (conflicting):**
  - In 2024 Apple first planned to remove Home-Screen web apps in the EU under the DMA, then reversed course and kept them in iOS 17.4. — [Apple dev forum](https://developers.apple.com/forums/thread/745414?page=2)
  - Contradicted by MagicBell (vendor blog), which lists EU PWA push as unsupported from 17.4. — [MagicBell](https://www.magicbell.com/blog/pwa-ios-limitations-safari-support-complete-guide)
  - This conflict is unresolved. Test on a real Swedish iPhone.
- **Stability:** iOS push subscriptions sometimes "disappear" without explanation, even on iOS 18, and iOS push stability lags behind Android. — [webscraft 2026](https://webscraft.org/blog/pwa-pushspovischennya-na-ios-u-2026-scho-realno-pratsyuye?lang=en)
- **ntfy features:** supports attachments and action buttons that let users respond to notifications directly, and has an official iOS app. — [ntfy.sh (mirror)](https://scriptagc.wasmer.app/https_ntfy_sh); [openapps](https://openapps.pro/apps/ntfy)
- **ntfy hosted tiers:** Supporter $6/month, Pro $12/month ($10 annual), Business $25/month. Railway lists lower starting prices, which conflicts. — [itechguides](https://www.itechguides.com/products/ntfy/); [toolradar](https://toolradar.com/tools/ntfy/alternatives)
- **ntfy self-hosting:** ntfy can be self-hosted; Railway has one-click templates for it. — [railway](https://railway.com/deploy/ntfy-push-notifications)
- **Pushover pricing:** $4.99 one-time per platform with no subscription for individuals, and a 30-day free trial. — [pushover.net/pricing](https://pushover.net/pricing); [pushover.net/licensing](https://pushover.net/licensing)
- **Pushover 5.0:** added end-to-end encryption, and 5.0.6 was released on 8 August 2026. — [appshunter](https://appshunter.io/ios/app/506088175)

### Inferences
- **Telegram bot:** probably the best fit for the "open listing / bought / skip" workflow.
  - It is free, works on all devices, and sends a photo with a caption and an inline keyboard. Button presses arrive at the backend as callback queries, and the bot can then edit the message, e.g. to mark it as handled.
  - Latency is typically seconds.
  - This comes from general Bot API knowledge (`sendPhoto` with `reply_markup.inline_keyboard`, `callback_query`); it was not re-verified this session.
- **ntfy on iOS:** iOS delivery from a self-hosted ntfy server relies on relaying through ntfy.sh's upstream for APNs. That is a known nuance (not verified this session) and favours using ntfy.sh hosted or Telegram.
- **Recommended design:**
  - A primary channel (Telegram, or ntfy/Pushover) for instant alerts with an image and buttons.
  - The PWA as the "inbox" UI for triage, history and feedback labels, which feed ML retraining.
  - E-mail only as a daily digest.
  - Discord is equivalent to Telegram but weaker for personal phone alerts.

### Gaps
- Exact iOS 26 Web Push status in the EU: no authoritative Apple or WebKit 2026 source was retrieved.
- Pushover action-button capability, and its image-attachment size limits, were not verified.
- No measured latency or reliability comparison across channels was found.

## Ingest patterns (e-mail, browser extension, headless polling) and scheduling

### Takeaway
Blocket has no official API. Unofficial wrappers (the `blocket-api` Python package, Apify actors) exist but can break whenever Blocket changes. Facebook Marketplace is login-walled and actively blocks scrapers, with ToS risk. A pragmatic hybrid:
- Poll Blocket and Tradera search endpoints at modest intervals (1–5 min) from the VPS.
- Ingest Facebook Marketplace and other sites through a user-side Manifest V3 browser extension, or through saved-search e-mail alerts, rather than server-side scraping.

### Cited Findings
- **`blocket-api` package:** an unofficial Python wrapper for blocket.se. A tracker lists v0.5.1 with 33 releases (data as of April 2026). Another project describes it as "semi-stable, unofficial", tested against the live API, and notes Blocket has no official API, so it relies on reverse-engineering. — [depscope](https://depscope.dev/pkg/pypi/blocket-api); [piwheels](https://www.piwheels.org/project/blocket-api); [sverige-begagnad-mcp on PyPI](https://pypi.org/project/sverige-begagnad-mcp/0.1.0/)
- **Apify actors:** several hosted Blocket scrapers exist, e.g. fervent_bus/blocket-scraper, aurenic, tagadanar and shahidirfan. — [Apify](https://apify.com/fervent_bus/blocket-scraper); [Apify](https://apify.com/shahidirfan/blocket-se-search-scraper.md)
- **Facebook Marketplace:** it has no API and lives behind login walls. Scraping tools break with Facebook updates, fast requests trigger checks and blocks, and the practice often violates the Terms of Service. Low-volume, own-session browsing with pauses is advised. — [data365 (vendor)](https://data365.co/blog/facebook-marketplace-scraper); [axiom.ai](https://axiom.ai/scrape/facebook-marketplace/)
- **Blocket's own alerts:** the official app supports "bevakningar" (saved searches) with push notifications when matching items are posted. — [Blocket App Store listing](https://apps.apple.com/se/app/blocket-k%C3%B6p-s%C3%A4lj-begagnat/id323710525)
  - A GitHub scraper project (around 2020) claimed Blocket's notifications arrived about 30 minutes after posting, which motivated faster polling. — [scraper-blocket (proxy mirror)](https://proxy-ga.blitzz.co/proxy/123456/github.com/WilhelmvonArndt/scraper-blocket)
- **Cloudflare Browser Rendering:** a managed headless-browser option with 10 hours/month included on Workers Paid. — [Cloudflare docs](https://developers.cloudflare.com/browser-rendering/pricing/)

### Inferences
- **Polling:** JSON search endpoints (via `blocket-api` or by inspecting network calls) are far cheaper and more robust than Playwright.
  - Keep Playwright as a fallback for detail pages only.
  - Use APScheduler, cron or systemd timers in the worker container, with jitter, a conditional "seen IDs" set in Postgres, and exponential backoff on 4xx/429.
- **E-mail ingest:** forward Blocket, Tradera or eBay saved-search alert e-mails to a Cloudflare Email Worker or a Postmark inbound webhook, then parse the listing URLs. This is robust and ToS-friendly, but it has the alert latency noted above (possibly about 30 min; unverified for 2026).
- **MV3 browser extension:** a content script on facebook.com/marketplace pages the user is already viewing posts the listing JSON to the backend with an API token. It is low-risk because it uses the user's own session at human pace, but it only captures what the user browses.
  - An extension can also open background tabs periodically, but that increases ban risk.
- **Legal and GDPR:** store only listing data needed for scoring. Seller names are personal data, so minimise or drop them. Respect robots.txt and rate limits.

### Gaps
- Whether Blocket changed its platform or API in 2025–2026: one search found nothing, so this is unverified.
- Tradera API: Tradera historically had an official developer API (SOAP) with an app key. Its 2026 status was not researched.
- Current Blocket alert latency was not verified.
- Gmail API and Postmark inbound pricing were not researched.

## Prior art: marketplace monitoring, arbitrage and valuation tools

### Takeaway
The commercial alert products are mostly US-centric (Facebook, Craigslist, OfferUp, eBay). They compete on speed (per-minute scans, alerts within seconds) and on profit estimates from sold comparables, and charge roughly $10/month. Swedish prior art is mainly hobby GitHub scrapers for Blocket plus Apify actors. Valuation databases (WorthPoint) are priced at roughly $27–30/month and their sold-price coverage skews to US auctions. Lessons:
- Speed matters.
- Scraping fragility is the main failure mode.
- Sold-price comparables are the key valuation signal.
- Ads and limited platform coverage are the main user complaints.

### Cited Findings
- **Swoopa:** an iOS app that scans local classifieds (Facebook Marketplace, Craigslist, OfferUp) and alerts on new postings.
  - Rated about 4.4/5 from roughly 300 ratings. Reviewers praise fast alerts and filters; complaints are ads, incomplete site coverage and slow upgrades. — [Spark/MWM listing](https://spark.mwm.ai/us/apps/swoopa/6475300269); [Grand Screen review](https://grand-screen.com/apps/swoopa/)
  - Swoopa also sells a "Reposter" for relisting items. — [App Store](https://apps.apple.com/us/app/-/id6744046113)
  - Described as suited to no-code users, especially for vehicles. DealScout is a freemium alternative with keyword, price and location alerts. — [ScrapeCreators](https://scrapecreators.com/blog/facebook-marketplace-alerts); [AlternativeTo DealScout](https://alternativeto.net/software/dealscout/about)
- **Flipify:** premium plans scan marketplaces every minute and alert within seconds. It compares listings to recently sold eBay items to estimate profit margin. From $10/month, usage-based, with a free version. — [Capterra](https://www.capterra.com/p/10050498/Flipify/)
- **Deal Scout 360:** scans eBay continuously and sends e-mail alerts with price, shipping, condition and link. It filters on keywords, price, condition, listing type, auction end time and location. From $9.99, with a free version. — [Capterra](https://www.capterra.co.uk/software/1087408/Deal-Scout-360)
- **WorthPoint pricing:** the Price Guide is about $26.99–29.99/month or about $250–260/year, with figures varying by source. — [App Pricing Lab](https://apppricinglab.com/iap/apple/1472512649); [underpricedai (competitor)](https://underpricedai.com/blog/is-worthpoint-worth-the-price-honest-review-from-a-reseller-in-2026)
- **WorthPoint coverage:** it claims over 730–845 million sold prices and a marks database of 150,000+ marks. A competitor review says it misses recent Poshmark, Mercari and Facebook sold data. — [WorthPoint landing page](https://pages.worthpoint.com/pages/welcome-landing-fb/); [underpricedai](https://underpricedai.com/blog/worthpoint-review)
- **Blocket GitHub projects:** WilhelmvonArndt/scraper-blocket is a Python scraper that checks Blocket constantly to beat the native alert delay. The GitHub "blocket" topic lists other scrapers, some with instant notifications, last updated around 2020. — [proxy mirror](https://proxy-ga.blitzz.co/proxy/123456/github.com/WilhelmvonArndt/scraper-blocket); [GitHub topic](https://github-redirect.dependabot.com/topics/blocket)
- **Swedish MCP server:** a PyPI project, `sverige-begagnad-mcp`, exposes Swedish second-hand marketplaces to AI agents and builds on `blocket-api`. — [PyPI](https://pypi.org/project/sverige-begagnad-mcp/0.1.0/)

### Inferences
- **Lessons to apply:**
  1. Alert latency is the core value. Commercial tools advertise per-minute scanning.
  2. Valuation relies on sold-price comps, not asking prices. For Swedish design furniture, the relevant comps are auction houses (Bukowskis, Lauritz, Auctionet, Stockholms Auktionsverk) and Tradera completed sales, more than US databases like WorthPoint. These comp sources were not researched in this session.
  3. Scrapers break. Build source adapters behind one interface, with health checks and alerts when a source returns zero results.
  4. Commercial apps' main complaints are ads and coverage, which a private tool avoids.
- **Gap in the market:** no Swedish commercial "Swoopa for Blocket" was found. Swedish tools appear to be hobby scrapers or Apify actors.

### Gaps
- Product details for Kovels, Google Lens accuracy on furniture, and "Magnus" (art valuation app) were not retrieved.
- Swedish startups in this space were not identified.
- No post-mortems or Hacker News discussions on failed marketplace-alert or arbitrage tools were found. A search returned only general scraping material.
- Kleinanzeigen-specific alert bots were not found in the results.

## Repo structure and dev workflow for a solo developer with an AI coding assistant

### Takeaway
Everything below is inference rather than sourced fact; no sources were researched for this question within the budget. The recommendation is a single monorepo with a small number of deployable units (worker, web, DB migrations), Docker Compose for both local dev and production, and explicit project instructions for the AI assistant (a CLAUDE.md or AGENTS.md).

### Cited Findings
- None. No sources were gathered for this question.

### Inferences
- **Suggested layout:**
  - `apps/web`: UI, either FastAPI + HTMX/Jinja or Next.js.
  - `apps/worker`: pollers, ingestion adapters per source, scoring pipeline, notifier.
  - `packages/core`: shared models, Pydantic schemas, the source-adapter interface.
  - `ml/`: notebooks, eval sets, a labelled examples gallery, prompt files.
  - `db/migrations`: Alembic, or plain SQL with sqitch/dbmate.
  - `infra/`: `docker-compose.yml`, Caddy/cloudflared config, backup scripts.
  - `tests/`: recorded HTTP fixtures per source (VCR-style), for deterministic adapter tests.
  - `CLAUDE.md`: commands, conventions and "never commit secrets" rules.
- **Single language:** Python end to end (uv, ruff, pytest). The ML, scraping and Playwright ecosystems are Python-first, which lowers context-switching for both developer and AI assistant.
- **Workflow:**
  - Feature branches with small PRs.
  - GitHub Actions running lint, tests and a Docker image build pushed to GHCR.
  - Deploy with `docker compose pull && up -d` over SSH, or Watchtower.
  - Secrets in `.env` on the server (or sops/age), never in the repo.
  - Keep an eval set of labelled listings so prompt and model changes can be regression-tested by the AI assistant.
  - Log every LLM call's cost to Postgres to enforce the SEK budget, with a hard daily cap in code.
- **Observability:** a `/health` endpoint per source adapter (last success time, item count), and a heartbeat to a free uptime monitor or ntfy if a source goes silent.

### Gaps
- No sourced best-practice references (blog posts or HN threads on solo-dev monorepos with AI assistants) were collected.
