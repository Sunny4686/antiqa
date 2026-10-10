import argparse
import logging


def main() -> None:
    parser = argparse.ArgumentParser(prog="fyndjakt")
    sub = parser.add_subparsers(dest="cmd", required=True)
    serve = sub.add_parser("serve", help="Kör webb + jobb")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    sub.add_parser("migrate", help="Uppgradera databasen")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    if args.cmd == "migrate":
        from fyndjakt.migrate import upgrade

        upgrade()
    elif args.cmd == "serve":
        import uvicorn

        uvicorn.run("fyndjakt.web.app:app", host=args.host, port=args.port)
