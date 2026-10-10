import argparse
import logging


def main() -> None:
    parser = argparse.ArgumentParser(prog="fyndjakt")
    sub = parser.add_subparsers(dest="cmd", required=True)
    serve = sub.add_parser("serve", help="Kör webb + jobb")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    sub.add_parser("migrate", help="Uppgradera databasen")
    bf = sub.add_parser("auctionet-backfill", help="Köa första fyllningen av Auctionet-comps (körs av workern)")
    bf.add_argument("--designer", action="append", default=[], help="Extra formgivarfråga, kan upprepas")
    wh = sub.add_parser("telegram-webhook", help="Registrera Telegram-webhooken")
    wh.add_argument("base_url", help="t.ex. https://fyndjakt.example.se")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # request lines contain the Telegram bot token

    if args.cmd == "migrate":
        from fyndjakt.migrate import upgrade

        upgrade()
    elif args.cmd == "auctionet-backfill":
        from fyndjakt.db import session_scope
        from fyndjakt.jobs import backfill_plan
        from fyndjakt.migrate import upgrade
        from fyndjakt.services import enqueue

        upgrade()
        plan = backfill_plan(args.designer)
        with session_scope() as session:
            enqueue(session, "auctionet_backfill", {"todo": plan})
        print(f"Köat: {len(plan)} steg (≤ 10 000 objekt vardera, 1 förfrågan / 5 s). Körs av `fyndjakt serve`.")
    elif args.cmd == "telegram-webhook":
        import httpx

        from fyndjakt.config import get_config

        cfg = get_config()
        if not (cfg.telegram_bot_token and cfg.telegram_webhook_secret):
            raise SystemExit("TELEGRAM_BOT_TOKEN och TELEGRAM_WEBHOOK_SECRET måste finnas i .env")
        r = httpx.post(
            f"https://api.telegram.org/bot{cfg.telegram_bot_token}/setWebhook",
            json={
                "url": args.base_url.rstrip("/") + "/telegram/webhook",
                "secret_token": cfg.telegram_webhook_secret,
                "allowed_updates": ["callback_query"],
            },
            timeout=20,
        )
        print(r.json())
    elif args.cmd == "serve":
        import uvicorn

        uvicorn.run("fyndjakt.web.app:app", host=args.host, port=args.port)
