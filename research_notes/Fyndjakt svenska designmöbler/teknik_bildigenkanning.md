# Teknik: bildigenkänning och värdering av designmöbler från amatörfoton (läge oktober 2026)

Researcher-anteckningar. Alla priser i USD om inget annat anges. SEK-omräkningar använder ett *antaget* kurs­värde på ca 10 SEK/USD (ej källbelagt, kontrollera dagskurs). Några verktyg kunde inte hämta arxiv.org, ai.google.dev eller nyris.io (DNS-fel i miljön), så vissa siffror kommer från sökresultatens sammanfattningar och tredjepartsaggregat. Det framgår vid varje sådan uppgift.

## 1. Bild-embeddings för finkornig produkt- och instansigenkänning (CLIP/SigLIP 2/DINOv2/DINOv3, finjustering)

### Takeaway
Ingen publicerad benchmark jämför de här modellerna specifikt på igenkänning av designmöbelmodeller. Den närmaste evidensen på instansnivå (mini-ILIAS) visar att DINOv3 är starkast vid lokal matchning på patchnivå. SigLIP med en enkel linjär adaption är starkast som global embedding. Rekommendationen blir att köra båda som kandidatgeneratorer och utvärdera på ett eget testset på 200–500 Blocket-foton. Metric learning (ArcFace) på hela backbonen är standardvägen när man har hundratals till tusentals märkta bilder, men jag hittade inga publicerade siffror på förbättringen för möbler.

### Cited Findings
- **mini-ILIAS (instansretrieval, arXiv 2512.12610 "Patch-wise Retrieval"):** Med global embedding (L0) når DINOv3 mAP@1k 0,2180 och SigLIP 0,2041. SigLIP med linjär adaption (ILIAS-baslinjen) når 0,3386. Med patchmatchning (L2/L3) leder DINOv3 med 0,3954/0,4298, mot 0,3924/0,4048 för adapterad SigLIP. Slutsatsen är att DINOv3 tjänar mest på lokal matchning och att adapterad SigLIP är bäst globalt. — [arXiv 2512.12610](https://arxiv.org/pdf/2512.12610) (siffrorna kommer från sökresultatets sammanfattning, eftersom fulltexten inte gick att hämta)
- Enligt RADIO1D (2026) slår DINOv3 i genomsnitt SigLIP2 på per-token ImageNet k-NN. Det är en proxy för klassificering, inte för instansretrieval. — [arXiv 2607.03624](https://arxiv.org/pdf/2607.03624)
- Metas egna linear-probe-resultat på ImageNet: SigLIP 2 89,1 %, PE-Core 89,3 % och DINOv3 88,4 %. Modellerna byter alltså plats beroende på uppgift. — [The Batch / DeepLearning.AI](https://www.deeplearning.ai/the-batch/metas-dinov3-gets-an-updated-loss-term-and-improved-vision-performance)
- På en tredjeparts benchmark för visuell produktsökning (nyris VPS benchmark) har DINOv2-Large 40,16 % P@1 på ett IKEA-möbeldataset. Det är en enskild källa och oberoende granskning saknas. Siffran pekar ändå på att zero-shot-embeddings ensamma inte räcker för exakt modellidentifiering av möbler. — [nyris VPS benchmark – DINOv2 Large](https://vpsbenchmark.nyris.io/models/facebook_dinov2-large)
- DeepFurniture innehåller 24k rumsbilder, 170k möbelinstanser och 20k unika möbelidentiteter. Uppgiften är att hitta rätt identitet i en databas utifrån en detekterad instans, och den mäts med top-k-accuracy. Datasetet är ett relevant öppet tränings- och testset för domänen. — [arXiv 1911.09299](https://arxiv.org/pdf/1911.09299)
- 3D-FUTURE är ett stort annoterat möbelrepositorium. Ett arbete om cross-domain-retrieval (foto till 3D-form) rapporterar 69,1 % top-1. — [arXiv 2010.12238](https://arxiv.org/pdf/2010.12238)
- Decorum (2025) rapporterar att CLIP-baserad retrieval är klart sämre än deras språkbaserade metod för *stilvillkorad* möbelretrieval i 3D-FUTURE. — [arXiv 2503.18155](https://arxiv.org/pdf/2503.18155)
- **Finjustering:** "All You Need to Know About Training Image Retrieval Models" (2025) rekommenderar DINOv2-base framför DINOv2-small och ResNets som utgångspunkt. CLS-features fungerar bäst, och studien rekommenderar att finjustera *alla lager* med Adam och lr ≈ 1e-6. — [arXiv 2503.13045](https://arxiv.org/html/2503.13045v1)
- ArcFace på CLIP-backbone i retail hanterar obalanserade dataset bättre än softmax, även när softmax kombineras med balanseringstekniker. — [arXiv 2312.10282](https://arxiv.org/html/2312.10282v2)
- För nischad finkornig retrieval utan stora datamängder är det praxis att finjustera ett förtränat nät. Det sista embeddinglagret kan överanpassas, och lagret före ger ibland bättre retrieval. — [arXiv 1803.03310](https://arxiv.org/pdf/1803.03310)
- En communitytråd om finkornig bilklassificering rapporterade ca 92 % med SigLIP2 SO400M och viktad k-NN. Datasetet var litet och resultatet är anekdotiskt. — [Reddit-snapshot](https://reddit.sentinel-team.org/posts/1uqtamz/snapshots/2026-07-09T20%3A50%3A09.14801Z)

### Inferences
- **Rekommenderad startpunkt:** SigLIP 2 (So400m eller B/16) för global kandidatretrieval. Den har också en textgren, så samma index kan sökas med text som "Bruno Mathsson Pernilla" eller "Hans Wegner CH24". Lägg till DINOv3 ViT-B/L som andra kanal, gärna med patchnivå-reranking av topp-50. Kombinera kanalerna med reciprocal rank fusion.
- Möbelmodeller skiljer sig ofta i små detaljer, som armstödsform, benprofil och klädsel/sits. Därför bör patch- eller lokal reranking (DINOv3 patch-tokens, eller klassiskt SuperPoint/LightGlue) ge mer än för vanliga produkter.
- Med 10–50 referensbilder per modell för några hundra modeller kan en ArcFace- eller sub-center-ArcFace-head på frusna features tränas på minuter på CPU eller en billig GPU. Det kräver mindre data än en full finjustering och är ett bra första steg. Rimliga förväntningar, som inte är källbelagda, är en tydlig ökning av recall@1. Mät det på ett eget testset.
- Ett inzoomat foto av en etikett eller stämpel ska inte jämföras med helbilder. Klassificera först bildtypen (helbild, detalj eller etikett) med zero-shot-CLIP-text och routa sedan.

### Gaps
- Jag hittade ingen benchmark som jämför CLIP, SigLIP 2, DINOv2, DINOv3 och EVA-CLIP specifikt för möbelmodellidentifiering från amatörfoton.
- Inga publicerade gain-siffror för ArcFace eller triplet på små möbeldataset (100–5000 bilder).
- Pinterest Shop-the-Look och Amazon visual search gav inga offentliga möbelspecifika jämförelser i sökningarna.
- Jag kunde inte verifiera nyris-benchmarkens metodik, eftersom sidan inte gick att hämta.

## 2. Vektorsök vid 100k–1M referensbilder (pgvector, Qdrant, LanceDB, FAISS)

### Takeaway
Vid 100k–1M vektorer är problemet litet. pgvector (HNSW) i samma Postgres som annonsdatan är enklast för en ensam utvecklare. Qdrant ger något bättre latens och filtrering men är en tjänst till att drifta. FAISS eller LanceDB in-process räcker om indexet byggs offline. Kostnaden styrs av RAM, och en VPS med 8–16 GB räcker.

### Cited Findings
- I ett test med 1,18 miljoner vektorer och samma HNSW-inställningar på en maskin var spridningen mellan snabbaste och långsammaste motor (Qdrant, Weaviate, Milvus, pgvector) vid matchad recall ca 2x i latens, 4x i disk och över 4x i toppminne. — [ComputingForGeeks](https://computingforgeeks.com/qdrant-weaviate-milvus-pgvector/)
- Ett leverantörstest med 50M vektorer (768-dim, 128 GB-maskiner) visade att Qdrant hade bättre enkelfrågelatens vid 99 % recall. pgvectorscale-sidan lyfter i stället kostnad och genomströmning. — [Instaclustr](https://www.instaclustr.com/education/vector-database/pgvector-vs-qdrant-5-key-differences-and-how-to-choose/.md); [Tiger Data](https://www.tigerdata.com/blog/pgvector-vs-qdrant)
- Ett hostingföretag uppskattar att Qdrant med 1M 768-dim-vektorer i minnet kräver en VPS med minst 16 GB RAM. Det är en leverantörsuppskattning och inget mätvärde. — [Valebyte](https://valebyte.com/blog/vector-db-на-vps-pgvector-vs-qdrant-vs-weaviate-что-выбрать/)
- Enligt en blogg kräver 1M vektorer à 1536 dim 6,2 GB i Qdrant och 9,1 GB i pgvector. Metodiken är oklar. — [lucaberton.com](https://lucaberton.com/blog/vector-database-kubernetes-qdrant-milvus-pgvector-2026/)

### Inferences
- **Räkneexempel:** 1M × 768 float32 ≈ 3 GB rådata och 1M × 1152 (SigLIP2 So400m) ≈ 4,6 GB, plus HNSW-overhead. Med halfvec (fp16) i pgvector eller scalar quantization i Qdrant halveras eller kvartas det. Det betyder att en VPS med 8 GB RAM, ca 10–25 USD i månaden (prisnivån är inte källbelagd), räcker till ca 1M bilder.
- Ett referensindex för designmöbler blir troligen mycket mindre än 1M. Ett par tusen modeller × 20–100 bilder ger ca 50k–200k vektorer, och då räcker FAISS (flat eller IVF) i minnet utan separat databas.
- Rekommendation: Postgres + pgvector med `halfvec` och HNSW. Annonser, sålda objekt och embeddings ligger då i en databas, och SQL-filter (kategori, pris, region) kombineras med vektorsök.

### Gaps
- Jag fick inga exakta RAM-siffror per motor vid 1M från ComputingForGeeks, eftersom artikeln inte hämtades i sin helhet.
- LanceDB testades inte i någon källa jag hittade.

## 3. Vision-LLM-API:er 2026: pris per bild, tillförlitlighet, promptmönster

### Takeaway
Claude Haiku 5.5 kostar 0,10 USD/MTok in (0,05 i batch) och är billigt nog för att granska varje annons som passerat förfiltret. Ett anrop med 3 annonsfoton och 5 referensbilder kostar ca 0,001 USD. Sonnet 5.5 (2 USD/MTok) eller Opus 5.5 (4 USD/MTok) passar sista steget för de få fynd som ser värdefulla ut. VLM:er hallucinerar om attribution för små, roterade eller suddiga bilder. VLM:n ska därför jämföra mot konkreta kandidatbilder från retrieval och svara i strikt JSON med möjligheten "ingen match", inte namnge formgivare fritt.

### Cited Findings
- **Claude-priser per MTok (in/ut), officiell sida:** Haiku 5.5 0,10/0,50 för prompter ≤100k tokens (0,50/2,50 över 100k). Haiku 4.5 1/5. Sonnet 5.5 2/10. Sonnet 5 2/10. Sonnet 4.6 3/15. Opus 5.5 4/20. Opus 5 5/25. Fable 5.1 10/50. Batch API ger 50 % rabatt, t.ex. Haiku 5.5 0,05/0,25, Sonnet 5.5 1/5 och Opus 5.5 2/10. Cache-läsning kostar t.ex. 0,01 för Haiku 5.5 och 0,10 för Sonnet 5.5. — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- **Bildtokens för Claude:** kostnaden är ⌈bredd/28⌉ × ⌈höjd/28⌉ visuella tokens. Claude 4.7 och senare har högupplöst nivå med max långsida 2576 px och 4784 tokens. Övriga modeller har max 1568 px och 1568 tokens. En bild på 1000×1000 px blir 1296 tokens och 1920×1080 blir 2691 tokens på den högupplösta nivån. Dokumentationens exempel: 1000×1000 kostar ca 1,30 USD per 1000 bilder på Haiku 4.5 och ca 6,48 USD per 1000 på Opus 5. Rådet är att nedskala när högupplösning inte behövs. — [Claude Vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- **Claudes kända begränsningar:** den kan hallucinera eller göra fel på lågkvalitativa, roterade eller mycket små bilder (under 200 px), räknar bara ungefärligt och läser inte bildmetadata (EXIF). Flera bilder i samma anrop analyseras tillsammans, och dokumentationen rekommenderar etiketterna "Image 1:", "Image 2:" och bild före text. API:t tar upp till 600 bilder per anrop, med en hårdare dimensionsgräns över 20 bilder (≤2000 px). Files API låter samma referensbild återanvändas via file_id. — [Claude Vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- **Gemini (tredjepartsaggregat, ej verifierat mot ai.google.dev):** 3.1 Flash-Lite ca 0,25/1,50 USD/MTok, 2.5 Flash-Lite 0,10/0,40, 3.5 Flash-Lite ca 0,30/2,50 och 3 Flash ca 0,50/3,00. Källorna är delvis motsägelsefulla. — [morphllm](https://www.morphllm.com/gemini-api-pricing); [anotherwrapper 3.5 Flash-Lite](https://anotherwrapper.com/tools/llm-pricing/gemini-3.5-flash-lite); [pricepertoken Gemini 3 Flash](https://pricepertoken.com/pricing-page/model/google-gemini-3-flash-preview)
- **OpenAI (tredjepartsaggregat, motsägelsefulla):** GPT-5 nano 0,05/0,40, GPT-5 mini 0,25/2,00 och GPT-5.4 nano 0,20/1,25 respektive mini 0,75/4,50 (verifierat 26 maj 2026 enligt källan). Jag hittade ingen bildtokenformel. — [computeprices GPT-5 mini](https://computeprices.com/providers/openai/models/gpt-5-mini); [intuitionlabs](https://intuitionlabs.ai/articles/chatgpt-api-pricing-2026-token-costs-limits)

### Inferences
- **Kostnad per verifieringsanrop**, egen beräkning från Anthropics formel och priser. Indata är 3 annonsfoton och 5 kandidatreferenser nedskalade till ca 784×784 px (28×28 = 784 tokens per bild): 8 × 784 ≈ 6,3k tokens plus ca 1k tokens text, alltså ca 7,3k tokens in och ca 300 tokens JSON ut.
  - Haiku 5.5: 7,3k × 0,10/M + 300 × 0,50/M ≈ 0,00088 USD, ca 0,009 SEK. Med batch ca 0,0004 USD.
  - Sonnet 5.5: 7,3k × 2/M + 300 × 10/M ≈ 0,0176 USD, ca 0,18 SEK.
  - Opus 5.5: 7,3k × 4/M + 300 × 20/M ≈ 0,035 USD, ca 0,35 SEK.
  - Kandidat-referensbilderna och den fasta instruktionen kan cache:as eller laddas upp via Files API. Cache-läsning kostar 10 % av inpriset. För OCR av etiketter och stämplar bör detaljbilden i stället skickas i högre upplösning (ca 1500–2500 px, 3–5k tokens).
- **Promptmönster:**
  - (a) *Retrieval-augmented verifiering:* "Är objektet i bild 1–3 samma modell som kandidat A–E? Svara med kandidat-id eller NONE." Det är säkrare än fri identifiering.
  - (b) Strikt JSON-schema (structured outputs/tool use) med fälten `candidate_id`, `match: yes/no/uncertain`, `evidence` (lista med konkreta visuella detaljer), `contradictions`, `label_text_ocr`, `replica_signals` och `photo_quality`.
  - (c) Kräv att modellen listar *motbevis* innan den ger sitt beslut.
  - (d) Kalibrera inte på modellens självrapporterade sannolikhet. Kalibrera i stället ett beslutsfilter på en hold-out-mängd, med retrieval-score, VLM-beslut och om OCR träffade ett tillverkarnamn som features.
  - (e) Kör två oberoende anrop (eller två leverantörer) på de dyraste besluten och kräv samstämmighet.
- VLM:er har starka "priors" mot kända ikoner som Eames, Wegner och Mathsson. Risken för falskt positiv attribution av "in the style of"-objekt är därför hög om kandidatlistan bara innehåller originalet. Lägg medvetet in kända replikor och liknande anonyma modeller som kandidater ("hard negatives").

### Gaps
- Officiella Gemini- och OpenAI-priser kunde inte hämtas direkt (ai.google.dev gick inte att nå från miljön). Verifiera dem innan beslut.
- Jag hittade ingen oberoende mätning av hallucinationsgrad för VLM-attribution av möbler eller antikviteter.

## 4. Funnel-design inom 500–5000 SEK/månad och volym på Blocket

### Takeaway
Det finns ingen offentlig siffra för nya möbelannonser per dag på Blocket. Blocket uppger själv ca 600 000 aktiva annonser totalt över alla kategorier, utan årtal. Med en funnel i fyra steg (text/metadata → embedding → Haiku 5.5 → Sonnet/Opus för toppfynd) blir LLM-kostnaden troligen tiotals till några hundra SEK i månaden, även vid 20 000 nya möbelannonser per dag. Största kostnaden blir i stället datainsamling och hosting.

### Cited Findings
- Blocket uppger att ca 600 000 saker, fordon, jobb, utbildningar och bostäder finns på Blocket dagligen. Värdet av alla annonser 2019 var 690 miljarder SEK. — [Om Blocket, Mynewsdesk](https://www.mynewsdesk.com/se/blocket)
- Möbler och heminredning nämndes redan 2009 som en av de snabbast växande kategorierna. — [Sveriges Radio](https://www.sverigesradio.se/artikel/3383604) (via sökresultat)
- Färdiga Blocket-scrapers finns på Apify och kostar ca 3–5 USD per 1000 resultat. En av dem kan bläddra i kategorin möbler/inredning sorterad på nyast, men Blocket begränsar en sökning till 50 sidor. — [Apify solidcode/blocket-scraper](https://apify.com/solidcode/blocket-scraper); [Apify fervent_bus](https://apify.com/fervent_bus/blocket-scraper)
- `begagnad-mcp` är ett öppet MCP-verktyg för sökning på Blocket och Tradera (search_blocket, get_blocket_item). — [awesome.ecosyste.ms: bjesus/begagnad-mcp](https://awesome.ecosyste.ms/projects/github.com%2Fbjesus%2Fbegagnad-mcp)

### Inferences (kalkyl med *antagen* volym; ersätt med uppmätt volym efter en veckas insamling)
- **Antagande:** 5 000–20 000 nya annonser per dag i möbler/inredning, med i snitt 4 bilder per annons. Siffran är inte källbelagd.
- **Steg 0, insamling:** Med Apify à 3–5 USD per 1000 och 10k annonser per dag blir det ca 300k per månad, alltså ca 900–1500 USD (9–15k SEK) i månaden. *Det spräcker budgeten.* Egen polling av kategorin "nyast" (lätt, respektfull scraping eller officiellt API om det finns) är nödvändig för att hålla 500–5000 SEK. Användarvillkor och robots.txt behöver granskas, och den juridiska bedömningen ligger utanför min scope.
- **Steg 1, text/metadata, deterministiskt och gratis:** regex och ordlista med formgivare (Mathsson, Wegner, Aalto, Jacobsen, Ekström, Malmsten, Svenskt Tenn osv.), tillverkare (Karl Mathsson, Fritz Hansen, Gemla, DUX, Källemo, Svenskt Tenn, Nordiska Kompaniet), modellnamn och nyckelord ("stämplad", "märkt", "60-tal", "teak", "palisander", "dödsbo"). Sätt dessutom en prisgräns och flagga "okända" annonser med vaga texter ("gammal fåtölj", "retro stol"), eftersom sleepers ofta finns just där. Steget filtrerar inte bort något, det bara prioriterar.
- **Steg 2, embeddings, egen CPU/GPU:** Embedda alla bilder och alltså inte bara de förfiltrerade, eftersom de mest underprissatta annonserna ofta saknar formgivarnamn. 40k bilder per dag med SigLIP2-B på CPU är rimligt på en VPS, men jag har ingen källa för genomströmningen. Alternativt kan en spot-GPU köras batchvis. kNN mot referensindexet ger en topp-k och en similarity score. Skicka vidare om score ≥ tröskel *eller* om texten matchar starkt. Siktet är att ca 2–5 % går vidare.
- **Steg 3, Haiku 5.5-verifiering:** 10k × 3 % = 300 anrop per dag ≈ 9 000 per månad × ca 0,0009 USD ≈ 8 USD, ca 80 SEK i månaden. Även om alla 10k annonser per dag skickades (300k per månad) blir det bara ca 270 USD (2,7k SEK). Med batch-API halveras kostnaden, men då försvinner realtiden.
- **Steg 4, Sonnet 5.5 eller Opus 5.5:** Kör bara när Haiku säger "match" och det uppskattade värdet är minst 3x utropspriset, ca 10–30 annonser per dag ≈ 300–900 per månad × ca 0,02–0,035 USD ≈ 6–30 USD i månaden.
- **Totalt:** hosting ca 150–400 SEK + LLM ca 100–600 SEK. Det ryms inom budgeten *om* insamlingen sker utan betald scraper per resultat.
- Pusha larm (e-post, Telegram) för de bästa fynden. Tid till kontakt är avgörande på Blocket, så batch-API passar bara för steg som kan vänta.

### Gaps
- Det finns ingen officiell eller färsk siffra för nya möbelannonser per dag på Blocket, och Schibsteds rapporter hittades inte i sökningarna. Mät volymen själv.
- Om Blocket har ett officiellt partner-API och vilka villkor som gäller för automatiserad insamling undersöktes inte.

## 5. Prisestimering: jämförbara försäljningar, kvantilregression, gles data, osäkerhet

### Takeaway
Akademisk evidens från konstauktioner visar att ML-värdering slår hedoniska regressioner och att visuella features ger en blygsam förbättring. För glesa designmöbeldata är en hierarkisk ansats bäst: kNN över sålda jämförelseobjekt för samma modell, med justering för skick och tid, och reservnivåer via formgivare och kategori. Svaret ska presenteras som ett intervall (P10–P90) med antal jämförelseobjekt, inte som en punkt.

### Cited Findings
- *Machines and Masterpieces* (Aubry, Kräussl, Manso, Spaenjers) använder neurala nät på ca 1 miljon målningsauktioner med visuella och icke-visuella features. Prognoserna utanför urvalet är "dramatiskt bättre" än hedonisk regression. Avvikelser från auktionshusens estimat korrelerar med osålda objekt och sämre framtida avkastning. — [Institut Louis Bachelier / SSRN 3347175](https://institutlouisbachelier.org/en/ilb-publications-en/doi10.2139%252fssrn.3347175)
- En masteruppsats (NOVA Lissabon, 2025) finner att ML slår traditionella metoder, att auktionshusens estimat är biased och att visuella CNN-features förbättrar prognoserna blygsamt. — [run.unl.pt](https://run.unl.pt/bitstream/10362/186115/1/FALL25_60491_Niklas_M_rquez.pdf)
- För möbelpriser i detaljhandeln (2026) presterar gradient boosting (XGBoost) bäst och KNN och linjära modeller sämre. — [Sinop Fen Bilimleri Dergisi](https://dergipark.org.tr/en/pub/sinopfbd/article/1795688)
- Ett fastighetsvärderingspapper (arXiv 2603.12986, 2026) lär sig *vilka* jämförelseobjekt som ska väljas i stället för att använda handsatta regler, så att färre jämförelseobjekt behövs. — [arXiv 2603.12986](https://arxiv.org/html/2603.12986v1)
- I onlineauktioner påverkar priser på liknande produkter, beskrivning, auktionslängd och säljarens rykte slutpriset. — [METU-avhandling](https://avesis.metu.edu.tr/yonetilen-tez/bcb93db0-c501-4f5b-b1a1-371f9b92167b/empirical-studies-on-price-determinants-of-online-auctionswith-machine-learning-applications)

### Inferences
- **Konkret modell:**
  1. *Exakt nivå:* sålda objekt med samma modell-id från Tradera, auktionshus som Bukowskis, Lauritz och Auctionet, och Blocket-annonser som tagits bort. Ta median och IQR efter justering för tid (inflation eller trendindex per formgivare) och skick (multiplikativa faktorer, t.ex. utmärkt 1,0, gott 0,85, behöver renovering 0,5–0,6). Faktorerna är *antaganden* som ska skattas från data.
  2. *Gles data (färre än 5 jämförelseobjekt):* krymp mot nivån formgivare × kategori (empirisk Bayes, krympning i log-pris).
  3. *Kvantilregression* med LightGBM och quantile loss (α = 0,1, 0,5, 0,9) på log-pris med features som modell-embedding (PCA), formgivare, tillverkare, material, ålder, skick, källa (auktion eller privat), säsong och region.
- Utropspris är inte försäljningspris. Skilj på "auktionsklubbat" och "Blocket-begärt". Blocket-annonser som försvinner är bara en svag proxy för försäljning.
- **Presentation:** "Uppskattat andrahandsvärde 4 000–7 500 kr (median 5 500), baserat på 12 sålda objekt 2023–2026. Säkerhet: medel." Visa jämförelseobjekten med bild och länk. Beräkna förväntad marginal = P25-värde − utropspris − transport och avgifter. P25 gör bedömningen konservativ.

### Gaps
- Jag hittade ingen publicerad studie om prismodeller specifikt för skandinaviska designmöbler eller antikmöbler.
- Tillgång till och villkor för historisk data från Auctionet, Bukowskis, Lauritz och Tradera undersöktes inte inom denna scope.

## 6. Replikor, "i stil med", bildkvalitet, active learning och öppna projekt

### Takeaway
Jag hittade ingen dedikerad forskning eller öppen kod för replikdetektering av möbler och inte heller någon "sleeper finder" för Blocket. Det här byggs bäst som ett regel- och evidenslager: etiketter och stämplar via OCR, konstruktionsdetaljer via checklista i VLM-prompten, prisrimlighet och hard negatives i referensindexet. Därtill en human-in-the-loop-kö där varje granskning blir träningsdata.

### Cited Findings
- Claude kan inte avgöra om en bild är AI-genererad och läser ingen EXIF. Det ger begränsat skydd mot manipulerade annonser. — [Claude Vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- Claude kan hallucinera på suddiga, roterade och små bilder. Dokumentationen rekommenderar tydliga bilder och läsbar text och varnar för att hård JPEG-komprimering försämrar OCR. — [Claude Vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- Det finns färdiga scrapers och MCP-verktyg för Blocket och Tradera men ingen logik för fyndvärdering mot historiska slutpriser. Det skiktet får man bygga själv. — [Apify Blocket-scraper](https://apify.com/fervent_bus/blocket-scraper); [begagnad-mcp](https://awesome.ecosyste.ms/projects/github.com%2Fbjesus%2Fbegagnad-mcp)
- Som närmaste forskningsanalogi för attribution och värdering använder konstauktions-ML visuella features. — [Machines and Masterpieces](https://institutlouisbachelier.org/en/ilb-publications-en/doi10.2139%252fssrn.3347175)

### Inferences
- **Replik- och stilsignaler att extrahera:**
  - (a) Etikett eller stämpel finns, och OCR-texten matchar en tillverkardatabas. Det är den starkaste signalen.
  - (b) Proportioner och detaljer jämfört med originalets referensbilder (patchmatchning).
  - (c) Material som inte stämmer med eran, t.ex. spånskiva, stjärnskruvar eller modern skumplast.
  - (d) Annonstext som "replika", "kopia", "i stil med", "à la", "inspirerad av" eller "typ" ger automatisk nedflaggning.
  - (e) Ett pris *mycket* under marknaden tillsammans med många identiska annonser tyder på en nyproducerad kopia.
- **Bildkvalitet:** Beräkna en skärpemetrik (Laplacian-varians) och upplösning per bild. Välj bästa helbild för embedding och bästa detaljbild för OCR, och nedskala resten till ca 768 px för att spara tokens. Om alla bilder är dåliga: markera "osäker" och be om fler bilder i stället för att ge ett beslut.
- **Active learning-loop:**
  1. Varje larm visas i ett enkelt gränssnitt med knapparna rätt modell, fel modell, replika eller osäker.
  2. Varje beslut sparas som ett märkt par (annonsbild, modell-id) eller en hard negative.
  3. ArcFace-headen tränas om varje vecka.
  4. Tröskeln kalibreras om mot precision@larm.
  5. Prioritera granskning med uncertainty sampling, alltså fall nära tröskeln och där retrieval och VLM är oense.
- **Bootstrap av referensindex:** produktbilder från tillverkare och återförsäljare, bilder från avslutade auktioner (med licens- och upphovsrättsgranskning) och DeepFurniture eller 3D-FUTURE för förträning.

### Gaps
- Inga öppna GitHub-projekt eller papper hittades för just replikdetektering av designmöbler, "sleeper"-identifiering på eBay eller Etsy, eller antikidentifiering med ML. Sökningen var begränsad (ca 15 anrop), så de kan finnas.
- Inga kvantitativa data hittades om andelen replikor bland Blocket-annonser för ikoniska modeller.
