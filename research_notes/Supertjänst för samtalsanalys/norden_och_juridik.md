# Samtalsanalys i Norden: konkurrenter, marknad och juridisk ram (Sverige/EU), läge oktober 2026

Anteckningar från WebSearch (direkt hämtning blockerades för bl.a. edpb.europa.eu). Inget här är juridisk rådgivning. Där en källa är en leverantörs egen marknadsföring står det så. Primärkällor som bör läsas i original: AI-förordningen (EU) 2024/1689 på EUR-Lex, Digital Omnibus-förordningen (EU) 2026/1744, kommissionens riktlinjer om förbjudna AI-metoder (februari 2025), IMY:s förteckning enligt art. 35.4, BrB 4:9 a, 2 kap. 3 a § distansavtalslagen (2005:59), MiFID II art. 16(7) samt delegerade förordningen 2017/565 art. 76.

## 1. Konkurrenter och närliggande aktörer i Norden/Europa, och var luckorna finns

### Takeaway
Den nordiska marknaden domineras av plattformsbolag med inbyggd analys (främst Puzzel, som har köpt Capturi och SupWiz) och av globala/europeiska säljverktyg för samtalsanalys (Gong, Modjo, Jiminny). Agaton (Stockholm) är den tydligaste svenska nischaktören, med seedrunda på cirka 10 MUSD i februari 2026. Konkurrensen avgörs av hur bra modellen klarar nordiska språk, att data stannar i EU och att produkten följer AI-förordningen.

### Cited Findings
**Agaton (Stockholm)**
- Grundat 2024, VD och medgrundare Andreas Kullberg. Kom ut ur "stealth" i februari 2026 med cirka 10 MUSD (8,4 MEUR) i seed, samledd av Inception Fund och Alstin Capital, med seed+speed Ventures och Foundry Ventures — [EU-Startups](https://www.eu-startups.com/2026/02/stockholm-based-agaton-secures-e8-4-million-to-turn-customer-conversations-into-revenue-insights/); [ArcticStartup](https://arcticstartup.com/agaton-raises-10m-in-seed/). Källorna anger olika belopp: ContentGrip skriver 9,9 MUSD — [ContentGrip](https://www.contentgrip.com/agaton-seed-funding-ai-sales/)
- Produkten är SaaS-röstanalys för sälj och kundtjänst. Den hittar köpsignaler, följer förändringar i "sentiment" och ger coachningsinsikter utöver transkribering. Bolaget uppger fler än 4 miljoner analyserade samtal, fördubblad konvertering hos toppsäljare och upp till 80 % kortare QA-tid (egna, ej verifierade siffror) — [Beinsure](https://beinsure.com/news/stockholm-startup-agaton-raises-10mn-seed/); [Agaton](https://www.agaton.ai/)
- Teamet har bakgrund från Spotify, Tink, Astrid, Sana och EF. Adress Brahegatan 4, Stockholm — [Agaton about](https://www.agaton.ai/about-us)

**Puzzel (Oslo) och Capturi (DK)**
- Puzzel säljer Conversational Intelligence som en del av sin kontaktcentersvit. Bolaget har egen taligenkänning (ASR) och NLP tränade på svenska, norska, danska, finska, nederländska och brittisk engelska, och behandlar data "entirely within EU infrastructure". Funktioner: transkribering, taggning, sammanfattning och automatisk QA-poängsättning av alla samtal (leverantörens påståenden) — [Puzzel](https://www.puzzel.com/products/conversational-intelligence)
- Puzzel köpte SupWiz (konversations-AI) i augusti 2024 och danska Capturi (talanalys) i oktober 2024. Bolaget uppger cirka 1 000 organisationer och cirka 100 000 agenter i Norden, Storbritannien och kontinentaleuropa — [Yespress](https://yespress.io/puzzel)
- Capturi (Åbyhøj, DK) har talanalys byggd för nordiska språk: danska, svenska, norska (bokmål), finska, engelska, tyska och polska. Bolaget uppger 35–40 miljoner analyserade samtal per år inom sälj, kundtjänst och medborgarservice — [Capturi LinkedIn](https://www.linkedin.com/products/capturi/); [SoftwareAdvice](https://www.softwareadvice.com/speech-analytics/capturi-profile/)
- Enligt Capturi har skandinaviska företag lämnat amerikanska samtalsanalysverktyg eftersom analysen av nordiska språk var för dålig (leverantörens egen bild) — [CustomerThink](https://customerthink.com/the-challenge-with-conversational-analysis-in-the-nordics-interview-with-tue-martin-berg-of-capturi/)

**Telefoni och AI-röstagenter i Sverige**
- Telavox (Malmö) lanserade en AI-röstreceptionist 2025 — [LeadIQ](https://leadiq.com/c/telavox/5a1d98612300005c00870eaf)
- Leverantörer av AI-telefonagenter i Sverige: Real Talk, Dstny, Menodi, Puzzel, Svaria, Telavox, Telink — [Real Talk-guide](https://callrealtalk.com/en/guider/ai-phone-agent-providers-in-sweden) (källan är själv en konkurrent)
- Ebbot (Stockholm, 11–50 anställda) automatiserar kundtjänst, med tonvikt på chatt — [RevenueBase](https://revenuebase.ai/companies/ai-chatbot-startups/sweden)
- Brightcall.ai beskriver sig som svensk leverantör av AI-agenter, callcenter-mjukvara och automatiserade återuppringningar (egen blogg) — [Brightcall](https://brightcall.ai/blog/top-5-ai-softwares-from-sweden----and-how-theyre-shaping-the-future-of-business)

**Europeiska och globala säljverktyg för samtalsanalys**
- Modjo (Paris) har tagit in mer än 14 MEUR och kör på AWS i Paris — [SalesHive](https://saleshive.com/vendors/modjo); [Puzzleinbox](https://puzzleinbox.com/tools/modjo/)
- Jiminny (Storbritannien) positioneras som det Europa-fokuserade alternativet — [Claap](https://www.claap.io/blog/conversation-intelligence-software)
- Gong (USA) erbjuder ett EU-datacenter som tillval. Jämförelser beskriver alternativen för EU-lagring som begränsade — [Optivian](https://optivian.ai/insights/gong-alternatives-europe/)
- Genesys Cloud CX har inbyggd tal- och textanalys med ämnen och sentiment — [Puzzel-jämförelse](https://www.puzzel.com/top-contact-centre-ai-platforms-for-europe-in-2026-puzzel)

### Inferences
- Branschen delar sig i två delar. (a) Kontaktcentersviter (Puzzel/Capturi, Genesys, troligen även Telavox och Dstny) där analysen ingår i plattformen. (b) Fristående säljverktyg (Gong, Modjo, Jiminny, Agaton) som kopplas till CRM och telefoni. En ny aktör måste välja: oberoende av plattform (integrera mot Telavox, Puzzel, Teams, Genesys med flera) eller vertikal nisch.
- Möjliga luckor: (1) Säljsamtal per telefon på svenska med hög ASR-kvalitet. Gong är engelsk-först och Puzzel/Capturi kontaktcenter-först. (2) Efterlevnadskontroller för telefonförsäljning (skriftlighetskrav, NIX, korrekt information) och för finans (MiFID-inspelning). (3) Produkter som är "AI Act-säkra" från början, utan emotionsigenkänning på röst och med stöd för MBL-förhandling och konsekvensbedömning (DPIA). (4) BPO-anpassad analys för flera kunder samtidigt.
- Agatons uttryck "sentiment changes" utifrån röst ligger nära gränsen i art. 5(1)(f) (se avsnitt 4). Det kan bli en konkurrensfördel att uttryckligen bygga på text och semantik i stället för röstbiometri.

### Gaps
- Följande hittades inte eller kunde inte verifieras: Weply, Freja, Speechly (köptes av Roblox 2022 enligt min tidigare kunskap, ej verifierat här), Capacity, Lime Technologies/Upsales/Dealfront (CRM-sidan, inga träffar om samtalsanalys), samt finska, norska och danska aktörer utöver Capturi.
- Det framkom inte vilka leverantörer svenska telekombolag, banker, försäkringsbolag, energibolag och BPO-bolag använder. Inga kundcase hittades.
- Inga artiklar från Breakit/Di Digital kom fram. Agatons eventuella senare rundor eller kunder efter februari 2026 är okända.

## 2. Marknadsstorlek och struktur för nordiska kontaktcenter, och köparnas problem

### Takeaway
Det saknas tillförlitliga siffror på antalet agenter. IBISWorld räknar med 446 callcenterföretag i Sverige och en omsättning på cirka 691,5 MEUR (2026), med krympande antal företag och färre agenter. Sverige står för cirka 46 % av den skandinaviska BPO-marknaden. Puzzels cirka 100 000 agenter i Norden plus Europa ger en nedre gräns för hur stor bara en plattforms installerade bas är.

### Cited Findings
- 446 callcenterföretag i Sverige 2025. Antalet krymper med 2,4 % per år (CAGR) 2020–2025, och marknadsvärdet 2026 uppskattas till 691,5 MEUR. Kunderna minskar antalet agenter — [IBISWorld](https://www.ibisworld.com/sweden/industry/call-centres/200313/)
- Sverige hade 45,9 % av den skandinaviska BPO-marknaden 2024, före Norge och Danmark. Siffran gäller BPO brett, inte bara kontaktcenter — [MarketLine via MarketPublishers](https://marketpublishers.com/report/services/other_services/bpo-services-in-scandinavia_marketline.html)
- Outsourcade nordiska agenter kostar cirka 22 200 EUR per agent och år (gammal uppgift) — [CBI](https://www.cbi.eu/market-information/outsourcing-itobpo/contact-center-services/market-potential)
- Lön för svenska callcenteragenter: 28 000–38 000 kr/mån plus 31,42 % arbetsgivaravgifter (leverantörsblogg) — [Callitdev](https://callitdev.com/en/blog/call-center-services-sweden)
- Accenture och Capgemini leder den nordiska BPO-marknaden (bredare BPO) — [Coordea](https://coordea.com/news/accenture-and-capgemini-leading-the-nordic-bpo-market/)
- Puzzel uppger cirka 100 000 agenter hos cirka 1 000 organisationer — [Yespress](https://yespress.io/puzzel)
- Problem som säljs in: QA-granskning är manuell och bygger på stickprov (Agaton lovar upp till 80 % kortare QA-tid), coachning och konvertering — [Beinsure](https://beinsure.com/news/stockholm-startup-agaton-raises-10mn-seed/). För nordiska köpare är det också ett problem att amerikanska verktyg ger dålig träffsäkerhet på nordiska språk — [CustomerThink](https://customerthink.com/the-challenge-with-conversational-analysis-in-the-nordics-interview-with-tue-martin-berg-of-capturi/)
- Telefonförsäljning: efter skriftlighetskravet 2018 har det blivit vanligare att företagen inte spelar in säljsamtalen (SOU 2021:79 enligt sammanfattning) — [Riksdagen prop.](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/proposition/skriftlighetskrav-vid-telefonforsaljning_h503129/html/)

### Inferences
- Med 22 200 EUR per agent och år blir en analyslicens på 50–150 EUR per agent och månad 3–8 % av agentkostnaden. Löftet om QA-besparing gör det försvarbart att ta betalt per agent.
- Krympande agentvolymer (automatisering, AI-agenter) talar för att priset hellre bör knytas till samtalsvolym eller resultat än till antal användare.

### Gaps
- Antal agenter i Sverige och Norden, och marknadsandelar för Transcom, Teleperformance, Foundever och Sitel i Norden, hittades inte. Leta i deras årsredovisningar och i Frost & Sullivans studie om europeisk kontaktcenter-BPO.
- Ingen oberoende undersökning av köparnas problem (t.ex. från Kundservicebranschen eller CCMA Nordic) kom fram.

## 3. GDPR och svensk arbetsrätt för inspelning och analys av samtal

### Takeaway
Ett företag får i Sverige spela in samtal där det själv är part utan straffansvar (BrB 4:9 a gäller bara samtal man inte deltar i). Behandlingen kräver ändå laglig grund enligt GDPR: i praktiken berättigat intresse för kvalitet och coachning, med information till den som ringer och rätt att invända, eller rättslig förpliktelse när MiFID gäller. Analys av anställda är primärförhandlingspliktig enligt 11 § MBL. Konsekvensbedömning (DPIA) blir i praktiken nödvändig. Överföringar till USA vilar på Data Privacy Framework (DPF), som överlevde tribunalen 2025 men är överklagat till EU-domstolen (C-703/25 P, inte avgjort i juni 2026).

### Cited Findings
**Straffrätt**
- Olovlig avlyssning (BrB 4 kap. 9 a §) avser hemlig inspelning med tekniskt hjälpmedel av samtal som gärningsmannen inte själv deltar i. Straffet är böter eller fängelse i högst två år. Motsatsvis är det tillåtet att spela in samtal man deltar i, även utan att motparten vet om det — [Lawline](https://lawline.se/answers/lagligt-att-spela-in-ett-samtal); [Lawline](https://lawline.se/answers/far-jag-spela-in-samtal-som-jag-sjalv-inte-deltar-i)
- Även när inspelningen är straffri kan dataskyddsreglerna gälla — [Lawline](https://lawline.se/answers/tillatet-att-spela-in-samtal)

**Laglig grund och information**
- Datainspektionen (numera IMY) fann 2016 att TeliaSonera saknade rättsligt stöd för att spela in kundsamtal för coachning och processförbättring, och gav bolaget valet att sluta eller informera de som ringer (enligt PUL, före GDPR) — [IMY-beslut Telia 2016](https://www.imy.se/globalassets/dokument/beslut/2016-05-12-telia.pdf)
- IMY har även gjort tillsyn mot Nordea som rör inspelning av samtal (dokumentet hittades men har inte lästs i detalj) — [IMY-beslut Nordea](https://www.imy.se/contentassets/882af6d7f09b4412872ba754618fbaf1/beslut-tillsyn-nordea.pdf)
- EDPB:s vägledning för små och medelstora företag (FAQ "Kan vi spela in telefonsamtal med kunder för att förbättra kvaliteten …?") säger att kunderna ska informeras om syftet, mottagarna, rätten att invända och rätten till tillgång — [EDPB SME-guide](https://www.edpb.europa.eu/node/5410_sv) (sidan kunde inte hämtas, sammanfattningen kommer från sökresultatet)
- Kunder kan begära ut sin inspelning med stöd av rätten till tillgång (art. 15) — [Lawline](https://lawline.se/answers/kan-en-kund-begara-ut-inspelat-telefonsamtal-vid-kontakt-med-kundtjanst)

**Övervakning av anställda och MBL**
- Primär förhandlingsskyldighet enligt 11 § MBL gäller innan arbetsgivaren beslutar om viktigare förändring av verksamheten eller av enskildas arbets- eller anställningsförhållanden. I vissa fall gäller den även mot organisationer utan kollektivavtal (13 §). AD kräver att arbetsgivaren lämnar den information som behövs för en meningsfull förhandling — [FAR Online](https://www.faronline.se/dokument/rattserien/ratt-arbetsratt/p/ra_primarforhandlingsskyldighet/); [AD 2008 nr 24](https://lagen.nu/dom/ad/2008:24)
- Arbetsdomstolen har i remissvar föreslagit att arbetstagarorganisationen ska kunna få skadestånd när arbetsgivaren missar förhandlingsskyldigheten vid kamerabevakning — [AD remissvar](https://www.regeringen.se/contentassets/ab5caf0a9cd04f4b932d1b3217e846fd/013-arbetsdomstolen.pdf)
- IMY anger övervakning i arbetslivet som särskilt tillsynsfokus, eftersom ny teknik möjliggör omfattande övervakning av anställda — [IMY](https://www.imy.se/link/fc2f0392d948421bb8ed199626d6de7b.aspx)

**DPIA**
- IMY:s vägledning om konsekvensbedömning (februari 2025) säger att behovet ska bedömas utifrån art. 35.1, exemplen i art. 35.3 och IMY:s förteckning enligt art. 35.4, som bygger på EDPB:s kriterier. Riskreducerande åtgärder får inte vägas in när man bedömer om DPIA behövs — [IMY mall/vägledning](https://www.imy.se/link/e83a5ae689c04fa0ac0111c157e45ab6.aspx)

**Överföring till USA**
- EU-tribunalen ogillade Latombes talan mot DPF den 3 september 2025 (T-553/23). Överklagandet till EU-domstolen gavs in den 31 oktober 2025 (C-703/25 P). Microsoft intervenerade till stöd för kommissionen i juni 2026, och målet var då fortfarande öppet — [WilmerHale](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20251201-european-court-of-justice-to-review-challenge-to-eu-us-data-privacy-framework); [iEU Monitoring](https://ieu-monitoring.com/editorial/microsoft-backs-eu-commission-in-eu-court-case-on-transatlantic-data-flows-and-privacy/1244467/)

### Inferences (tolkning, att verifiera med jurist)
- **Rollfördelning:** Kunden (arbetsgivaren) är personuppgiftsansvarig och plattformen personuppgiftsbiträde (art. 28-avtal). Om leverantören använder samtalen för att träna egna modeller blir den troligen självständigt personuppgiftsansvarig för det ändamålet och behöver egen laglig grund. Det är en vanlig fallgrop.
- **Laglig grund:** Samtycke fungerar dåligt för anställda (beroendeställning) och opraktiskt för de som ringer. Berättigat intresse (art. 6.1 f) med intresseavvägning är normalvägen. MiFID-inspelning bygger på art. 6.1 c.
- **Information:** Ett meddelande innan samtalet kopplas ("samtalet kan spelas in och analyseras för kvalitet och utbildning") plus länk till fullständig information enligt art. 13. Vid utgående säljsamtal ska informationen ges i början av samtalet. Kunden ska kunna invända (art. 21).
- **DPIA:** Systematisk övervakning av anställda med ny teknik (AI) och storskalig behandling träffar flera av EDPB:s kriterier, så DPIA krävs i praktiken. Plattformen bör leverera en DPIA-mall till kunderna.
- **Särskilda kategorier:** Samtal i bank, försäkring, vård och energi (betalningsproblem) kan innehålla hälso- eller ekonomiuppgifter. Röst blir biometrisk uppgift enligt art. 9 bara om den behandlas för att unikt identifiera någon (röstavtryck). Plattformen bör undvika talarigenkänning via röstavtryck, eller behandla det som art. 9-data.
- **Lagring:** Sverige har ingen generell lagstadgad lagringstid för kundsamtal. Lagringsminimering gäller. 30–90 dagar för QA-ljud och längre tid för transkript är vanligt i branschen (ej källbelagt), medan MiFID kräver 5–7 år.
- **Svensk arbetsrätt:** Sverige har ingen särskild lag om integritet i arbetslivet (SOU 2009:44 ledde inte till lagstiftning, min kunskap, ej verifierat här). Därför styr GDPR, MBL och kollektivavtal (t.ex. Unionens) tillsammans. Hos BPO-bolag och telekom med kollektivavtal bör en MBL-förhandling planeras in i varje säljcykel.
- **Överföring:** Om DPF ogiltigförklaras i C-703/25 P (en "Schrems III") faller amerikanska underbiträden som LLM- och ASR-API:er tillbaka på standardavtalsklausuler (SCC) och bedömning av överföringsrisk (TIA). Ett EU-värdat alternativ (t.ex. EU-regioner med EU-baserade underbiträden) minskar risken och är ett säljargument mot Gong.

### Gaps
- Inget aktuellt IMY-ställningstagande under GDPR om inspelning av kundsamtal för QA hittades. Nordea-beslutets innehåll är inte kontrollerat.
- Ingen AD-dom om AI-analys eller inspelning av agenters samtal hittades.
- Det är inte bekräftat om IMY:s förteckning enligt art. 35.4 uttryckligen nämner övervakning av anställda.
- Datum för förhandling, generaladvokatens förslag och dom i C-703/25 P är okända per oktober 2026. Kontrollera curia.europa.eu.

## 4. EU:s AI-förordning: emotionsförbud, högrisk, transparens och Digital Omnibus

### Takeaway
Art. 5(1)(f) (gäller sedan 2 februari 2025) förbjuder att dra slutsatser om **anställdas** känslor utifrån biometriska data, t.ex. röst, på arbetsplatsen. Kommissionen nämner uttryckligen ett callcenter som spårar agenters ilska via röstigenkänning som förbjudet. Att analysera **kunders** känslor faller utanför förbudet (riktlinjerna punkt 254), men är då ett emotionsigenkänningssystem med transparenskrav (art. 50.3) och kan vara högrisk (bilaga III.1 c). Att övervaka och utvärdera arbetstagares prestationer är högrisk enligt bilaga III.4 b. Digital Omnibus (förordning (EU) 2026/1744, i kraft 27 juli 2026) skjuter upp skyldigheterna för högrisksystem i bilaga III till **2 december 2027**. Art. 50 (bl.a. att röstagenter ska upplysa om att de är AI) gäller oförändrat från **2 augusti 2026**.

### Cited Findings
**Art. 5(1)(f) och kommissionens riktlinjer (februari 2025)**
- Förbudet gäller bara AI-system som identifierar eller drar slutsatser om känslor eller avsikter utifrån biometriska data — [Lewis Silkin](https://www.lewissilkin.com/insights/2025/02/17/understanding-the-eu-ai-acts-prohibited-practices-key-workplace-and-advertising-102k011)
- "Using webcams and voice recognition systems by a call centre to track employees' emotions is also prohibited" (exempel: ilska) — [Lewis Silkin](https://www.lewissilkin.com/insights/2025/02/17/understanding-the-eu-ai-acts-prohibited-practices-key-workplace-and-advertising-102k011); [WSGR](https://www.wsgrdataadvisor.com/2025/02/eu-commission-issues-guidelines-on-prohibited-ai-practices-under-eu-ai-act/)
- Förbudet gäller arbetstagares känslor, inte kunders. "The use of a voice recognition system in a call center to track customer emotions … would not be within scope (para. 254, example box)" — [FPF](https://fpf.org/blog/red-lines-under-eu-ai-act-unpacking-the-prohibition-of-emotion-recognition-in-the-workplace-and-education-institutions/)
- Undantag finns för medicinska skäl och säkerhetsskäl. Verktyg för personlig träning kan vara tillåtna om data inte delas med arbetsgivaren — [FPF](https://fpf.org/blog/red-lines-under-eu-ai-act-unpacking-the-prohibition-of-emotion-recognition-in-the-workplace-and-education-institutions/)
- Förbudet träffar användaren (deployer) även om leverantören har uteslutit sådan användning i avtalet — [FPF](https://fpf.org/blog/red-lines-under-eu-ai-act-unpacking-the-prohibition-of-emotion-recognition-in-the-workplace-and-education-institutions/)
- Riktlinjerna är inte bindande, och det är EU-domstolen som tolkar auktoritativt — [Orrick](https://www.orrick.com/en/Insights/2025/04/EU-Commission-Publishes-Guidelines-on-the-Prohibited-AI-Practices-under-the-AI-Act); [Covington](https://www.insideglobaltech.com/2025/06/04/european-commission-guidelines-on-prohibited-ai-practices-under-the-eu-artificial-intelligence-act/)
- Primärtext: förordning (EU) 2024/1689, art. 3(39) (emotionsigenkänningssystem), art. 5(1)(f), art. 50(3), bilaga III punkt 1 c och punkt 4 b — [EUR-Lex 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

**Digital Omnibus (högrisktidplan)**
- Preliminär överenskommelse 7 maj 2026. Parlamentet röstade 16 juni 2026 (423–57–174) och rådet gav slutligt klartecken 29 juni 2026. Förordningen (EU) 2026/1744 publicerades i EUT den 24 juli och trädde i kraft den 27 juli 2026 — [Usercentrics](https://usercentrics.com/knowledge-hub/eu-ai-act-high-risk-delay-article-50-transparency-consent/); [CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-omnibus-vii-deadline-delay-20260/); [Cooley](https://cdp.cooley.com/digital-ai-omnibus-delays-key-deadlines-introduces-new-rules/)
- Högrisksystem i bilaga III flyttas från 2 augusti 2026 till 2 december 2027. Bilaga I (produkter) flyttas till 2 augusti 2028 — [CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-high-risk-deadline-omnibus-20260/); [Hogan Lovells](https://www.hlc.com/en/publications/eu-legislators-agree-to-delay-for-highrisk-ai-rules); [artificialintelligenceact.eu](https://artificialintelligenceact.eu/ai-act-explorer/digital-omnibus/)
- Omnibusen lägger till två förbjudna kategorier (icke-samtyckta intima bilder och CSAM) men ändrar enligt de lästa källorna inte art. 5(1)(f) — [CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-omnibus-vii-deadline-delay-20260/)

**Art. 50 (transparens)**
- Leverantörer av system som interagerar direkt med människor, inklusive röstassistenter och konversationsagenter, ska se till att användaren förstår att det är en AI, om det inte är uppenbart. Detta gäller från 2 augusti 2026 och sköts inte upp av omnibusen. Den enda lättnaden gäller art. 50.2 (maskinläsbar märkning) för system som släppts på marknaden före 2 augusti 2026, med ny tidsgräns 2 december 2026 — [CSA PDF](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/07/CSA_research_note_eu_ai_act_article_50_transparency_20260729-csa-styled-1.pdf); [Baker Botts](https://www.bakerbotts.com/thought-leadership/publications/2026/september/eu-ai-act-article-50-transparency-obligations-go-live); [Stephenson Harwood](https://perspectives.stephensonharwood.com/post/102nfqh/eu-ai-act-update-european-commission-adopts-guidelines-on-article-50-transparenc)
- Kommissionens riktlinjer om art. 50 ska ha antagits omkring 20 juli 2026 (inte läst i original) — [Stephenson Harwood](https://perspectives.stephensonharwood.com/post/102nfqh/eu-ai-act-update-european-commission-adopts-guidelines-on-article-50-transparenc)
- Brott mot art. 50 kan ge sanktionsavgifter på upp till 15 MEUR eller 3 % av global omsättning — [Baker Botts](https://www.bakerbotts.com/thought-leadership/publications/2026/september/eu-ai-act-article-50-transparency-obligations-go-live)

### Inferences (produktkonsekvenser, att verifiera med jurist)
- **Agenters röst:** Om prosodi, tonläge eller röststress hos agenten används för att dra slutsatser om stress, ilska, entusiasm eller "säkerhet" och resultatet når arbetsgivaren, är det med stor sannolikhet förbjudet sedan februari 2025. Det gäller oavsett vad avtalet säger, och sanktionsnivån för art. 5 är upp till 35 MEUR eller 7 %. Säkrast är att inte alls ha röstbaserade känslomodeller på agentsidan, och att tekniskt kunna stänga av all paralingvistisk analys per talarkanal.
- **Text kontra biometri:** Riktlinjerna definierar emotionsigenkänning utifrån biometriska data. Textbaserad analys av transkriptet (vad som sägs, t.ex. invändningar, nämnda konkurrenter, "kunden uttrycker missnöje med priset") faller enligt de kommentarer som lästs utanför art. 5(1)(f). Gränsen är omstridd när textanalysen används för att dra slutsatser om agentens känslotillstånd, så det är försiktigast att inte märka agenter med känslor alls. "Köpintention" som slutsats från kundens ord om behov, budget och tidplan är affärssemantik, inte känsla. Om den härleds från kundens röstton blir den emotions- eller avsiktsigenkänning på biometrisk grund (definitionen omfattar även "intentions"). Det är tillåtet för kunder men utlöser art. 50.3 och möjligen högrisk enligt bilaga III.1 c.
- **Kunders känslor via röst:** Inte förbjudet, men användaren (deployer) måste enligt art. 50.3 informera de som exponeras. Sedan 2 augusti 2026 bör det alltså finnas ett uttryckligt meddelande som även nämner AI-analys. Röstbaserad emotionsigenkänning av kunder kan också vara högrisk enligt bilaga III.1 c från 2 december 2027.
- **Högrisk enligt bilaga III.4 b:** QA-poäng, rankning av agenter och underlag för lön, bonus eller uppsägning är "monitor and evaluate performance and behaviour" och därmed högrisk från 2 december 2027. Det kräver riskhantering, datastyrning, teknisk dokumentation, loggning, mänsklig tillsyn, CE-märkning/EU-registrering för leverantören samt information till arbetstagare och arbetstagarrepresentanter (art. 26.7) för användaren. Leverantören kan pröva art. 6.3-undantaget (smal procedurell uppgift) för rena sammanfattningar eller transkript, men inte för poängsättning av personer.
- **Röstagenter:** En AI-agent som ringer eller tar emot samtal måste säga att den är en AI från 2 augusti 2026 (art. 50.1).

### Gaps
- Kommissionens riktlinjer har inte lästs i original (punktnumrering, exakt formulering om "sentiment" och "intentions" och om textbaserad analys). Läs PDF:en på digital-strategy.ec.europa.eu.
- Det är inte bekräftat om omnibusen ändrade art. 4 (AI-kunnighet) eller tillförde lättnader för små och medelstora företag (SMF/SMC) som påverkar en startup.
- Det är inte bekräftat vilken svensk myndighet som har utsetts till marknadskontrollmyndighet för AI-förordningen.

## 5. Svenska sektorregler: inspelning, telefonförsäljning och finans

### Takeaway
Ensidigt samtycke räcker straffrättsligt (part i samtalet). För telefonförsäljning till konsument gäller sedan 1 september 2018 skriftlighetskravet: avtalet är ogiltigt om konsumenten inte skriftligen accepterar efter samtalet. NIX-Telefon är självreglering. En statlig utredning (redovisning senast 15 januari 2027) prövar starkare spärregister eller förbud. Inom finans kräver MiFID II art. 16(7) inspelning av samtal som rör order och transaktioner, med 5 års lagring (7 år på begäran av myndigheten).

### Cited Findings
- Skriftlighetskravet (2 kap. 3 a § lagen (2005:59) om distansavtal och avtal utanför affärslokaler, i kraft 1 september 2018): när näringsidkaren själv ringer konsumenten ska anbudet bekräftas i varaktig form, och konsumenten måste acceptera skriftligen efter samtalet, annars är avtalet ogiltigt — [Prop. Skriftlighetskrav vid telefonförsäljning](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/proposition/skriftlighetskrav-vid-telefonforsaljning_h503129/html/); [Lawline](https://lawline.se/answers/ar-jag-bunden-av-avtalet-med-telefonforsaljaren)
- Konsumentverket ansåg 2022 att telefonförsäljning fortfarande orsakar stora problem och har föreslagit ett generellt förbud — [Konsumentverket remissvar](https://www.regeringen.se/contentassets/5d59e25f76bb4f85a2c2ea5e3cde30dc/konsumentverket.pdf); [Motion 2025/26:3649](https://data.riksdagen.se/dokument/HD023649)
- Regeringen tillsatte i juli 2026 en utredare ("Ett starkt konsumentskydd vid telefonförsäljning", Fi) som ska analysera ett förstärkt spärregister och överväga förbud. Redovisning senast 15 januari 2027 — [Regeringen](https://www.regeringen.se/contentassets/4d7e166bffd143f781a4edeab6aa38ae/ett-starkt-konsumentskydd-vid-telefonforsaljning-hr202601525/)
- I dag får telefonförsäljning ske så länge konsumenten inte tydligt motsatt sig det, och konsumenten kan registrera sig i NIX-Telefon — [Regeringen](https://www.regeringen.se/contentassets/4d7e166bffd143f781a4edeab6aa38ae/ett-starkt-konsumentskydd-vid-telefonforsaljning-hr202601525/)
- Finland har skärpt reglerna för telefonförsäljning i konsumentskyddslagen. Avtalet binder inte konsumenten utan skriftligt godkännande (finsk rätt, inte svensk) — [Statsrådet FI](https://valtioneuvosto.fi/sv/-/1410853/reformen-av-konsumentskyddslagen-skarper-reglerna-for-telefonforsaljning)
- MiFID II art. 16(7): inspelning av telefonsamtal och elektronisk kommunikation som rör handel för egen räkning och mottagande, vidarebefordran och utförande av kundorder, även när ingen transaktion blir av. Lagring 5 år, förlängt till 7 år om behörig myndighet begär det. Lagringstiden räknas från när posten skapas — [ESMA Q&A](https://www.esma.europa.eu/node/204124); [Hogan Lovells](https://www.hoganlovells.com/-/media/hogan-lovells/pdf/mifid/new_mifid_update_31_dec_2016/lwdlib015463830v1mifid_ii_telephone_and_email_recording_23_12_2016pdf.pdf); detaljregler i delegerade förordningen (EU) 2017/565 — [Womble Bond Dickinson](https://www.womblebonddickinson.com/uk/insights/articles-and-briefings/mifid-2-keeping-it-record)

### Inferences
- **Produktmöjlighet inom telefonförsäljning:** Kontroll att anbudsbekräftelsen skickats och accepterats, att NIX kontrollerats, att säljaren presenterat sig, och flaggning av vilseledande påståenden (marknadsföringslagen). Utredningen 2027 kan leda till förbud eller opt-in för telefonförsäljning till konsument. Den B2C-utgående säljmarknaden kan alltså krympa, så B2B-sälj och kundtjänst är tryggare målgrupper.
- **Finans:** MiFID-inspelningar har egen laglig grund (art. 6.1 c) men bara för MiFID-ändamålet. Att återanvända samma inspelningar för AI-coachning kräver en prövning av förenliga ändamål (art. 6.4) eller egen laglig grund. Bank och försäkring kräver också utkontrakteringsregler (EBA/FI om utkontraktering, DORA för IKT-tredjepartsrisk). Dessa har inte undersökts här.

### Gaps
- FI:s egna föreskrifter eller tillsyn om inspelning och svensk tillämpning av art. 16(7) och art. 76 i 2017/565 hittades inte.
- Försäkringsdistribution (IDD), energi (Ei) och telekom (PTS, LEK) saknar kontrollerade inspelningskrav.
- DORA och EBA:s riktlinjer om utkontraktering för leverantörer till banker har inte undersökts.
- Ingen källa bekräftar en "telemarketinglag 2022" i Sverige. Det som finns är regeln från 2018 och utredningen 2026–27. Uppgiften om 2022 avser sannolikt Finland eller Konsumentverkets remissvar 2022.
- Norsk, dansk och finsk rätt om samtalsinspelning och regler motsvarande MBL (t.ex. norska arbeidsmiljøloven kap. 9, danska samarbetsavtal) har inte undersökts.
