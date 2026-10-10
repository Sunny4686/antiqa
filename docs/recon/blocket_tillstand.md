# Tillstånd från Blocket för automatiserad läsning

| | |
|---|---|
| Form | **Muntligt** (telefonsamtal med Blockets kundsupport) |
| Datum | 2026-10-10 |
| Kontaktperson / ärendenr | _fyll i_ |
| Omfattning enligt samtalet | _fyll i: vad som får hämtas, takt, sortering_ |
| Gränser nämnda i samtalet | _fyll i_ |

## Avvägning

Blockets användarvillkor (gällande från 2026-09-01) kräver "föregående skriftligt tillstånd" för
automatiserade tjänster. De anger också att "all otillåten användning medför ersättningsskyldighet".
Ägaren har bedömt att det muntliga tillståndet räcker och beslutat att gå vidare (2026-10-10), med
vetskap om att det inte uppfyller villkorens krav på skriftlig form. Om Blocket senare bekräftar
skriftligt ska bekräftelsen sparas här.

## Gränser vi håller (konservativt, tills andra gränser är kända)

- Högst 1 sökanrop per 2–5 min (slumpad jitter). Högst en samtidig förfrågan mot blocket.se.
- Enskilda annonssidor hämtas bara för nya träffar, i samma kö och med samma minsta avstånd.
- Öppen User-Agent som identifierar tjänsten.
- Ingen inloggning, inget kringgående. Vid 403/429/CAPTCHA stoppar källan och ägaren larmas.
  Inget adressbyte.
- `?sort=` (spärrat i robots.txt) används inte om standardordningen räcker.
- Inga säljaruppgifter sparas.

Om Blocket hör av sig eller återkallar tillståndet ska pollern stängas av direkt (`BLOCKET_ENABLED=false`).
