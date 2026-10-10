# Juridik och dataåtkomst: Blocket-bevakning + Auctionet-slutpriser för intern fyndjakt (läge okt 2026)

> Metodnot: Researchen gjordes 2026-10-10. Sökning fungerade, men direkthämtning (WebFetch/curl) mot blocket.se, auctionet.com, tradera.com, bukowskis.com, auktionsverket.se, lagen.nu, svt.se och blocket.zendesk.com blockerades av miljöns proxy. **Robots.txt och de fullständiga användarvillkoren kunde därför inte läsas ordagrant för någon av sajterna.** Påståenden om deras innehåll bygger på sökresultat och sekundärkällor, och bör kontrolleras manuellt innan något byggs. Länkar till EUR-Lex och curia för EU-domar och direktiv är kanoniska primärkällor som inte hämtades i denna session; sammanfattningarna stöds av de sekundärkällor som anges. Detta är en riskbedömning, inte juridisk rådgivning.

## 1. Blocket: villkor, officiella kanaler, bevakningar och plattformsbytet

### Takeaway
Blocket har ingen känd publik API, RSS eller partnerfeed för privatpersoner. Den enda officiella "push"-kanalen är bevakningar: push i appen kommer kort efter publicering, e-post en gång per dag. Blocket bytte till en ny plattform byggd på Finn/Vend-teknik den 18 november 2025, och gamla bevakningar och söklogik gick förlorade eller ändrades. Villkorens ordalydelse om robotar och skrapning kunde inte verifieras i denna session.

### Cited Findings
- **Bevakningar (officiellt hjälpcenter):** Man namnger sökningen och väljer e-post- eller pushnotis. **Push kommer kort efter att en matchande annons publicerats, medan e-post skickas en gång per dag.** Notiser kan också stängas av helt. — [Blocket hjälpcenter: Bevakningar](https://blocket.zendesk.com/hc/sv/articles/22875498207506-Bevakningar) (enligt sökutdrag; sidan kunde inte hämtas)
- En nyare hjälpartikel säger att e-post för närvarande skickas per aktiv bevakning, så flera bevakningar ger flera mejl. Inställningar finns under Mitt Blocket > Bevakningar > Notisinställningar. — [Blocket hjälpcenter: Hur ser jag alla mina bevakningar?](https://blocket.zendesk.com/hc/sv/articles/31351437749650-Hur-ser-jag-alla-mina-bevakningar); se även [Hej nya Blocket!](https://blocket.zendesk.com/hc/sv/articles/30074390858514-Hej-nya-Blocket)
- Pushnotiser för bevakningar lanserades i appen för cirka tio år sedan (äldre pressmeddelande). — [Mynewsdesk/Blocket](https://www.mynewsdesk.com/se/blocket/news/blocket-goer-det-laettare-att-komma-foerst-till-kvarn-pushnotiser-lanseras-i-appen-150739)
- **Plattformsbytet:** Blocket lanserade sin nya sajt den 18 november 2025. Den bygger på samma teknik som norska Finn, och Blocket har sagt att den gamla versionen inte kommer tillbaka. — [Carup](https://carup.se/nya-blocket-far-bilforsaljningen-att-rasa/); [Foretagande.se](https://foretagande.se/blockets-nya-sajt-far-stark-kritik-helt-kass)
- Realtid rapporterar att "bevakningar, favoriter, söklogik – ingenting av det gamla finns kvar". Både Realtid och Dagens PS skriver att bevakningarna inte fungerar som förut. En Facebookgrupp mot förändringen har över 22 000 medlemmar (via SvD). — [Realtid](https://www.realtid.se/bors-finans/affarer/massprotest-mot-blocket-storflykt-till-konkurrenter/); [Dagens PS](https://www.dagensps.se/motor/rasar-mot-andringen-pa-blocket-allt-ar-bortblast/); [Realtid TV](https://www.realtid.se/realtidtv/nya-blocket-en-katastrof-for-bilhandlare/)
- Användare rapporterar att sparade bevakningar försvann och att det är svårt att se vilka bevakningar som fått nya annonser. — [SweClockers-forum "Nya Blocket 2025"](https://www.sweclockers.com/forum/trad/1749008-nya-blocket-2025); [Klocksnack](https://klocksnack.se/threads/nya-blocket.203826/) (forum, overifierat)
- **Bolagsstruktur:** Schibsted Marketplaces bytte namn till Vend Marketplaces ASA under Q2 2025. Bolagsstämman godkände namnbytet den 7 maj 2025. Blocket, FINN, Tori, DBA och Bilbasen behölls som lokala varumärken, och vd:n kopplade namnbytet till "a shared technology platform". Tori flyttades till den nordiska plattformen 2024. — [Vend: Schibsted Marketplaces becomes Vend](https://vend.com/news/schibsted-marketplaces-becomes-vend-a-new-name-for-a-smarter-future); [Inderes release](https://www.inderes.fi/releases/schibsted-asa-schaschb-name-change-to-vend-marketplaces-asa); [Wikipedia: Vend Marketplaces ASA](https://en.wikipedia.org/wiki/Vend_Marketplaces_ASA)
- Blocket-kontot är nu ett Vend-konto, och den registrerade kan ladda ner sina egna personuppgifter via Vend-kontot (gäller samtliga sajter med Vend-inloggning). — [Blocket hjälpcenter: personuppgifter](https://blocket.zendesk.com/hc/sv/articles/360000829179-Jag-har-ett-Blocket-konto-Schibsted-Marketplaces-konto-Hur-kan-jag-f%C3%A5-tillg%C3%A5ng-till-de-personuppgifter-ni-har-om-mig)
- Appens utvecklare anges som Schibsted Sverige AB i svenska App Store och som Vend Marketplaces AB i tyska. — [App Store SE](https://apps.apple.com/se/app/blocket-k%C3%B6p-s%C3%A4lj-begagnat/id323710525); [App Store DE](https://apps.apple.com/de/app/blocket/id323710525)
- **Villkor om användarinnehåll (äldre):** Enligt SVT gav Blockets villkor Blocket en "oinskränkt rätt att fritt förfoga över" användargenererat innehåll, inklusive annonsbilder, även efter att annonsen raderats. Stockholms tingsrätt gav Blocket rätt i en tvist om en annonsbild. Artikeln är flera år gammal. — [SVT: Blocket får sälja vidare dina annonsbilder](https://www.svt.se/nyheter/inrikes/blocket-far-salja-vidare-dina-bilder)
- **Klausuler om skrapning:** Tre riktade sökningar hittade ingen Blocket-specifik text om robotar, spindlar eller skrapning. Jämförbara svenska plattformar förbjuder uttryckligen automatisk insamling, till exempel Nordnet. — [Nordnet FAQ](https://www.nordnet.se/faq/ovrigt/regler-foer-scraping-och-automatisk-datainsamling)

### Inferences
- Blocket äger uppenbarligen breda rättigheter till annonsinnehållet, och Vend-plattformarna (Finn, DBA) har historiskt aktivt bot-skydd. Det är mycket sannolikt att nuvarande villkor förbjuder automatiserad insamling. Behandla det som ett förbjudet beteende tills motsatsen är verifierad.
- Den nya Finn-baserade plattformen gör sannolikt gammal skrapkod och gamla URL-mönster (till exempel äldre `blocket.se/annonser/...`-sökningar) obsoleta. Finn har en känd publik sök-API för partner/proffs, men det är okänt om Blocket erbjuder motsvarande.
- För arbitrage är push i appen den officiellt snabbaste kanalen (minuter). E-post en gång om dagen är för långsamt för fyndjakt på eftertraktad design, där bra objekt ofta säljs inom timmar.

### Gaps
- Blockets nuvarande användarvillkor ordagrant (klausuler om automatiserad åtkomst och vidareutnyttjande) och robots.txt: kunde inte hämtas.
- Om e-post-bevakningar efter november 2025 fortfarande är dagliga sammanställningar, eller om det finns ett "direkt"-läge: hjälpcentret anger en gång per dag, men det är oklart om artikeln uppdaterats efter migreringen.
- Om Blocket/Vend erbjuder en partner-API eller ett feed-program, motsvarande Finns API för bilhandlare och mäklare: hittade inget.
- Antal tillåtna bevakningar per konto: hittades inte.

## 2. Svensk och EU-rätt: katalogskydd, upphovsrätt, TDM, GDPR, avtal och dataintrång

### Takeaway
Huvudrisken är civilrättslig och består av tre delar: sui generis-databasrätt (49 § URL), Blockets avtalsvillkor (och enligt Ryanair kan villkoren gälla även när databasen inte är skyddad) och upphovsrätt till foton. Den straffrättsliga risken (dataintrång) är låg så länge man inte kringgår inloggning eller tekniska spärrar. CV-Online (2021) har gjort katalogskyddet till en avvägning om huruvida databasinvesteringen skadas. Det gynnar en liten, intern, icke-konkurrerande användning. Ingen svensk dom om skrapning av annonssajter hittades.

### Cited Findings
- **49 § URL (katalogskydd):** Den som framställt en katalog eller databas med ett stort antal uppgifter, eller som är resultatet av en väsentlig investering, har ensamrätt att framställa exemplar av och göra tillgänglig hela eller en väsentlig del av den. Skyddet gäller arbetet, inte de enskilda uppgifterna. — [Riksdagen: URL 1960:729](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/lag-1960729-om-upphovsratt-till-litterara-och_sfs-1960-729/); [lagen.nu 1960:729](https://lagen.nu/1960:729); [Riksdagen GL01LU2](https://data.riksdagen.se/dokument/GL01LU2)
- Skyddstiden anges som 10 år i äldre förarbeten men 15 år i en nyare uppsats. Direktivet 96/9/EG och nuvarande lag anger 15 år, och den äldre siffran gällde tidigare lydelse. — [Riksdagen GL01LU2](https://data.riksdagen.se/dokument/GL01LU2); [LU-uppsats](https://lup.lub.lu.se/student-papers/record/9033376/file/9038950.pdf)
- Systematiskt upprepade uttag av små delar som sammantaget motsvarar en väsentlig del omfattas också (art. 7.5 i direktivet). — [aliasnille.se (praktikerblogg)](https://aliasnille.se/webbutveckling/web-scraping-lagligt-sverige/); [Direktiv 96/9/EG, EUR-Lex](https://eur-lex.europa.eu/legal-content/SV/TXT/?uri=CELEX:31996L0009)
- Svensk doktrin (LU-uppsats): skrapning är inte olaglig i sig. Den blir olaglig när villkoren förbjuder den, när datan är skyddad av upphovsrätt eller närstående rätt och när ingen inskränkning är tillämplig. — [LU-uppsats "Upphovsrättsligt intrång genom webbskrapning"](https://lup.lub.lu.se/student-papers/record/9033376/file/9038950.pdf); se även [Lundh, Databasskydd på Internet](https://lup.lub.lu.se/luur/download?func=downloadFile&recordOId=1559894&fileOId=1565135)
- **CV-Online Latvia v Melons (C-762/19, 3 juni 2021):** En specialiserad metasökmotor för jobbannonser (kurdarbs.lv), som indexerade och länkade till cv.lv, kan göra uttag eller vidareutnyttjande. Men det är intrång bara om det **skadar databasframställarens investering**, det vill säga risken att investeringen inte kan återvinnas. Domstolen ska väga detta mot informationsfrihet och konkurrens. Domen markerar en förskjutning från Innoweb. — [Clifford Chance](https://cliffordchance.com/expertise/services/intellectual-property/global-ip-updates/2021/q4/cv-online-latvia-v-melons.html); [SCL](https://www.scl.org/12290-cjeu-search-engine-copying-of-databases-infringes-sui-generis-right-where-it-adversely-affects-database-maker-investment/); [Kluwer Copyright Blog](https://copyrightblog.kluweriplaw.com/2021/06/17/access-to-information-and-competition-concerns-enter-the-sui-generis-rights-infringement-test-the-cjeu-redefines-the-database-right/?output=pdf); [IPPT, domen](https://www.ippt.eu/sites/ippt/files/2021/IPPT20210603_CJEU_CV-Online_Latvia_v_Melons.pdf)
- **Innoweb v Wegener (C-202/12, 2013):** En dedikerad metasökmotor som låter användare söka i hela en annonsdatabas (bilannonser) i realtid ansågs vidareutnyttja hela databasen. Domen relativiserades senare av CV-Online. — [Clifford Chance 2021 (diskuterar Innoweb)](https://www.cliffordchance.com/insights/resources/blogs/talking-tech/en/articles/2021/02/are-all-search-engines-incompatible-with-sui-generis-database-right.html); [EUR-Lex C-202/12](https://eur-lex.europa.eu/legal-content/SV/TXT/?uri=CELEX:62012CJ0202)
- **Ryanair v PR Aviation (C-30/14, 15 jan 2015):** Databasdirektivet gäller inte databaser som saknar både upphovsrätts- och sui generis-skydd. Användarundantagen i art. 6.1 och 8 hindrar då inte ägaren från att begränsa användningen genom avtal (Ryanairs click-wrap-villkor förbjöd skrapning). Konsekvens: ägaren har avtal som skydd även när immaterialrätten inte räcker. — [Portolano/MediaLaws](https://portolano.it/news/ecj-clarifies-database-directive-scope-in-screen-scraping-case); [Law Gazette](https://lawgazette.co.uk/legal-updates/protection-for-unprotected-databases/5046552.article); [CELEX 62014CJ0030](https://inenuitvoer.sdu.nl/content/CELEX-62014CJ0030-ENG)
- Konkurrensrätt kan begränsa skrapförbud för dominerande aktörer (till exempel ett Milano-avgörande 2013 mot Ryanair). — [MediaLaws](https://www.medialaws.eu/ecj-clarifies-database-directive-scope-in-screen-scraping-case/)
- **Text- och datautvinning (DSM-direktivet art. 3/4; URL 15 a–c §§, i kraft 1 jan 2023):** Undantaget gäller för verk man har lovlig tillgång till, om inte rättighetshavaren har reserverat sig maskinläsbart. Om undantaget också täcker katalogskyddet behöver kontrolleras separat. — [aliasnille.se](https://aliasnille.se/webbutveckling/web-scraping-lagligt-sverige/); [DSM-direktivet 2019/790, EUR-Lex](https://eur-lex.europa.eu/legal-content/SV/TXT/?uri=CELEX:32019L0790). Art. 4 DSM omfattar uttryckligen även sui generis-databasrätt (art. 7.1 i direktiv 96/9), enligt direktivtexten.
- **Kneschke v LAION (OLG Hamburg 5 U 104/24, 10 dec 2025):** Mångfaldigande av foton för dataset omfattades av TDM-undantaget. Ett opt-out formulerat i naturligt språk i villkoren ansågs **inte** uppfylla kravet på maskinläsbarhet i §44b UrhG / art. 4 DSM. Reservationer måste vara klara och uttryckliga. Ärendet kan gå vidare till BGH, men källorna är något oense om resonemanget. — [Bird & Bird](https://cm.twobirds.com/en/insights/2025/germany/higher-regional-court-hamburg-confirms-ai-training-was-permitted-(kneschke-v,-d-,-laion)); [Technology's Legal Edge](https://www.technologyslegaledge.com/2025/12/robert-kneschke-v-laion-judgment-of-10-december-2025-ref-5-u-104-24/); [Hogan Lovells tracker](https://digital-client-solutions.hoganlovells.com/resources/ai-litigation-case-law-tracker/case/robert-kneschke-vs-laion-e-v/decision/1)
- **Dataintrång (BrB 4:9c):** Bestämmelsen kräver att gärningen sker "olovligen". Straffet är böter eller fängelse i högst två år, och grovt brott finns. Ingen källa eller dom hittades om att skrapning av öppet tillgängliga sidor skulle vara olovlig. Praktikerbedömningen är att kringgående av inloggning, betalvägg eller teknisk spärr är en helt annan sak. — [lagen.nu: Dataintrång](https://lagen.nu/begrepp/Dataintr%C3%A5ng); [Lagrådsremiss Skärpt straff för dataintrång](https://www.regeringen.se/contentassets/ee8ce55c783e4e02bcca3d40f559691c/skarpt-straff-for-dataintrang.pdf); [aliasnille.se](https://aliasnille.se/webbutveckling/web-scraping-lagligt-sverige/); [LU-uppsats Rydlund](https://lup.lub.lu.se/luur/download?func=downloadFile&recordOId=1561648&fileOId=1565704)
- **Svensk praxis:** Ingen dom om skrapning av annonssajter (Hemnet, Blocket, Booli eller liknande) hittades. Närmast är PMÖD B 9256-18 (2019-10-17): en läkare som laddade ner en katalogskyddad prövningsdatabas ansågs ha framställt exemplar utan samtycke, men friades eftersom han hade rätt att ta del av uppgifterna. — [PMÖD B 9256-18](https://www.domstol.se/patent--och-marknadsoverdomstolen/patent--och-marknadsoverdomstolens-avgoranden/2019/59130/)
- **Upphovsrätt till bilder:** Fotografier skyddas automatiskt, antingen som verk om de är originella eller annars som fotografisk bild (49 a § URL). — [PRV: Upphovsrätt på bilder](https://www.prv.se/sv/upphovsratt/for-anvandare/upphovsratt-pa-bilder/)

### Inferences
- **Katalogskydd:** Blockets och Auctionets annonsbaser uppfyller nästan säkert kravet på väsentlig investering. Att lagra slutpriser över tid från Auctionet (tusentals objekt) och bygga en egen prisdatabas är ett uttag av en kvantitativt väsentlig del, även när det sker i små portioner. Efter CV-Online är den avgörande frågan om användningen skadar investeringen. En privat, intern prisreferens som inte publiceras och inte konkurrerar om trafik ligger i den svagare änden. Risken finns ändå i teorin, och den växer om datamängden blir stor eller om verktyget någonsin kommersialiseras eller delas.
- **Privat bruk (12 § URL)** gäller inte för katalogskyddade databaser på samma sätt. Det är dessutom tveksamt om undantaget gäller när syftet är förvärvsverksamhet (arbitrage/vidareförsäljning). Nyttan är begränsad.
- **TDM-undantaget (15 a §)** kan teoretiskt täcka mångfaldigande för analys, inklusive av sui generis-skyddade databaser. Men om Blocket eller Auctionet har en maskinläsbar reservation (till exempel i robots.txt eller via TDMRep-headers) faller det. Undantaget ändrar heller inte avtalsrisken. Enligt Ryanair-logiken kan villkoren förbjuda det som immaterialrätten inte förbjuder, och för en inloggad användare är det sannolikt att avtalet binder.
- **GDPR:** Säljares namn, telefonnummer, ort och profil på Blocket är personuppgifter. För en enskild som bedriver näringsverksamhet (återförsäljning) gäller inte privatundantaget i art. 2.2 c. Lagra minimalt (annons-id, pris, titel, kategori, ort på kommunnivå), lagra inga telefonnummer eller namn, och ha en kort gallringstid. Då blir risken låg, med berättigat intresse som rättslig grund. (Slutsatsen bygger på GDPR:s allmänna systematik; ingen specifik källa hämtades.)
- **Dataintrång:** Risken är försumbar för att läsa sidor man själv har åtkomst till. Den ökar om man kringgår bot-skydd (CAPTCHA, rate limits, blockering), roterar IP-adresser eller fejkar konton för att undgå spärrar. Det ligger närmare "olovligen", även om ingen praxis finns.

### Gaps
- Fulltexten i URL 15 a–c §§ och den exakta nuvarande lydelsen av 49 § kunde inte hämtas från lagen.nu eller riksdagen.
- Ingen svensk dom om webbskrapning av annonsplattformar, och ingen svensk byråartikel 2024–2026 om webbskrapning hittades i sökningen.
- Ingen avgörande källa om huruvida svenska privatpersoners prisdatabaser för eget bruk har prövats.

## 3. Auktionshus och Tradera: villkor, API:er och robots.txt

### Takeaway
Tradera har fortfarande ett officiellt utvecklarprogram (SOAP v3 plus REST v4 i beta, med kvoter) och är det enda lagliga API-alternativet i listan. Auctionet, Bukowskis, Stockholms Auktionsverk och Lauritz har ingen känd publik API för slutpriser. Deras villkor och robots.txt kunde inte läsas i denna session.

### Cited Findings
- **Tradera:** api.tradera.com beskriver REST API (v4) och SOAP API (v3). v4 är i beta, och endpoints kan ändras utan förvarning. Man behöver ett utvecklarkonto och app-credentials. Kvoten är 10 000 anrop per 24 timmar per metod, och överskridanden ger HTTP 429. Ingen nedläggning har aviserats. Sökningar via API:t ger i första hand aktiva objekt; avslutade och sålda objekt är begränsade. — [Tradera Developer Program](https://api.tradera.com/); [v3 docs: FirstCall](https://api.tradera.com/v3/documentation/static.aspx?page=FirstCall); [ekdennisek/tradera-api-client](https://github.com/ekdennisek/tradera-api-client); [PyPI tradera_api](https://pypi.org/project/tradera_api/)
- **Auctionet:** Ingen publik utvecklar- eller API-dokumentation hittades. Kända integrationer gäller betalningar (Brite) och onboarding av auktionshus. — [Brite case: Auctionet](https://britepayments.com/fr/temoignages/auctionet/)
- Auktionshus på Auctionet hänvisar köpare till Auctionets villkor (auctionet.com/sv/terms), men sidan kunde inte hämtas. — [Karljohan Auktioner köpvillkor](https://karljohanauktioner.se/kopvillkor/)
- Branschpraxis: säljaren/auktionshuset ansvarar för att bildmaterialet inte strider mot upphovsrättslagen (exempel från auktionet.se, oklart om samma bolag). Rättigheterna till katalogfoton ligger alltså hos auktionshuset eller fotografen, inte hos Auctionet som plattform. — [auktionet.se villkor](https://www.auktionet.se/info/terms)
- Branschen i stort: lot-API:er brukar vara stängda partner-API:er (till exempel Invaluables Catalog Upload API). — [API Evangelist: Invaluable](https://providers.apievangelist.com/providers/invaluable/)

### Inferences
- Auctionets historiska slutpriser är publikt synliga (sålda objekt med klubbat pris). Det är sannolikt det mest värdefulla och mest katalogskyddade underlaget. Att hämta ett begränsat urval för de specifika formgivare eller modeller man följer (tiotals eller hundratals objekt, manuellt eller med låg frekvens) är en klart lägre risk än en fullständig spegling.
- Bukowskis, Stockholms Auktionsverk och Lauritz har sannolikt liknande villkor (ensamrätt till bilder och texter). Lauritz har haft bolagsrättsliga turbulenser, vilket påverkar datans kontinuitet men inte juridiken.
- Bättre alternativ till skrapning: (1) Traderas API för avslutade och aktiva objekt; (2) att fråga Auctionet om en dataexport eller licens. Som enskild återförsäljare/köpare har man en kundrelation, och en liten, icke-konkurrerande användning kan beviljas. (3) Egna köp- och försäljningsdata.

### Gaps
- Robots.txt och villkor för auctionet.com, bukowskis.com, auktionsverket.se och lauritz.com: blockerade, ej verifierade.
- Om Tradera-API:t 2026 exponerar avslutade eller sålda objekt med slutpris: ej verifierat.
- Om Auctionet har TDM-reservation (maskinläsbar opt-out): okänt.

## 4. Bedömning av workarounds (privatperson, intern arbitrage)

### Takeaway
Den bästa vägen när det gäller både juridik och kontorisk är att parsa Blockets egna bevakningsnotiser (e-post, eller push vidarebefordrad), i kombination med ett manuellt delningsflöde ("dela länk till boten") och egen historik. En lokal agent i den egna inloggade sessionen som pollar några få sökningar med låg frekvens är en måttlig avtals- och bannrisk. Storskalig skrapning av Auctionets slutpriser är den största rättsliga exponeringen.

### Cited Findings
- E-post för bevakningar kommer en gång per dag, push kort efter publicering. — [Blocket hjälpcenter](https://blocket.zendesk.com/hc/sv/articles/22875498207506-Bevakningar)
- Att kringgå inloggning eller tekniska spärrar är kvalitativt annorlunda (dataintrång). — [aliasnille.se](https://aliasnille.se/webbutveckling/web-scraping-lagligt-sverige/)
- Avtalsvillkor kan förbjuda skrapning oavsett databasskydd. — [Law Gazette om Ryanair](https://lawgazette.co.uk/legal-updates/protection-for-unprotected-databases/5046552.article)
- Upprepade små uttag kan sammantaget utgöra intrång. — [Direktiv 96/9/EG art. 7.5](https://eur-lex.europa.eu/legal-content/SV/TXT/?uri=CELEX:31996L0009)

### Inferences (riskmatris, egen bedömning)
| Väg | Rättslig risk | Risk för kontoavstängning | Kommentar |
|---|---|---|---|
| (b) Parsa Blockets bevakningsmejl i Gmail | **Låg** | **Mycket låg** | Datan skickas till dig av Blocket, så det är ingen åtkomst till deras system. Problemet är hastigheten: e-post en gång per dag. Komplettera med pushnotis; Android-notiser kan läsas lokalt via en notification listener, vilket är tekniskt möjligt men skört. Efter november 2025 behöver mejlformatet verifieras. |
| (c) Manuell "dela länk till boten" | **Låg** | **Mycket låg** | Du läser annonsen som vanlig användare. Boten hämtar en enskild sida på begäran, vilket är ett försumbart uttag. Spara inte säljarens personuppgifter. |
| (d) Egen historik (egna köp och försäljningar, egna anteckningar, manuellt noterade auktionspriser) | **Mycket låg** | Ingen | Den rättsligt renaste prisdatabasen. Manuellt antecknade slutpriser (fakta) skyddas inte i sig; risken uppstår först när en väsentlig del av databasen tas ut. |
| (a1) Webbläsartillägg som passivt läser sidor du själv öppnar | **Låg till måttlig** | **Låg** | Ingen extra trafik. Avtalsrisken beror på villkorens ordalydelse ("automatiserade verktyg"). I praktiken går det inte att upptäcka. |
| (a2) Lokal agent i inloggad session som pollar 3–10 sparade sökningar var 5–15 minut | **Måttlig** (avtalsbrott; katalogskydd osannolikt vid så små uttag) | **Måttlig** | Vend/Finn-plattformen har bot-detektering. Låg frekvens, människolik UA och ingen IP-rotation sänker risken. Kringgå aldrig CAPTCHA eller blockering, eftersom det driver mot dataintrång. Ett avstängt Vend-konto kan påverka inloggning på alla Vend-sajter. |
| Bred skrapning av Blocket utan inloggning (alla möbelannonser) | **Måttlig till hög** | Hög (IP-blockering) | Innoweb- och CV-Online-scenariot. Liten skada på investeringen talar för dig, men systematiskt uttag plus villkorsbrott talar emot. |
| Fullständig spegling av Auctionets slutpriser plus bilder | **Hög** (katalogskydd + upphovsrätt till foton) | Konto ej nödvändigt; IP-blockering | Välj hellre ett urval per formgivare, Tradera-API:t eller en förfrågan om licens. |

- Praktisk verklighet: civilrättsliga processer mot enskilda småskaliga skrapare är sällsynta. Det realistiska utfallet är blockering, kontoavstängning eller ett varningsbrev. Risken skalar med volym, synlighet och kommersiell konkurrens.

### Gaps
- Vend-plattformens faktiska bot-skydd (Cloudflare, Akamai eller liknande) och tröskelvärden: okända.
- Om Blocket-pushnotiser innehåller tillräckligt med data (titel, pris, länk) för att parsas: ej verifierat.

## 5. Modellträning på auktionsfoton: embeddings och referensbibliotek kontra visning

### Takeaway
Att ladda ner auktionsfoton och räkna fram embeddings för en intern referens- eller likhetssökning är ett mångfaldigande. Det kan rymmas i TDM-undantaget (15 a § URL / art. 4 DSM) om ingen giltig maskinläsbar reservation finns. Kneschke v LAION (OLG Hamburg, december 2025) stödjer en sådan läsning. Att visa eller publicera bilderna, även internt i ett delat UI, är det som tydligt kräver tillstånd. Det säkraste mönstret är att spara embeddings, metadata och länk, men inte bilderna permanent.

### Cited Findings
- Fotografier skyddas automatiskt, som verk eller som fotografisk bild. — [PRV](https://www.prv.se/sv/upphovsratt/for-anvandare/upphovsratt-pa-bilder/)
- TDM-undantaget gäller lovligt tillgängligt material om ingen maskinläsbar reservation finns. — [aliasnille.se](https://aliasnille.se/webbutveckling/web-scraping-lagligt-sverige/); [DSM-direktivet art. 4](https://eur-lex.europa.eu/legal-content/SV/TXT/?uri=CELEX:32019L0790)
- OLG Hamburg (10 dec 2025): reproduktion av foton för dataset täcktes av TDM-undantaget. Opt-out i naturligt språk var inte maskinläsbart och därmed ogiltigt. — [Bird & Bird](https://cm.twobirds.com/en/insights/2025/germany/higher-regional-court-hamburg-confirms-ai-training-was-permitted-(kneschke-v,-d-,-laion)); [DLA Piper](https://www.dlapiper.com/en/insights/blogs/mse-today/2025/robert-kneschke-v-laion)
- Art. 4.2 DSM: kopior får behållas så länge som är nödvändigt för utvinningen. — [DSM-direktivet, EUR-Lex](https://eur-lex.europa.eu/legal-content/SV/TXT/?uri=CELEX:32019L0790)

### Inferences
- Rekommenderat mönster: hämta bilden, beräkna embedding och extrahera attribut, och radera eller kassera originalet efter en kort tid. Spara bara vektor, objekt-id, slutpris, datum och käll-URL. Vid träff i UI:t: länka till källan eller hämta bilden live som hotlink, och lagra ingen kopia.
- Om sajten har en maskinläsbar reservation (robots.txt som blockerar AI- och crawler-agenter, TDMRep, `noai`-meta) faller TDM-undantaget. Kontrollera detta per sajt innan körning. Det kunde inte göras här.
- Att visa auktionsfoton i ett internt verktyg för en person är en grå zon. Det handlar inte om tillgängliggörande för allmänheten, men om lagrade kopior och om mångfaldigandet ligger utanför 15 a §. Visning i en annons (till exempel att återanvända Auctionets eller säljarens foto när du säljer vidare) är **tydligt intrång**. Ta alltid egna foton.
- EU:s AI-förordning (transparenskrav för GPAI) träffar inte en lokal embedding-modell för eget bruk.

### Gaps
- Ingen svensk praxis om TDM och 15 a § hittades.
- Om Auctionet eller auktionshusen deklarerar TDM-opt-out: ej verifierat.
- Att Kneschke-målet ligger hos BGH bygger på en enda källa.
