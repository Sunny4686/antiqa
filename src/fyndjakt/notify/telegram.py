"""Telegram alerts via the Bot API. Formatting is pure and tested; sending is a thin httpx wrapper."""

import html
from dataclasses import dataclass

import httpx

FEEDBACK_BUTTONS = (
    ("köpt", "Köpt"),
    ("ej_intressant", "Ej intressant"),
    ("fel_modell", "Fel modell"),
    ("replika", "Replika"),
    ("bra_men_såld", "Bra men såld"),
)
FEEDBACK_LABELS = {k for k, _ in FEEDBACK_BUTTONS}


@dataclass
class AlertData:
    listing_id: int
    kind: str  # FYND | KOLLA_SJALV
    title: str
    url: str | None
    price_sek: int | None
    p25: int | None
    median: int | None
    p75: int | None
    n_comps: int
    net_sek: int | None
    roi: float | None
    distance_km: float | None
    municipality: str | None
    confidence: str
    candidate: str | None
    evidence: list[str]
    contradictions: list[str]
    needs_underside_photo: bool


def kr(v: int | None) -> str:
    return "?" if v is None else f"{v:,}".replace(",", " ") + " kr"


def format_alert(a: AlertData) -> str:
    e = html.escape
    head = "🔥 <b>FYND</b>" if a.kind == "FYND" else "👀 <b>Kolla själv</b>"
    lines = [f"{head}: {e(a.title)}", f"Pris: {kr(a.price_sek)}"]
    if a.median is not None:
        lines.append(f"Värde: {kr(a.p25)}–{kr(a.p75)} (median {kr(a.median)}), n={a.n_comps}")
    else:
        lines.append("Värde: inga jämförelseobjekt")
    if a.net_sek is not None:
        roi = f", ROI {a.roi:.0%}" if a.roi is not None else ""
        lines.append(f"Netto: {kr(a.net_sek)}{roi}")
    where = e(a.municipality or "okänd ort")
    if a.distance_km is not None:
        where = f"{round(a.distance_km)} km, {where}"
    lines.append(f"Avstånd: {where}")
    lines.append(f"Säkerhet: {a.confidence}" + (f" · Kandidat: {e(a.candidate)}" if a.candidate else ""))
    for ev in a.evidence[:2]:
        lines.append(f"✓ {e(ev)}")
    if a.contradictions:
        lines.append(f"✗ {e(a.contradictions[0])}")
    if a.needs_underside_photo:
        lines.append("📸 Be om foto av undersidan")
    return "\n".join(lines)


def keyboard(listing_id: int, url: str | None) -> dict:
    rows = []
    if url:
        rows.append([{"text": "Öppna annons", "url": url}])
    btns = [{"text": label, "callback_data": f"fb:{listing_id}:{key}"} for key, label in FEEDBACK_BUTTONS]
    rows += [btns[:3], btns[3:]]
    return {"inline_keyboard": rows}


def parse_callback(data: str) -> tuple[int, str] | None:
    parts = data.split(":", 2)
    if len(parts) != 3 or parts[0] != "fb" or parts[2] not in FEEDBACK_LABELS or not parts[1].isdigit():
        return None
    return int(parts[1]), parts[2]


class TelegramError(Exception):
    """Telegram API failure. The message never contains the request URL, which carries the bot token."""


class TelegramClient:
    def __init__(self, token: str, http: httpx.Client | None = None):
        self._base = f"https://api.telegram.org/bot{token}"
        self._http = http or httpx.Client(timeout=20.0)

    def _call(self, method: str, payload: dict, timeout: float | None = None) -> dict | list:
        try:
            r = self._http.post(f"{self._base}/{method}", json=payload, timeout=timeout or httpx.USE_CLIENT_DEFAULT)
        except httpx.HTTPError as e:
            raise TelegramError(f"{method}: {type(e).__name__}") from None
        if r.status_code != 200:
            try:
                detail = r.json().get("description", "")
            except ValueError:
                detail = ""
            raise TelegramError(f"{method}: HTTP {r.status_code} {detail}".strip()) from None
        return r.json()["result"]

    def send_alert(self, chat_id: str, text: str, markup: dict, photo_url: str | None, silent: bool) -> int:
        if photo_url and len(text) <= 1024:
            res = self._call(
                "sendPhoto",
                {
                    "chat_id": chat_id,
                    "photo": photo_url,
                    "caption": text,
                    "parse_mode": "HTML",
                    "reply_markup": markup,
                    "disable_notification": silent,
                },
            )
        else:
            res = self._call(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": markup,
                    "disable_notification": silent,
                    "link_preview_options": {"is_disabled": True},
                },
            )
        return res["message_id"]

    def get_updates(self, offset: int | None, timeout_s: int = 25) -> list[dict]:
        payload = {"timeout": timeout_s, "allowed_updates": ["callback_query"]}
        if offset is not None:
            payload["offset"] = offset
        return self._call("getUpdates", payload, timeout=timeout_s + 10)

    def delete_webhook(self) -> None:
        self._call("deleteWebhook", {})

    def send_text(self, chat_id: str, text: str, silent: bool = False) -> None:
        self._call("sendMessage", {"chat_id": chat_id, "text": text, "disable_notification": silent})

    def mark_handled(self, chat_id: str, message_id: int, label: str, callback_id: str) -> None:
        self._call("answerCallbackQuery", {"callback_query_id": callback_id, "text": f"Sparat: {label}"})
        self._call(
            "editMessageReplyMarkup",
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "reply_markup": {"inline_keyboard": [[{"text": f"✓ Hanterad: {label}", "callback_data": "noop"}]]},
            },
        )
