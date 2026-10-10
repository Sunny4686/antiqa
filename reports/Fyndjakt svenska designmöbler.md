# Låt Blockets egna larm hitta designfynden

Den smalaste fungerande versionen av tjänsten skrapar inte Blocket. Blocket sköter grovfiltreringen genom 20–50 noga formulerade bevakningar. Deras snabba app-push fångas på din egen Android-telefon och skickas vidare till en liten server. Där bedömer deterministisk kod och en billig vision-LLM (Claude Haiku 5.5) annonsen mot en handkurerad bevakningslista med modeller och jämförbara slutpriser, som du bygger själv från Auctionet, egna affärer och dina böcker. Notisen skickas via Telegram, och bara när beräknad nettomarginal och avstånd klarar dina trösklar. Upplägget håller sig långt under budgeten: drift plus AI-anrop landar runt **200–600 SEK/månad**, eftersom Haiku 5.5 kostar 0,10 USD per miljon indatatokens ([Anthropic](https://platform.claude.com/docs/en/about-claude/pricing)). Det minimerar också den juridiska risken, eftersom data som Blocket själv skickar till dig inte innebär någon ny åtkomst till deras system. Pengar och teknik är alltså inte flaskhalsen. Det som avgör om verktyget lönar sig är tre saker. Den första är hur snabbt och hur innehållsrikt Blockets push faktiskt är efter plattformsbytet i november 2025. Den andra är om du kan få fram tillräckligt många pålitliga slutpriser per modell. Den tredje är om marginalen överlever auktionsavgifter på 20–25 % på köparsidan plus säljarprovision och frakt. Båda de första är overifierade och ska testas under vecka 1. Arbitraget finns främst i segment där privatsäljare inte känner igen det de säljer, som mindre kända svenska formgivare från 50–70-talen och vintage-IKEA med namngiven formgivare, och mer sällan i Josef Frank eller Axel Einar Hjorth. Rapporten avslutas med en fasplan med kill-kriterier och en färdig PRD-prompt för AI-kodassistenten.

**Läsanvisning om källäget.** Underlaget samlades in den 10 oktober 2026 i en miljö där direkthämtning av blocket.se, auctionet.com, bukowskis.com och flera nyhetssajter misslyckades. **Blockets och Auctionets användarvillkor och robots.txt har inte lästs ordagrant.** Flera priser kommer från sökmotorers sammanfattningar eller sekundärkällor. Det som anges som "egen bedömning" eller "overifierat" ska behandlas som hypoteser. Avsnittet *Detta måste verifieras* samlar dem. Rapporten är en riskbedömning, inte juridisk rådgivning.

## Arbitraget finns i okända namn, inte i Frank och Hjorth

Marknaden är stark. I juli 2026 beskrev en designexpert på Stockholms Auktionsverk designauktionsmarknaden som "hetare än på länge". Nya köpare hade kommit in och stannat, och vissa 1900-talsklassiker hade gått från sommarstugemöbler till samlarobjekt ([Realtid](https://www.realtid.se/realtidtv/din-gamla-stol-kan-vara-vard-100-000-experten-pekar-ut-fynden/), via sökmotorns sammanfattning). Enligt Auctionets svenska sökstatistik för 2025 toppas formgivarlistan av **Josef Frank, Bruno Mathsson och Carl Malmsten**, Svenskt Tenn och 1900-talsdesign dominerar och jugend är den populäraste epoken ([Auctionet/Mynewsdesk](https://www.mynewsdesk.com/se/auctionet/subjects/livsstil-mode-fritid-inredning)). I toppen finns sexsiffriga belopp: ett Utö-bord av Hjorth klubbades för **340 000 SEK mot ett utrop på 150 000–200 000 SEK** ([Bukowskis](https://bukowskis.com/en/auctions/632/315-axel-einar-hjorth-bord-uto-nordiska-kompaniet-1930-tal)). Samma medier som rapporterar sådana rekord lär dock privatsäljarna vad de har. Ett Hjorth-bord för 800 kr på Blocket är en lottovinst, inte en affärsmodell.

Den realistiska fyndzonen är där auktionsintresset är högt men igenkänningen låg. Vintage-IKEA är det tydligaste beviset. Ett par gula Impala-fåtöljer av Gillis Lundgren klubbades för **38 100 SEK** på Växjö Auktionskammare ([Dagens PS](https://www.dagensps.se/privatekonomi/ikea-fatoljen-kostade-268-kronor-och-klubbades-for-190-000-kronor/), via sökmotorns sammanfattning). Karin Mobrings Natura-fåtöljer har sålts för 1 362 USD per par, och handlare pekar ut Mobring, Bengt Ruda och Tord Björklund som de mest eftertraktade IKEA-formgivarna ([Homes & Gardens](https://www.homesandgardens.com/interior-design/the-most-valuable-vintage-ikea-pieces)). Mediebevakningen av Impala har samtidigt varit så omfattande att just den modellen sannolikt redan är "känd" bland säljarna. Fyndet ligger i de mindre omskrivna IKEA-modellerna och i mellanskiktet av svenska formgivare och tillverkare, som Ekström/Lamino, Alf Svensson, Malmvall, Folke Ohlsson/Dux, Nils Jonsson och Kristiansson/Luxus. **Prisnivåerna för hela mellanskiktet saknar verifierade källor.** Underlaget för dem är modellens bakgrundskunskap, och de är den viktigaste luckan att fylla genom att manuellt gå igenom Auctionets avslutade objekt per formgivare.

### Avgifterna äter hälften innan du har tjänat en krona

Marginalkalkylen är det som sorterar bort de flesta "fynd". Köparprovisionen på svenska auktionshus ligger typiskt på **22–25 %** ([Estimonia](https://estimonia.com/directory/country/sweden)). Den betalas visserligen av köparen, men den sänker vad budgivarna är beredda att lägga i klubbslag. Säljaren betalar dessutom provision, enligt en fransk källa upp till 20 % ([mr-expert](https://mr-expert.com/en/auction-sales-seller-and-buyer-fees/)), och fasta avgifter per rop. Svenska flippare konstaterar torrt att "en stor % försvinner i avgifter … samt till frakt" ([Rika Tillsammans](https://rikatillsammans.se/forum/t/extrainkomst-flippa-grejer/24471)).

Min arbetsmodell, som ska kalibreras mot verkliga avräkningar, är att säljaren får **0,75–0,8 av klubbslaget** minus några hundra kronor i fasta avgifter. Därtill kommer transport, ofta flera hundra till 1 500 SEK per större möbel. Tumregeln blir att betala högst 40–50 % av förväntat klubbslag, och att objekt under cirka 2 000–3 000 SEK i förväntat klubbslag sällan lönar sig via auktionshus. Utropet är inget tak, vilket Hjorth-bordet ovan visar. Verktyget ska ändå räkna konservativt, på den nedre kvartilen av jämförbara slutpriser och inte på medianen.

### Replikor och licensproduktion är den största felköpsrisken

Många klassiker tillverkas fortfarande. String Furniture återupptog produktionen 2004 ([Nest](https://www.nest.co.uk/design-icon-string-pocket)), och sedan 2005 cirkulerar nyproducerade hyllor parallellt med vintage ([Rig/Lunds universitet](https://journals.lub.lu.se/rig/article/download/10466/9464/25357)). Wegners CH24 har märkning under sitsen, men etiketter kan ha lossnat på äkta stolar, så frånvaro av etikett bevisar ingenting ([Utility Design](https://www.utilitydesign.co.uk/blog/spotlight-on-the-carl-hansen-ch24-wishbone-chair/); [1stDibs](https://www.1stdibs.com/answers/how-can-you-tell-if-a-wishbone-chair-is-real)). Följden för verktyget är att det ska skilja mellan tre nivåer av säkerhet: **modell identifierad** (ofta möjligt från foton), **tillverkare och period** (kräver foto av märkning och undersida) och **skick**. Standardåtgärden före köp blir "be säljaren om foto av undersidan". En annons som säger "i stil med Mathsson" eller "Wegner-stil" ska automatiskt nedgraderas.

## Blockets egen push är den snabbaste och renaste datakällan

Blocket har ingen känd publik API eller feed för privatpersoner. Den officiella vägen är bevakningar: **push kommer "kort efter" att en matchande annons publicerats, medan e-post skickas en gång per dag** ([Blocket hjälpcenter](https://blocket.zendesk.com/hc/sv/articles/22875498207506-Bevakningar), enligt sökutdrag). Ett hobbyprojekt från cirka 2020 hävdade att notiserna kom cirka 30 minuter efter publicering, och det var skälet till att projektet byggde en egen skrapa ([scraper-blocket](https://proxy-ga.blitzz.co/proxy/123456/github.com/WilhelmvonArndt/scraper-blocket)). Uppgifterna går inte att förena utan mätning.

Till det kommer plattformsbytet. Blocket gick den **18 november 2025** över till en ny sajt byggd på Finn-teknik ([Carup](https://carup.se/nya-blocket-far-bilforsaljningen-att-rasa/)). Enligt Realtid finns "bevakningar, favoriter, söklogik – ingenting av det gamla" kvar ([Realtid](https://www.realtid.se/bors-finans/affarer/massprotest-mot-blocket-storflykt-till-konkurrenter/)). Gamla skrapor, URL-mönster och erfarenheter om notisernas innehåll är därmed opålitliga. Inofficiella wrappers som Python-paketet `blocket-api` bygger på reverse engineering och beskrivs som "semi-stable, unofficial" ([PyPI: sverige-begagnad-mcp](https://pypi.org/project/sverige-begagnad-mcp/0.1.0/)). Betalda Apify-skrapor kostar cirka **3–5 USD per 1 000 resultat** ([Apify](https://apify.com/solidcode/blocket-scraper)). Vid en full möbelkategori blir det tusentals kronor i månaden och spräcker budgeten.

### Juridiken: avtal och databasrätt väger tyngre än dataintrång

Huvudrisken är civilrättslig och har tre delar. Den första är katalogskyddet i **49 § upphovsrättslagen**, som ger den som gjort en väsentlig investering i en databas ensamrätt till hela eller väsentliga delar av den ([Riksdagen](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/lag-1960729-om-upphovsratt-till-litterara-och_sfs-1960-729/)). Även upprepade små uttag kan sammantaget räknas som ett väsentligt uttag ([Direktiv 96/9/EG](https://eur-lex.europa.eu/legal-content/SV/TXT/?uri=CELEX:31996L0009)). EU-domstolen har i CV-Online (C-762/19, 2021) gjort intrånget beroende av om användningen **skadar databasframställarens möjlighet att få tillbaka sin investering** ([Clifford Chance](https://cliffordchance.com/expertise/services/intellectual-property/global-ip-updates/2021/q4/cv-online-latvia-v-melons.html)). Det talar för en liten, intern och icke-konkurrerande användning.

Den andra delen är avtalet. Enligt Ryanair (C-30/14) kan en sajtägare förbjuda skrapning genom villkor även när databasen saknar immaterialrättsligt skydd ([Law Gazette](https://lawgazette.co.uk/legal-updates/protection-for-unprotected-databases/5046552.article)). Ingen Blocket-specifik klausul om robotar hittades, men jämförbara svenska plattformar förbjuder uttryckligen automatiserad insamling ([Nordnet](https://www.nordnet.se/faq/ovrigt/regler-foer-scraping-och-automatisk-datainsamling)). Blocket har dessutom tidigare vunnit i tingsrätten om sin "oinskränkta rätt" till annonsbilder ([SVT](https://www.svt.se/nyheter/inrikes/blocket-far-salja-vidare-dina-bilder)). Utgå därför från att automatiserad insamling är förbjuden tills villkoren lästs.

Den tredje delen är upphovsrätten till foton, som gäller automatiskt ([PRV](https://www.prv.se/sv/upphovsratt/for-anvandare/upphovsratt-pa-bilder/)).

Dataintrång (BrB 4:9 c) kräver att man tar sig in "olovligen" ([lagen.nu](https://lagen.nu/begrepp/Dataintr%C3%A5ng)). Ingen dom gör läsning av öppna sidor olovlig, men att kringgå CAPTCHA, blockeringar eller inloggning förskjuter bedömningen. Ingen svensk dom om skrapning av annonssajter hittades. Närmast är PMÖD B 9256-18, där en läkare som laddat ner en katalogskyddad databas friades eftersom han hade rätt att ta del av uppgifterna ([PMÖD](https://www.domstol.se/patent--och-marknadsoverdomstolen/patent--och-marknadsoverdomstolens-avgoranden/2019/59130/)). Det realistiska utfallet för en småskalig privat aktör är blockering, kontoavstängning eller ett varningsbrev, inte en process. Ett avstängt Vend-konto kan dock slå mot inloggningen på alla Vend-sajter, eftersom Blocket-kontot numera är ett Vend-konto ([Blocket hjälpcenter](https://blocket.zendesk.com/hc/sv/articles/360000829179-Jag-har-ett-Blocket-konto-Schibsted-Marketplaces-konto-Hur-kan-jag-f%C3%A5-tillg%C3%A5ng-till-de-personuppgifter-ni-har-om-mig)).

| Insamlingsväg | Rättslig risk | Risk för kontoavstängning | Hastighet | Roll i planen |
|---|---|---|---|---|
| Android-push från bevakningar, vidarebefordrad till backend | Låg | Mycket låg | Minuter (overifierat) | **Primär, testas vecka 1** |
| Manuell "dela länk" till bot/webb | Låg | Mycket låg | Direkt när du ser annonsen | Primär reserv |
| Webbläsartillägg som passivt läser sidor du själv öppnar | Låg–måttlig | Låg | Beror på dig | Fas 2 |
| Bevakningsmejl parsade i Gmail | Låg | Mycket låg | En gång per dygn | Skyddsnät och täckningsmätning |
| Hämta *enskild* annonssida på begäran efter push eller delning | Låg–måttlig | Låg | Sekunder | Ingår, med hård hastighetsgräns |
| Agent i inloggad session som pollar 3–10 sökningar var 5–15 min | Måttlig (avtalsbrott) | Måttlig | 5–15 min | Endast efter beslutspunkt i fas 3 |
| Bred skrapning av hela möbelkategorin | Måttlig–hög | Hög | 1–5 min | **Byggs inte** |
| Fullständig spegling av Auctionets slutpriser och bilder | Hög | (IP-blockering) | – | **Byggs inte** |

Riskbedömningen i tabellen bygger på forskningsanteckningarnas analys av ovanstående källor. Den är min egen sammanvägning, inte en prövad rättslig slutsats.

### Prisdatan: välj ut, skriv av fakta och spara inga bilder

Auctionets slutpriser är det mest värdefulla underlaget och samtidigt det som är starkast skyddat som databas. Auctionet har ingen känd publik API ([Brite/Auctionet](https://britepayments.com/fr/temoignages/auctionet/)). Den lagligt renaste prisdatabasen består av dina egna köp och försäljningar plus slutpriser som du manuellt noterar för de modeller du faktiskt följer: tiotals eller hundratals rader, med datum, klubbslag, skick och länk. Enskilda fakta skyddas inte. Risken uppstår först om du tar ut en väsentlig del av databasen.

Tradera har ett officiellt utvecklarprogram med en kvot på **10 000 anrop per dygn och metod** ([Tradera Developer Program](https://api.tradera.com/)). Det är det enda lagliga API-alternativet, men det är oklart hur mycket avslutade objekt med slutpris det exponerar. Ett tredje alternativ är att helt enkelt fråga Auctionet om export eller licens för en liten, icke-konkurrerande användning.

Bilder kräver särskild försiktighet. Att räkna fram embeddings från auktionsfoton för en intern likhetssökning kan rymmas i TDM-undantaget (URL 15 a §, art. 4 i DSM-direktivet), som uttryckligen omfattar även databasrätten, förutsatt att ingen maskinläsbar reservation finns ([DSM-direktivet](https://eur-lex.europa.eu/legal-content/SV/TXT/?uri=CELEX:32019L0790)). OLG Hamburg fann i december 2025 i Kneschke mot LAION att ett förbehåll i naturligt språk i villkoren inte räckte som maskinläsbar reservation ([Bird & Bird](https://cm.twobirds.com/en/insights/2025/germany/higher-regional-court-hamburg-confirms-ai-training-was-permitted-(kneschke-v,-d-,-laion))). Domen är tysk och kan överklagas. Säkraste mönstret är att spara vektor, id, slutpris och länk men radera bilden. Återanvänd aldrig någon annans foto när du säljer vidare.

Dina egna böcker hanteras på samma sätt. Extrahera *fakta* (modell, år, tillverkare, märkning, kännetecken, kända kopior) till bevakningslistan och spara inte inskanningar varaktigt. Undantaget för privat bruk (12 § URL) är tveksamt när syftet är vidareförsäljning. Det är min bedömning och ingen källa prövar frågan.

GDPR gäller fullt ut, eftersom privatundantaget inte omfattar näringsverksamhet. Spara annons-id, titel, pris, kategori och ort på kommunnivå, men aldrig säljarens namn eller telefonnummer, och gallra efter en kort tid.

### Bedömning: Android-vidarebefordran av Blockets push är rätt första spik

Idén att låta en notification listener på din egen Android-telefon (Tasker med ett notisplugin för en snabb test, eller en egen liten Kotlin-app med Androids `NotificationListenerService`) fånga Blockets bevakningspush och posta den till backend är den mest hävstångsstarka och minst riskabla insamlingsvägen i hela upplägget.

Den har fyra styrkor. Den använder Blockets snabbaste officiella kanal. Den skapar ingen trafik mot Blocket utöver den du själv redan genererar, eftersom datan levereras till dig. Den kostar nästan ingenting. Och den låter Blockets sökmotor sköta grovfiltreringen, så att volymen in till din pipeline blir hanterbar: tiotals till ett par hundra annonser per dag i stället för tiotusentals.

Den har också fyra svagheter, och alla är overifierade.

1. **Innehåll.** Det är okänt om notisen innehåller titel, pris och annons-id/URL eller bara "ny annons i bevakning X". Länken i en Android-notis ligger normalt i en ogenomskinlig PendingIntent som en listener inte kan läsa som URL. Det är generell Android-kunskap, inte källbelagt.
2. **Hastighet.** Den verkliga latensen efter plattformsbytet är okänd.
3. **Gränser.** Det är okänt hur många bevakningar ett konto får ha. Hjälpcentret beskriver var de hanteras men anger ingen gräns ([Blocket hjälpcenter](https://blocket.zendesk.com/hc/sv/articles/31351437749650-Hur-ser-jag-alla-mina-bevakningar)).
4. **Driftsäkerhet.** Androids batterioptimering kan döda lyssnaren, grupperade notiser kan dölja enskilda annonser och appuppdateringar kan ändra formatet.

Spiken avgörs därför under vecka 1 med ett enkelt test. Logga alla Blocket-notiser i en vecka och jämför med vad som faktiskt publicerades.

Om notisen innehåller titel och pris men inte länk finns en fungerande halvmanuell väg. Backend gör en snabb förbedömning enbart på text. Om annonsen ser lovande ut får du en Telegram-notis "öppna och dela". Ett tryck i Blocket-appen och sedan "Dela" till din bot ger länken. Därefter hämtar servern den enskilda annonssidan för full bildanalys. Om notisen innehåller länk går hela kedjan automatiskt. Om notisen är innehållslös eller kommer mer än 30 minuter efter publicering faller idén, och du går tillbaka till delningsflödet plus webbläsartillägget.

## En server, en databas och en Telegram-bot räcker till MVP:n

Eftersom Blockets bevakningar gör grovfiltreringen behövs varken vektordatabas, egen embedding-modell eller schemalagd polling i första versionen. Det är den viktigaste förenklingen jämfört med forskningsanteckningarnas fullskaliga fyrstegstratt. Med kanske 50–200 inkommande annonser per dag (antagande, mät!) kan varje annons gå direkt till Haiku 5.5 med 3–4 nedskalade foton, annonstexten och ett utdrag ur bevakningslistan. Claude räknar bildkostnaden som ⌈bredd/28⌉ × ⌈höjd/28⌉ tokens, så en bild på 784 × 784 px blir 784 tokens ([Claude Vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)). Ett anrop med fyra bilder och text blir runt 4–5 tusen tokens, cirka **0,0006 USD**. Vid 200 annonser per dag blir det cirka 4 USD i månaden. Lägg till Sonnet 5.5 (2 USD/MTok in) som andra bedömare för de cirka tio bästa kandidaterna per dag, cirka 0,02 USD per anrop, så blir hela AI-kostnaden fortfarande under 100 SEK i månaden ([Anthropic](https://platform.claude.com/docs/en/about-claude/pricing)).

Vision-modellen får dock inte namnge formgivare fritt. Claude kan hallucinera på små, suddiga eller roterade bilder ([Claude Vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)), och VLM:er har starka förväntningar mot ikonerna. Modellen ska därför välja bland konkreta kandidater från bevakningslistan, där kända kopior och liknande anonyma modeller finns med som avsiktliga lockbeten, ha "NONE" som giltigt svar, lista motbevis före beslut och svara i strikt JSON. Värderingen och marginalberäkningen sker sedan deterministiskt i kod. LLM:en identifierar men räknar aldrig pengar.

Embeddings väntar till fas 3 och bara om bredare insamling motiverar dem. Underlaget avråder från att lita på zero-shot-embeddings ensamma: DINOv2-Large når bara **40 % P@1** på ett IKEA-möbeldataset i en tredjepartsbenchmark ([nyris](https://vpsbenchmark.nyris.io/models/facebook_dinov2-large)). När det blir aktuellt räcker SigLIP 2 plus pgvector i samma Postgres-databas.

| Komponent | Val i MVP | Ungefärlig kostnad/mån | Källa och osäkerhet |
|---|---|---|---|
| Server | 1 liten EU-VPS (t.ex. Hetzner CAX11, 2 vCPU ARM) med Docker Compose | ca 66 SEK (€5,99) | Pris efter höjning i juni 2026 ([privatedevops](https://privatedevops.com/news/hetzner-june-2026-cloud-price-increase-what-to-do)); tillgången rapporterades begränsad i augusti ([findstack](https://www.findstack.com/resources/hetzner-price-increase-2026)), välj annan EU-VPS vid behov |
| Databas | SQLite (WAL) och nattlig backup till objektlagring | ca 0–20 SEK | Egen bedömning; byt till Postgres + pgvector först i fas 3 |
| Inloggning | Cloudflare Tunnel + Access med e-post-PIN eller Google | 0 SEK | Gratis under 50 användare ([Cloudflare](https://www.cloudflare.com/en-au/products/cloudflare-access)) |
| Push | Telegram-bot med foto, text och knappar | 0 SEK | Generell kunskap om Bot API, ej omverifierad; reserv: Pushover, 4,99 USD engång ([Pushover](https://pushover.net/pricing)) |
| AI | Haiku 5.5 för alla, Sonnet 5.5 för toppkandidater, hårt dagstak i kod | ca 50–300 SEK | [Anthropic](https://platform.claude.com/docs/en/about-claude/pricing); volymen är ett antagande |
| Domän | Egen domän via Cloudflare | några tiotal SEK | Ej källbelagt |
| **Totalt** | | **ca 200–600 SEK** | Resten av budgeten är buffert, inte mål |

Cloudflare Access ger privat inloggning utan en rad egen auth-kod. Webhookvägarna för telefonen, webbläsartillägget och Telegram måste dock undantas från Access och i stället skyddas med en egen hemlig token. iOS PWA-push har motstridiga uppgifter om EU-status och rapporteras instabil ([MagicBell](https://www.magicbell.com/blog/pwa-ios-limitations-safari-support-complete-guide); [webscraft](https://webscraft.org/blog/pwa-pushspovischennya-na-ios-u-2026-scho-realno-pratsyuye?lang=en)). Det talar för Telegram som pushkanal och webben som inkorg, inställningar och historik.

Filtreringen på marginal och geografi är ren kod. Förväntat nettovärde beräknas som P25 av jämförbara slutpriser × nettokvot (standard 0,78) − fasta avgifter − transport (fast belopp + kr/km × avstånd t/r från en kommuncentroid till din hemort) − uppskattad renovering − begärt pris. Larm skickas om nettot överstiger ditt minimum i kronor, avkastningen överstiger ditt minimum i procent, avståndet ligger inom din radie eller valda län och säkerheten är minst "medel". Fall med låg säkerhet men stor möjlig uppsida går i en separat, tystare kanal ("kolla själv").

## Fyra hinder avgör om verktyget betalar sig

**Möjligheterna är verkliga men smala.** Marknaden är het 2026, och ingen kommersiell "Swoopa för Blocket" hittades; svenska motsvarigheter är hobbyskrapor och Apify-aktörer ([GitHub topic: blocket](https://github-redirect.dependabot.com/topics/blocket); [Apify](https://apify.com/fervent_bus/blocket-scraper)). Amerikanska motsvarigheter som Flipify konkurrerar på larm inom sekunder och vinstestimat från sålda jämförelseobjekt ([Capterra](https://www.capterra.com/p/10050498/Flipify/)). Det bekräftar receptet: snabbhet plus jämförelse mot slutpriser. Din fördel är domänkunskap och böcker som ingen generell app har. Kunskapen kodas in i bevakningslistan, som blir verktygets egentliga tillgång. Koden går att byta ut, men listan bär värdet. Konkurrensen om fynden avgörs ändå av vem som ringer först. Snabbhet slår precision, och ett larm som kommer en timme sent är i praktiken värdelöst för eftertraktade objekt.

| Hinder | Varför det är allvarligt | Hur vi tar oss över |
|---|---|---|
| **Insamlingslatens och åtkomst** | Bevakningspush kan vara långsam eller innehållslös efter plattformsbytet; bred skrapning är juridiskt och tekniskt dyr | Mät push vecka 1; delningsflöde som reserv; webbläsartillägg i fas 2; inloggad lågfrekvent pollning bara efter medvetet beslut i fas 3 |
| **Gles prisdata** | Inga verifierade svenska prisintervall för mellanskiktet; utan jämförelseobjekt blir marginalen gissning | Handkurerad lista med 50–150 modeller och 3–10 slutpriser var, byggd under vecka 1–4; krympning mot formgivare × kategori vid färre än 5 jämförelseobjekt; egen affärsliggare som matar tillbaka verkliga utfall |
| **Felattribution och replikor** | VLM:er överskattar ikoner; licensproduktion och kopior ser rätt ut på mobilfoto | Kandidatbaserad verifiering med lockbeten, "NONE" som svar, motbevis före beslut, standardfrågan "foto av undersidan", nedgradering på stil-ord |
| **Avgifter och tid** | 0,75–0,8 nettokvot plus frakt och renovering; 2–8 veckor till utbetalning (overifierat) | Konservativ P25-värdering, hård minsta marginal i kronor, liggare över faktisk tid per affär, alternativa säljkanaler (Tradera, Blocket) per objekt |

Två risker ligger utanför tabellen. Den första är plattformsrisk: Blocket kan ändra notisformat eller appbeteende utan förvarning, som i november 2025. Den andra är självbedrägeri: det är lätt att mäta "antal larm" i stället för kronor i vinst. Båda hanteras med samma disciplin, nämligen en hälsokontroll som larmar när en källa tystnar och en affärsliggare som är enda sanningen om lönsamheten.

Det starkaste motargumentet mot hela projektet ska också tas på allvar. Blockets egna bevakningar, din erfarenhet och fem minuters manuell granskning per dag kanske räcker. Verktyget måste därför bevisa sitt mervärde mot den nollhypotesen, vilket kill-kriterierna nedan gör explicit.

## Fasplan med mätbara mål och kill-kriterier

Målnivåerna nedan är mina förslag, satta utifrån budgeten och osäkerheten i underlaget. Inget av dem är källbelagt branschmått. Justera dem efter vecka 2, när du har egen data.

| Fas | Leverans | Mätbart mål | Kill- eller pivotkriterium |
|---|---|---|---|
| **Vecka 1: spikar, ingen server** | 20–30 bevakningar (formgivare, tillverkare, modellnamn plus vaga ord som "retro fåtölj", "dödsbo", "teak" med prisgräns); Tasker/notislogg på telefonen; läs Blockets och Auctionets villkor och robots.txt; bevakningslista v0 med 30 modeller och slutpriser | Median-latens push → publicering uppmätt på ≥ 30 notiser; dokumenterat notisinnehåll | Om push saknar både titel och pris *eller* latensen är > 30 min: stryk Android-vägen, kör dela-länk + tillägg |
| **Vecka 2: kärnflödet** | VPS, Cloudflare Access, `/ingest`-endpoints, hämtning av enskild annons, Haiku-bedömning, deterministisk marginal och avstånd, Telegram-larm med knappar | ≥ 90 % av inkomna annonser bedömda inom 60 s; AI-kostnad loggad per anrop | Om pipelinen inte är stabil efter 2 veckors kvällsarbete: förenkla (släpp bilder, kör bara text) |
| **Vecka 4: kalibrering** | Märkt testset med ≥ 100 annonser; `eval`-skript; bevakningslista v1 med 80–150 modeller; affärsliggare i webben | Precision ≥ 30 % på larm ("värt att öppna"); ≥ 3 handlingsbara larm/vecka; ≥ 1 köp | Precision < 15 % eller 0 handlingsbara larm på 2 veckor: verktyget är brus, pausa |
| **Vecka 8: lönsamhet** | Webbläsartillägg (passiv läsning); Gmail-parsning som skyddsnät; veckorapport | Realiserad nettovinst ≥ 3 000 kr/mån i snitt; ≥ 2 affärer med positiv marginal; driftkostnad < 10 % av vinsten | **Kill:** < 1 lönsam affär på 8 veckor, eller vinst < driftkostnad + 20 tim egen tid × ditt timpris |
| **Vecka 12+: utbyggnad (bara om vecka 8 klaras)** | Beslut om lågfrekvent pollning i egen session; SigLIP 2 + pgvector om insamlingen breddas; Tradera-API för jämförelseobjekt | Vinst ≥ 5 000 kr/mån; täckningsmätning: andel fynd du hittat manuellt som verktyget missade < 30 % | Om vinsten inte växer med bredare insamling: frys på vecka-8-nivån |

Effektiviteten ska mätas som **kronor realiserad nettovinst per månad**, inte som antal larm. Precision på larm (andel du själv bedömer som värda att öppna) och fynd per vecka är styrsignaler. Varje knapptryck i Telegram ("Köpt", "Ej intressant", "Fel modell", "Replika", "Bra men såld") blir en märkt datapunkt för testsetet.

## Detta måste verifieras innan och under bygget

| Punkt | Varför | Hur |
|---|---|---|
| Blockets användarvillkor och robots.txt (efter november 2025) | Avgör avtalsrisken för hämtning av enskilda sidor och eventuell pollning | Läs manuellt i webbläsare; spara kopia med datum |
| Innehåll och latens i Blocket-push | Bärande antagande för hela ingest-designen | Notislogg i en vecka |
| Max antal bevakningar per konto; om e-post fortfarande bara skickas en gång per dygn | Påverkar täckning och skyddsnät | Testa i appen; hjälpcenter |
| Auctionets villkor, robots.txt och eventuell TDM-reservation | Avgör om embeddings från auktionsfoton är tillåtna | Läs manuellt; fråga Auctionet om licens |
| Aktuella avgiftstabeller hos de hus du tänker sälja via | Nettokvoten 0,75–0,8 är en uppskattning | Begär prislista; kalibrera mot första avräkningen |
| Prisintervall per modell för mellanskiktet | Inga verifierade källor finns i underlaget | Auctionets avslutade objekt per formgivare, manuellt |
| VPS-pris och tillgång, Claude-modell-id | Leverantörssidor kunde inte hämtas (Hetzner) eller kan ändras | Kontrollera vid beställning; gör modellnamn konfigurerbara |
| Traderas API för avslutade objekt | Möjlig laglig källa till jämförelseobjekt | Skapa utvecklarkonto och testa |

## Product requirements prompt för MVP:n

Prompten nedan kan klistras in som första meddelande till en AI-kodassistent (t.ex. Claude Code) i ett tomt repo. Den följer valen ovan och kodar in de juridiska skyddsräckena som krav.

```text
# Uppdrag: Bygg MVP:n "Fyndjakt" – intern larmtjänst för undervärderade skandinaviska designmöbler på Blocket

Du är min kodassistent. Jag köper och säljer designmöbler privat i liten skala. Bygg en lean, intern
webbtjänst för 1 användare (max 3). Principen är "lean and mean": få rörliga delar, inga tjänster
som inte behövs, inget som inte stödjer målet "fler lönsamma köp per månad". Fråga mig hellre än att
gissa när ett krav är oklart. Skriv all UI-text på svenska; kod, identifierare och kommentarer på engelska.

## Mål och icke-mål
MÅL: När en ny Blocket-annons som matchar mina bevakningar dyker upp ska tjänsten inom 60 sekunder
(1) identifiera om möbeln sannolikt är en modell på min bevakningslista, (2) uppskatta andrahandsvärde
från mina sparade jämförbara slutpriser, (3) räkna fram förväntad nettomarginal och avstånd, och
(4) skicka ett Telegram-larm bara om mina trösklar uppfylls.
ICKE-MÅL i MVP: bred skrapning av Blocket eller Auctionet, schemalagd pollning av sökresultat,
vektordatabas/embeddings, egen ML-träning, flera användare med roller, mobilapp (utöver den lilla
Android-lyssnaren), andra kategorier än möbler.

## Juridiska och etiska skyddsräcken (hårda krav)
- Tjänsten får ALDRIG crawla sök- eller kategorisidor. Den får bara hämta en ENSKILD annonssida när
  en URL kommit in via mina egna kanaler (push, delning, tillägg).
- Hastighetsgräns: max 60 annonshämtningar per timme och max 1 samtidig; ärlig User-Agent; vid 403/429:
  exponentiell backoff och larma mig, försök ALDRIG kringgå CAPTCHA, blockering eller inloggning,
  ingen proxy- eller IP-rotation.
- Lagra aldrig säljares namn, telefonnummer eller profil-id. Spara annons-id, URL, titel, pris,
  beskrivning, kategori, ort/kommun, publiceringstid.
- Bilder: ladda ner max 4 per annons, nedskala till längsta sida 784 px för LLM, radera lokala kopior
  efter 7 dagar (konfigurerbart). Spara bild-URL:er. Visa aldrig auktionshusens bilder i UI annat än som länk.
- Jämförelseobjekt (comps) matas in manuellt eller via CSV av mig; bygg ingen Auctionet-skrapa.

## Stack (välj inte annat utan att fråga)
- Python 3.12, uv, ruff, pytest. FastAPI + Jinja2 + HTMX (ingen SPA, inget npm-bygge).
- SQLite i WAL-läge via SQLAlchemy 2 + Alembic. Designa schemat så att byte till Postgres är trivialt.
- Anthropic Python SDK. Modellnamn i config: MODEL_FAST (Haiku 5.5) och MODEL_STRONG (Sonnet 5.5).
  Verifiera exakta modell-id:n i Anthropics dokumentation innan du hårdkodar standardvärden.
- Telegram Bot API (webhook) för push.
- Docker Compose med tjänsterna: app (web + worker i samma process med en enkel asynkron jobbkö
  i SQLite-tabell), cloudflared (Cloudflare Tunnel). Ingen Redis, ingen Celery.
- Driftmiljö: en liten EU-VPS. Cloudflare Access skyddar allt UTOM /ingest/* och /telegram/webhook,
  som skyddas med hemliga tokens i header (INGEST_TOKEN, TELEGRAM_WEBHOOK_SECRET).
- Hemligheter i .env (aldrig i repo). Nattlig backup av SQLite-filen till S3-kompatibel lagring.

## Datamodell (minimum)
- listings: id, source ('blocket'), external_id (unik), url, title, price_sek, description, municipality,
  lat, lon, published_at, received_at, ingest_channel ('android_push'|'share'|'extension'|'email'),
  raw_notification (text), status.
- listing_images: listing_id, url, local_path (nullable), width, height, sharpness, deleted_at.
- models (bevakningslistan): id, designer, manufacturer, model_name, period, category, aliases (lista),
  identifying_features (text), replica_traps (text: kända kopior, licensproduktion och hur de skiljs åt),
  marks (text: stämplar/etiketter), reference_image_urls (lista, valfri), active.
- comps: id, model_id, source ('auctionet'|'bukowskis'|'tradera'|'own_sale'|'other'), sold_at,
  hammer_sek, condition ('utmärkt'|'gott'|'slitet'|'renoveringsobjekt'), url, note.
- assessments: listing_id, model_candidate_id (nullable), match ('yes'|'uncertain'|'no'),
  evidence, contradictions, replica_signals, label_ocr, condition_guess, needs_underside_photo,
  value_p25, value_median, value_p75, n_comps, value_level ('model'|'designer_category'|'none'),
  transport_sek, net_margin_sek, roi, distance_km, confidence ('låg'|'medel'|'hög'), llm_model,
  tokens_in, tokens_out, cost_usd, created_at.
- feedback: listing_id, label ('köpt'|'ej_intressant'|'fel_modell'|'replika'|'bra_men_såld'), created_at.
- deals (affärsliggare): listing_id (nullable), model_id, bought_at, buy_price, transport_cost,
  repair_cost, sold_at, sale_channel, sale_price_gross, fees, net_result, hours_spent, note.
  Sålda affärer ska automatiskt kunna bli en comps-rad (source='own_sale').
- settings: home_lat, home_lon, max_distance_km, allowed_regions (lista län), min_net_margin_sek
  (standard 1500), min_roi (standard 0.5), net_ratio (standard 0.78), fixed_fees_sek (standard 500),
  transport_base_sek (standard 300), transport_sek_per_km (standard 3.0), daily_ai_budget_usd
  (standard 1.0), quiet_hours.
- ai_calls: tidsstämpel, modell, tokens, kostnad (för budgetvakt).

## Ingest
1. POST /ingest/notification – från Android (Tasker eller egen app). Body: package, title, text,
   big_text, posted_at, eventuell url. Spara rått. Försök extrahera titel, pris, ort, URL och annons-id
   med regex. Har vi URL: köa hämtning. Saknas URL: kör textförbedömning (steg 2–3 nedan, utan bilder)
   och om score är över tröskel skicka Telegram "Öppna och dela till boten" med titel och pris.
2. Telegram: när jag delar/klistrar en Blocket-URL till boten → köa hämtning + full bedömning.
3. POST /ingest/listing – från webbläsartillägg (fas 2) med URL och sidans strukturerade data; samma flöde.
4. Webbformulär "Lägg till annons" (klistra in URL).
5. Deduplicera på external_id; samma annons bedöms bara en gång (ombedömning endast vid prisändring).

## Hämtning av enskild annons
Hämta sidan med httpx. Leta först efter strukturerad data (JSON-LD eller inbäddad JSON) och extrahera
titel, pris, beskrivning, ort, bilder, publiceringstid. Om det misslyckas: skicka sidans synliga text
(max 8 000 tecken) till MODEL_FAST med ett extraktionsschema. Skriv parsern så att den är lätt att
uppdatera, och lägg sparade HTML-fixtures i tests/fixtures för deterministiska tester.
Hälsokontroll: om 3 hämtningar i rad misslyckas → Telegram-larm "Källan trasig".

## Bedömningspipeline (en funktion per steg, alla testbara)
1. Normalisering + bildkvalitet: mät upplösning och skärpa (Laplacian-varians), välj bästa helbild och
   bästa detaljbild.
2. Deterministiska textregler: matcha mot models.aliases, designer, manufacturer; plussignaler
   ("stämplad", "märkt", tillverkarnamn); minussignaler som sänker confidence ett steg och sätter
   replica-flagga: "replika", "kopia", "i stil med", "à la", "inspirerad av", "typ", "-stil".
   Välj ut max 8 kandidatmodeller (textmatch först, annars samma kategori). Lägg ALLTID till
   replica_traps-text för kandidaterna i prompten.
3. LLM-verifiering med MODEL_FAST: bilder först ("Image 1:", ...), sedan annonstext och kandidatlista.
   Instruera: välj kandidat-id eller NONE, lista konkreta visuella bevis, lista motbevis FÖRE beslut,
   läs av etiketter/stämplar, ange om foto av undersidan behövs. Tvinga strikt JSON via tool use.
   Använd prompt caching för den fasta instruktionen.
4. Värdering (ren kod, ingen LLM): hämta comps för vald modell; justera för skick med multiplikatorer
   (utmärkt 1.0, gott 0.85, slitet 0.7, renoveringsobjekt 0.55 – konfigurerbart) och tid (konfigurerbar
   årlig trend, standard 0). Om n_comps ≥ 5: P25/median/P75 på modellnivå. Om 1–4: krymp i log-pris
   mot medianen för designer × kategori. Om 0: value_level='none' → inget marginallarm, bara "kolla själv"
   om det är en bevakad formgivare.
5. Geografi: slå upp kommun → centroid (lägg med en CSV över Sveriges 290 kommuner med lat/lon från
   öppen data; fråga mig om licensen är oklar). distance_km = haversine från hemmet.
   transport_sek = transport_base_sek + transport_sek_per_km × 2 × distance_km.
6. Marginal: net_margin_sek = value_p25 × net_ratio − fixed_fees_sek − transport_sek − price_sek.
   roi = net_margin_sek / max(price_sek, 1).
7. Eskalering: om match ∈ {yes, uncertain} och net_margin_sek ≥ 2 × min_net_margin_sek, kör samma
   bedömning med MODEL_STRONG. Om de två är oense → confidence='låg'.
8. Larmbeslut: skicka "FYND" om net_margin_sek ≥ min_net_margin_sek OCH roi ≥ min_roi OCH
   (distance_km ≤ max_distance_km ELLER län i allowed_regions) OCH confidence ≥ 'medel'.
   Skicka "KOLLA SJÄLV" (tyst notis) om bevakad modell/formgivare men confidence='låg' eller
   value_level='none' och potentiell uppsida är stor. Inget annat skickas. Respektera quiet_hours
   utom för FYND.
9. Budgetvakt: logga varje AI-anrop med kostnad; om dagens kostnad ≥ daily_ai_budget_usd körs bara
   steg 1–2 + text-only-larm och jag får ett meddelande.

## Telegram-larm
Foto (bästa helbilden) + bildtext: titel, begärt pris, uppskattat värde "P25–P75 (median), n=X",
förväntad nettomarginal i kr och ROI, avstånd och ort, confidence, kandidatmodell, 1–2 bevis och
1 motbevis, ev. "Be om foto av undersidan". Knappar: [Öppna annons] [Köpt] [Ej intressant]
[Fel modell] [Replika] [Bra men såld]. Knapptryck → feedback-rad och redigera meddelandet till "hanterad".

## Webb-UI (bakom Cloudflare Access)
- /inkorg: senaste bedömda annonser, sorterbara på marginal/score, filter på larmtyp.
- /annons/{id}: alla fält, bilder (från Blocket-URL), bedömning, LLM-JSON, comps som använts.
- /bevakningslista: CRUD för models och comps + CSV-import/export (kolumnerna dokumenterade i README).
- /installningar: alla settings ovan.
- /affarer: affärsliggaren med summering per månad (nettoresultat, timmar, kr/timme).
- /statistik: larm/vecka, precision (andel larm med feedback ≠ ej_intressant/fel_modell/replika),
  köp/månad, realiserad vinst/månad, AI-kostnad/månad, latens notis→larm (median, p90),
  andel annonser per ingest-kanal.
- /health (öppen, ingen data): senaste lyckade ingest per kanal.

## Android-lyssnare (separat mapp android/, fas 1b)
Vecka 1 använder jag Tasker för att logga notiser. Skriv dessutom en minimal Kotlin-app med
NotificationListenerService som filtrerar på Blockets paketnamn (konfigurerbart), postar
title/text/bigText/postTime och ev. URL till /ingest/notification med INGEST_TOKEN, köar lokalt vid
nätfel och visar en enkel status (senast skickad, antal fel). Dokumentera hur man undantar appen från
batterioptimering. Ingen annan funktionalitet.

## Utvärdering
- tests/: enhetstester för regex-extraktion, textregler, värdering, marginal, larmbeslut (rena
  funktioner, inga nätverksanrop), samt parser-tester mot HTML-fixtures.
- eval/: ett skript `uv run python -m eval.run` som kör pipelinen mot en märkt CSV (listing_url eller
  sparad fixture, facit: model_id|NONE, värt_att_öppna: ja/nej) och skriver precision@larm, recall på
  kända positiva, falska positiva per typ (replika, fel modell), kostnad och latens. Varje promptändring
  ska köras mot eval innan merge.

## Leveransordning och acceptanskriterier
M1 (vecka 2): ingest via notis/dela/formulär, hämtning, pipeline steg 1–8, Telegram-larm, inkorg,
  inställningar, budgetvakt, Docker Compose + cloudflared, README med driftsättning.
  Klart när: en delad Blocket-URL ger ett korrekt formaterat larm eller ett loggat "inget larm"
  inom 60 s, och alla tester är gröna.
M2 (vecka 4): bevakningslista med CSV-import, affärsliggare, statistik, eval-skript, Android-app.
  Klart när: eval kan köras på ≥ 100 märkta annonser och statistiksidan visar precision och vinst.
M3 (vecka 8): webbläsartillägg (Manifest V3) som PASSIVT läser Blocket-annonssidor jag själv öppnar och
  postar till /ingest/listing; Gmail-parsning av bevakningsmejl som skyddsnät. Tillägget får inte öppna
  flikar, ladda om sidor eller navigera på egen hand.

## Arbetssätt
- Skapa CLAUDE.md med kommandon, konventioner och skyddsräckena ovan.
- Små commits, en funktion i taget, tester först för de rena funktionerna.
- Fråga mig innan du lägger till ett nytt beroende, en ny tjänst eller någon form av automatisk hämtning
  som inte står i detta dokument.
- Börja med att visa mig ett förslag på mappstruktur och databasschema innan du skriver kod.
```

## Slutsats

Den avgörande insikten är att den lönsamma delen av projektet inte är tekniken utan kunskapen. AI-kostnaden blir försumbar när Blockets egna bevakningar får göra grovfiltreringen, och juridiken blir hanterbar när du låter bli att bygga en skrapa. Kvar blir två saker som bara du kan leverera: en bevakningslista som kodar in var säljare inte vet vad de har, och en affärsliggare som visar om det faktiskt blir pengar. Bygg därför verktyget som en förstärkning av din egen bedömning, med ett larm som säger "titta här, det här talar emot, be om undersidan", och inte som en automatisk köpmaskin.

Den största öppna frågan avgörs redan vecka 1: hur snabb och innehållsrik Blockets push är efter november 2025. Svaret styr hela insamlingsdesignen. Om pushen håller blir tjänsten en av de billigaste och renaste fyndmotorer som går att bygga. Om den inte håller är rätt reaktion att luta sig tyngre mot delningsflödet och tillägget, inte att börja skrapa. Hela nyttan ligger i att vara först på annonser som Blocket själv redan skickar till dig, och en skrapa skulle ge minimalt extra värde till en avsevärt högre risk.
