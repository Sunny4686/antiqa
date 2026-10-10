# Bukowskis och Tradera: genomgång 2026-10-10

## Bukowskis (referensdata: slutpriser och bilder)
- robots.txt (sparad här): `Disallow` bara för `/admin/`, `/cms/` och PDF:er. Objektsidor och arkiv är tillåtna.
- Villkor (`/sv/legal`): köp-, sälj- och transportvillkor. Inga regler om webbplatsens innehåll, automatiserad
  åtkomst eller skrapning. Content and User Data Policy (customerservice.bukowskis.com) nämner inte heller det.
- Inget API. Objektsidor (`/sv/lots/<id>-<slug>`) är Next.js med `__NEXT_DATA__`: titel, klubbat pris, datum,
  beskrivning, skick och bilder (cloudfront).
- Rättslig grund för att analysera texter och bilder: undantaget för text- och datautvinning (URL 15 a §), som
  gäller när rättighetshavaren inte har reserverat sig maskinläsbart. Bukowskis har ingen sådan reservation.
- Villkor vi håller: högst 1 förfrågan per 10 s, tydlig User-Agent med kontakt, bara offentliga objektsidor,
  stopp och larm vid 403/429/CAPTCHA, bilder bara som nedskalade analyskopior. Inget publiceras vidare.

## Tradera (fyndkälla, inte referensdata)
- Officiellt API (api.tradera.com). Kräver registrerat AppId och AppKey (ägaren registrerar).
- Tillåtet enligt utvecklarvillkoren: sökning och upptäckt, analys, notiser. Otillåtet: auktionssniping,
  automatisk budgivning och kringgående av marknadsplatsens skydd.
- Gräns: 10 000 anrop per metod och dygn.
- API:t söker bara pågående objekt; sålda objekt med slutpris finns inte (bara egna transaktioner). Tradera blir
  alltså en källa för nya annonser med bilder, inte för slutpriser.
- robots.txt (sparad här) gäller webbplatsen, inte API:t; vi använder bara API:t.
