# Teknikstack och enhetsekonomi: svensk samtalsanalys (efter samtal och i realtid)

Läget i oktober 2026. Valutaantagande: 10,5 SEK/USD. EUR-priser omräknas med Hetzners egna USD-uppgifter där de finns, annars ungefär 1 EUR ≈ 1,1 USD (antagande).
Metodnot: WebFetch mot huggingface.co misslyckades (DNS). Nästan alla siffror nedan kommer från sökutdrag. Där källan är tredjepart eller en konkurrent står det. **Kontrollera alla priser på leverantörens egen sida innan de används i en offert.**

Antaganden för kostnadsmodellen (används under "Inferences"):
- Ett genomsnittligt säljsamtal eller kundtjänstsamtal är 5–10 min.
- Svenskt samtalstal ger cirka 150 ord/min, vilket blir ungefär 250–300 tokens/min. Ett samtal på 10 min blir alltså cirka 3 000 tokens transkript. Detta är en uppskattning och inte uppmätt; kör `count_tokens` på riktiga transkript.
- Systemprompt och JSON-schema för signalextraktion är cirka 3 000 tokens och cachas.

## 1. Svensk ASR: kvalitet, strömning, pris och EU-residens

### Takeaway
KB-Whisper (KBLab, öppen) har lägst publicerad svensk WER och nästan ingen marginalkostnad när man kör den själv. Den passar därför bäst som MVP-motor för batch efter samtal. För realtid saknar Whisper inbyggd strömning, så kommersiella strömnings-API:er (AssemblyAI EU, ElevenLabs Scribe v2 Realtime, Azure, Speechmatics) blir aktuella för 0,15–1,00 USD/h. Det finns **ingen oberoende benchmark på svensk 8 kHz-telefoni**, så ett eget testset av riktiga samtal behövs innan valet görs.

### Cited Findings
**KB-Whisper (KBLab / Kungliga biblioteket)**
- Tränad på mer än 50 000 timmar svenskt tal (undertexter, riksdagstal, dialektarkiv). Bästa modellen sänker WER med i snitt 47 % mot whisper-large-v3 på FLEURS, CommonVoice och NST. — [KBLab/kb-whisper-large, modellkort](https://huggingface.co/KBLab/kb-whisper-large); [arXiv 2505.17538 "Swedish Whispers"](https://arxiv.org/pdf/2505.17538v2)
- WER för large: KB 5,4 / 4,1 / 5,2 mot OpenAI large-v3 7,8 / 9,5 / 11,3 (FLEURS / CommonVoice / NST). — [modellkort via sökutdrag](https://huggingface.co/KBLab/kb-whisper-large)
- kb-whisper-small ska slå whisper-large-v3 på svenska trots att den är cirka 6 gånger mindre. — [kb-whisper-small](https://huggingface.co/KBLab/kb-whisper-small)
- Förbehåll: siffrorna är KBLabs egna mätningar. Tredjepartssajter upprepar dem utan att ha gjort egen utvärdering. FLEURS och CommonVoice är uppläst tal och inte telefonsamtal. — [PromptLayer](https://www.promptlayer.com/models/kb-whisper-large); [VexaScribe](https://vexascribe.com/sv/kb-whisper)

**Kommersiella API:er (svenska siffror där de finns)**
- Speechmatics svenska sida (FLEURS, leverantörens egen tabell): Speechmatics Enhanced 8,16 % WER, Microsoft Azure 13,13 %, Google Chirp 2 20,58 %, Deepgram Nova-2 13,82 %. Sidan verkar delvis inaktuell och inkonsekvent. — [Speechmatics Swedish STT](https://www.speechmatics.com/speech-to-text/swedish)
- Speechmatics-pris: säljstyrt. Tredjepartsuppgifter är Enhanced cirka 0,0125 USD/min (0,75 USD/h) och "Melia 1" 0,12 USD/h. Uppgifterna går isär. — [convertaudiototext.com](https://convertaudiototext.com/blog/speech-to-text-api-pricing-2026); [vexascribe.com](https://vexascribe.com/compare/best-transcription-api-for-developers)
- ElevenLabs Scribe v2 Realtime: 0,39 USD/h (cirka 0,0065 USD/min) i listpris, 0,28 USD/h på årliga Business-avtal. Leverantören uppger cirka 150 ms latens och "93,5 % accuracy across 30 languages" på FLEURS. Svenska nämns inte specifikt. — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api); [ElevenLabs realtime](https://elevenlabs.io/realtime-speech-to-text)
- Soniox påstår att Scribe v2 Realtime ligger efter Soniox på brusig och konverserande svenska. Det är konkurrentmarknadsföring och inte verifierat. — [Soniox vs ElevenLabs (sv)](https://soniox.com/compare-stt/soniox-vs-elevenlabs/swedish)
- AssemblyAI: Universal-3.5 Pro async cirka 0,21 USD/h, Universal-2 0,15 USD/h, strömning från 0,15 USD/h. EU-regionen (`api.eu.assemblyai.com` / `streaming.eu.assemblyai.com`) kostar lika mycket som US. Diarisering är ett tillägg (exempelvis +0,02 USD/h). — [AssemblyAI pricing reference](https://www.assemblyai.com/pricing.md). En tredjepartskälla uppger att strömning debiteras efter hur länge socketen är öppen och inte efter skickat ljud. — [costbench](https://www.costbench.com/software/ai-transcription-apis/assemblyai/hidden-costs/)
- Deepgram Nova-3: källorna går isär. Monolingual 0,0048–0,0077 USD/min, multilingual 0,0058–0,0092 USD/min. Diarisering cirka +0,002 USD/min och keyterm prompting cirka +0,0013 USD/min. Ingen källa bekräftar svenska; "31 språk" nämns. — [HappyRobot](https://www.happyrobot.ai/hub/deepgram-pricing); [Soniox vs Deepgram](https://soniox.com/pricing/stt/soniox-vs-deepgram); [costbench](https://www.costbench.com/software/ai-transcription-apis/deepgram/). AssemblyAI:s jämförelsetabell (konkurrent) anger Nova-3 till cirka 0,26 USD/h batch och "No" för EU-residens. — [AssemblyAI blogg](https://www.assemblyai.com/blog/speech-to-text-api-pricing)
- Azure AI Speech (tredjepart): realtid 1,00 USD/h (cirka 0,017 USD/min), fast transcription 0,36 USD/h, batch 0,18 USD/h (0,003 USD/min). En annan källa anger batch till 0,36 USD/h. — [convertaudiototext.com](https://convertaudiototext.com/blog/speech-to-text-api-pricing-2026); [futureagi.com](https://futureagi.com/blog/speech-to-text-apis-in-2026-benchmarks-pricing-developer-s-decision-guide/)
- Amazon Transcribe: tidigare 0,024 USD/min. En källa från 2026 uppger 0,006 USD/min batch och 0,010 USD/min strömning (us-east), med lägre volymsteg. Uppgiften är osäker. — [convertaudiototext.com](https://convertaudiototext.com/blog/speech-to-text-api-pricing-2026)
- Google Chirp 3 (V2 API): 0,016 USD/min standard, 0,003–0,004 USD/min i dynamisk batch med 24 h leveranstid. — [convertaudiototext.com](https://convertaudiototext.com/blog/speech-to-text-api-pricing-2026); [AssemblyAI om Google-alternativ](https://www.assemblyai.com/blog/google-cloud-speech-to-text-alternatives)
- Det enda relevanta oberoende arbetet som hittades är en studie från 2024 som jämför Google, Azure och en öppen svensk modell för talare med svenska som förstaspråk (L1) och andraspråk (L2). WER-siffrorna fanns inte i utdraget. — [arXiv 2405.13379](https://arxiv.org/pdf/2405.13379)

### Inferences
- Rangordning för svensk kvalitet, baserad på publicerade siffror som alla är leverantörsmätta och på uppläst tal: KB-Whisper large ≈ bäst (cirka 5 % FLEURS) > Speechmatics (cirka 8 %) > Azure / Deepgram Nova-2 (cirka 13–14 %) > Chirp 2 (cirka 21 %). På 8 kHz-telefoni med dialekter och överlappande tal kan alla siffror förväntas bli flera procentenheter sämre. Rangordningen kan också ändras.
- Whisper-familjen (inklusive KB-Whisper) är en encoder-decoder som arbetar på fönster om cirka 30 s och är inte byggd för strömning. Pseudoströmning med VAD-chunkning går, men ger högre latens och sämre stabilitet än inbyggt strömmande API:er. Det här är en arkitekturslutsats och inte uppmätt.
- Fintuning av KB-Whisper på några hundra timmar egen 8 kHz-telefoni (med samtycke) är den troliga vägen till ett kvalitetsförsprång mot Gong/Cresta på svenska.
- Prisspann per ljudminut för API: batch cirka 0,0025–0,0125 USD (0,03–0,13 SEK), strömning cirka 0,0025–0,017 USD (0,03–0,18 SEK).

### Gaps
- Ingen källa ger svensk WER på 8 kHz-telefoni för någon leverantör.
- Ingen siffra hittades för NVIDIA Canary/Parakeet på svenska, och det framgick inte om svenska stöds. Ingen siffra hittades heller för AssemblyAI Universal eller Deepgram Nova-3 på svenska.
- Whisper large-v3-turbo på svenska mättes inte i de källor som hittades.
- Licens för KB-Whisper (modellkortet gick inte att hämta) behöver kontrolleras. Detsamma gäller vilka leverantörer som har en svensk eller nordisk datacenterregion (Azure Sweden Central och liknande) med garanterad databehandling i EU.
- Open ASR Leaderboard söktes inte specifikt på grund av gränsen för antal verktygsanrop.

## 2. Talardiarisering

### Takeaway
I telefoni är stereoinspelning (agent på en kanal, kund på den andra) den billigaste och mest robusta "diariseringen", och kostar i praktiken 0 kr. pyannote behövs bara för monoinspelningar och möten med flera deltagare. Som API kostar det cirka 0,1 EUR per ljudtimme.

### Cited Findings
- pyannoteAI Precision-2: 0,112 EUR/h på Developer-planen (19 EUR/mån inklusive 165 h) och 0,096 EUR/h på Starter. Enterprise har förhandlat volympris och on-prem. — [pyannoteAI models reference](https://www.pyannote.ai/md/models); [pyannoteAI pricing](https://www.pyannote.ai/pricing); [pyannoteAI blogg 2026](https://www.pyannote.ai/blog/top-7-speaker-diarization-apis-and-models-in-2026)
- pyannote.audio 4.x finns som öppen källkod på PyPI. — [pyannote-audio 4.0.4](https://pypi.org/project/pyannote-audio/4.0.4/)
- Diarisering som tillägg i ASR-API:er: Deepgram cirka +0,002 USD/min ([HappyRobot](https://www.happyrobot.ai/hub/deepgram-pricing)), AssemblyAI cirka +0,02 USD/h ([AssemblyAI pricing](https://www.assemblyai.com/pricing.md)).

### Inferences
- pyannoteAI-pris omräknat: cirka 0,0016–0,0019 EUR/min, ungefär 0,02 SEK/min. Det är litet jämfört med ASR, men blir onödigt om inspelningen redan är stereo.
- Arkitekturrekommendation: kräv dubbla kanaler från CCaaS-integrationen (SIPREC, AudioHook och Amazon Connect levererar normalt separata strömmar för de två riktningarna, men det är inte verifierat här). Använd pyannote bara för möten och mono.

### Gaps
- Ingen DER-siffra för svenska eller telefoni hittades. NeMo-diarisering jämfördes inte.

## 3. Paralingvistik och prosodi utan emotionsigenkänning

### Takeaway
Det mest affärsnyttiga (talandel, avbrott, monologlängd, tempo, pauser, svarstid) kan räknas fram ur ordtidsstämplar och kanalseparerad VAD, utan någon särskild ljudmodell. Det bör hållas fritt från emotionsklassning med tanke på EU AI Act (bakgrundsantagande, se nedan).

### Cited Findings
- Inga källor hittades inom gränsen för verktygsanrop om openSMILE/eGeMAPS för den här tillämpningen.

### Inferences
- Användbara signaler ur ASR plus stereo, med räkneregler (inget eget beroende krävs):
  - Talandel per kanal.
  - Avbrott: överlapp där den andra kanalen redan talar över en viss tröskel.
  - Längsta monolog.
  - Ord per minut från ordtidsstämplar.
  - Pausfördelning och svarstid mellan talarbyten.
  - Antal frågor (via LLM eller frågetecken i transkriptet).
- Tonhöjd (F0) och energi via openSMILE eGeMAPS eller librosa går att ta fram billigt på CPU. Värdet är oklart om det inte används för affekt. Undvik att visa "känsla" eller "stress" hos individer.
- Juridisk riktning, som juristspåret bör verifiera: AI Act förbjuder emotionsigenkänning på arbetsplatsen (art. 5.1 f). Agentens röst analyserad för emotion är därför en riskzon. Det här är bakgrundskunskap och inte källbelagt i den här sökningen.

### Gaps
- Ingen källa söktes fram om openSMILE-licens (kommersiell licens krävs för audEERING:s openSMILE 3.x enligt tidigare kunskap; behöver verifieras) eller om forskning som kopplar prosodiska mått till säljutfall.

## 4. LLM-signalextraktion med Claude: modeller, priser, batch, cachning, utvärdering

### Takeaway
LLM-kostnaden per samtalsminut är försumbar med Haiku 5.5 (cirka 0,0001 USD/min) och liten med Sonnet 5.5 (cirka 0,0007–0,0015 USD/min, med batch och cachning). ASR och telefoniintegration är alltså de stora kostnadsposterna, inte LLM:en. Strukturerad output (`output_config.format`) och Batches API (−50 %) passar analys efter samtal.

### Cited Findings
- Aktuella priser (Anthropics prislista cachad 2026-10-06), per miljon tokens in/ut:
  - Claude Haiku 5.5 (`claude-haiku-5-5`): 0,10 / 0,50 USD för prompter upp till 100K tokens, 0,50 / 2,50 USD över det.
  - Claude Sonnet 5.5 (`claude-sonnet-5-5`): 2 / 10 USD, cacheläsning 0,20 USD.
  - Claude Opus 5.5: 4 / 20 USD.
  - Claude Haiku 4.5: 1 / 5 USD.
  - Claude Sonnet 4.6: 3 / 15 USD.

  — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing) (via Anthropics claude-api-referens, cachad 2026-10-06)
- Batches API: asynkron körning till 50 % av priset. Promptcachning: cacheskrivning cirka 1,25× inpris (5 min TTL, 1 h TTL finns), cacheläsning cirka 0,1×. Minsta cachebara prefix är 512–4 096 tokens beroende på modell. — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing); [Prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- Strukturerad output: `output_config: {format: ...}` eller `strict: true` på verktyg garanterar giltig JSON enligt schema. Påtvingad `tool_choice` returnerar 400 på Sonnet 5.5 och Opus 5.5. Sonnet 5.5 och Haiku 5.5 har tänkande påslaget som standard; tänkandet styrs med `effort`, och på Sonnet 5.5 kan det stängas av med `thinking: {type: "between_tools"}`. Tänkande tokens debiteras som output. — [Anthropic docs: structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- `inference_geo` styr var inferensen körs (Opus/Sonnet 4.6 och senare). — [Anthropic docs](https://platform.claude.com/docs/en/build-with-claude/data-residency)

### Inferences
Räkneexempel för ett samtal på 10 min: cirka 3 000 tokens transkript, 3 000 tokens cachad systemprompt, cirka 800 tokens JSON-output.
- **Haiku 5.5:** 3 000 × 0,10 + 3 000 × 0,01 + 800 × 0,50 per miljon ≈ 0,00073 USD per samtal, alltså cirka **0,00007 USD/min (0,0008 SEK/min)**. Med batch hälften så mycket.
- **Sonnet 5.5:** 3 000 × 2 + 3 000 × 0,20 + 800 × 10 per miljon ≈ 0,0146 USD per samtal, alltså cirka **0,0015 USD/min (0,015 SEK/min)**. Med batch cirka 0,0007 USD/min. Om tänkandet är på med medel effort kan output bli 2–4 gånger större, vilket ger cirka 0,002–0,004 USD/min.
- Flera prompter per samtal (sammanfattning, MEDDIC/BANT-fält, invändningar, compliance-checklista, CRM-fält) multiplicerar kostnaden ungefär linjärt. Även 5 anrop med Sonnet håller sig under cirka 0,01 USD/min (0,1 SEK/min). Rekommendation: Haiku 5.5 för klassning och fält, Sonnet 5.5 för sammanfattning och coachning. Mät kvaliteten, för Haiku 5.5:s pris är anmärkningsvärt lågt mot 4.5.
- Utvärderingsupplägg (eget förslag):
  1. Guldset med 100–300 manuellt annoterade svenska samtal per signal.
  2. Mät precision och recall per fält. För fritext används LLM-domare med rubric, kalibrerad mot människor.
  3. Kör hela pipelinen på ASR-output och inte på rena transkript, så att ASR-fel slår igenom i mätningen.
  4. Kör om utvärderingen vid varje prompt- eller modellbyte.

### Gaps
- Haiku 5.5-priset (0,10 / 0,50 USD) är en tiondel av Haiku 4.5. Det bör dubbelkollas på den officiella prissidan innan det används i offerter.
- Ingen mätning av token per minut svenskt samtalstal. Siffran 250–300 tokens/min är en uppskattning.
- EU-residens för Claude: `inference_geo` stöder "us" enligt dokumentationen. Om det finns ett EU-alternativ på förstapartens API, eller om man behöver gå via Bedrock (Frankfurt/Stockholm) eller Vertex (EU), verifierades inte.

## 5. Telefoni- och CCaaS-integrationsvägar

### Takeaway
För svenska SME:er är den billigaste MVP-vägen att hämta inspelningar och transkript efter samtalet via växel-API:er och webhooks (Telavox, liksom Puzzel och Teams, där API:et inte verifierats). Realtid kräver strömmade mediagränssnitt (Genesys AudioHook, Amazon Connect/Kinesis, Twilio Media Streams, SIPREC). Där tar CCaaS-leverantören ofta egna minutavgifter.

### Cited Findings
- Telavox:
  - Webhook för färdiga transkript kräver Business Transcribe och Call Recording. Den skickar signerade HTTPS-anrop med segment, sammanfattning, action items och taggar. Det finns ett publikt API för att lista och hämta Business-transkriptioner. — [Telavox support: Transcribe webhook](https://support.telavox.com/-personlige-webhooks/transskriber-webhook); [Telavox: Personal and Business transcription](https://support.telavox.com/settings/personal-and-business-transcription)
  - Legacy v1 API kan hämta samtalsljud per inspelnings-id men **fasas ut 31 december 2026**. Migrering till Customer API (CAPI) krävs; ett inspelningsendpoint i CAPI har inte verifierats. — [Telavox developer: calls v1](https://developer.telavox.com/documentation/calls/)
  - Studio API strömmar samtalshändelser (inte ljud) över WebSocket. — [Telavox Studio API](https://support.telavox.com/en_US/settings/studio-api)
  - Telavox har en egen "AI Assist"-webhook, alltså en potentiell konkurrent eller samarbetspartner. — [Telavox UK news](https://telavox.co.uk/whats-new/news-ai-assist-webhook-for-smarter-workflows/)
- Genesys AudioHook Monitor: debiteras per integration och per strömmad minut (pauser debiteras inte). Pris kräver offert. Transcription Connector kostar lika mycket som AudioHook Monitor. — [Genesys: AudioHook Monitor pricing](https://help.genesys.cloud/articles/audiohook-monitor-pricing/); [Genesys: Transcription Connector pricing](https://help.genesys.cloud/362782)
- Amazon Connect external voice: 3 100 USD/mån per extern röstkonnektor plus 0,012 USD per extern röstminut; Contact Lens debiteras utöver detta. — [AWS What's New, maj 2025](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-connect-external-voice-pricing-changes/). Contact Lens har realtidsströmning. — [AWS 2022](https://aws.amazon.com/about-aws/whats-new/2022/03/amazon-connect-contact-lens-real-time-streaming/). En tredjepartskälla anger röst till cirka 0,038 USD/min på AI-inklusiv plan och cirka 0,018 USD/min à la carte. — [Retell AI](https://www.retellai.com/blog/retell-vs-twilio-amazon-connect-vs-genesys-google-ccai)
- Recall.ai (Zoom/Meet/Teams-mötesbottar): Pay As You Go sänktes från 0,70 till 0,50 USD per inspelningstimme i början av 2026, plus 0,15 USD/h för inbyggd transkription. Lagring är gratis i 7 dagar, därefter 0,05 USD/h för 30 dagar. Ingen plattformsavgift, de första 5 h är gratis, och priset beror inte på antal deltagare. Prissidan visade fortfarande 0,70 USD/h i en snapshot. — [Recall.ai blogg](https://recall.ai/blog/new-recall-ai-pricing-for-2026); [Recall.ai pricing](https://www.recall.ai/pricing)

### Inferences
- Integrationsprioritet för den svenska marknaden: (1) Telavox (CAPI, sedan v1 fasas ut) och andra svenska molnväxlar, (2) Teams (via Recall.ai för möten; certifierad compliance recording kräver Microsofts certifieringsprogram), (3) Genesys och Amazon Connect för större kontaktcenter, (4) SIPREC för on-prem eller SBC.
- Recall.ai kostar cirka 0,0083 USD/min (0,09 SEK/min) bara för inspelningen, vilket är mer än ASR med KB-Whisper. Egna mötesbottar sänker kostnaden men kräver mycket underhåll.
- Amazon Connect external voice har en fast avgift på 3 100 USD/mån som bara lönar sig vid stora volymer. Exempel: vid 1 miljon min/mån blir det 0,0031 USD/min fast plus 0,012 USD/min.

### Gaps
- Inget hittades om Puzzels inspelnings- eller ström-API, Twilio Media Streams-pris, SIPREC-implementationer (till exempel open source-mottagare) eller listan över Microsofts certifierade leverantörer av Teams compliance recording och certifieringskostnad. Det beror på gränsen för antal verktygsanrop.

## 6. CRM-återskrivning

### Takeaway
Lime CRM och Upsales (de dominerande svenska SME-CRM:erna) har API-nyckelbaserade integrationer som svenska telefoniappar redan använder för att logga samtal som aktiviteter. Återskrivning är därför tekniskt okomplicerad. HubSpot, Salesforce och Dynamics har väl dokumenterade publika API:er (inte sökta här).

### Cited Findings
- Lime CRM: integration kräver en klient-URL från Limes API-dokumentation och en API-nyckel genererad av en Lime-administratör. Alla in- och utgående samtal registreras som aktiviteter med datum, tid och längd (Lynes-integrationen). — [Lynes help](https://help.lynes.io/en/articles/1767951596-insights); [Lime: Lynes-integration](https://www.lime-technologies.com/en/products/lime-crm/integrations/lynes/). Lime listar redan en AI-samtalsintegration (CallStream AI) i sin marknadsplats. — [Lime: CallStream AI](https://www.lime-technologies.com/en/products/lime-crm/integrations/callstream-ai/). Unified.to har en Lime CRM-konnektor i beta och länkar till docs.lime-crm.com. — [unified.to](https://unified.to/integrations/limecrm.md)
- Upsales: API-nyckel genereras i Upsales och integrationen kommunicerar via API i bakgrunden. CTI finns via Upsales E-phone. — [Telink: Upsales](https://telink.se/en/produkt/upsales); [Telink help](https://help.telink.se/en/articles/1769531489-insights)

### Inferences
- MVP-förslag: skriv tillbaka en sammanfattning plus strukturerade fält (nästa steg, invändningar, affärsstadium) som aktivitet eller anteckning. Unified API:er (Unified.to, Merge) kan täcka HubSpot, Salesforce, Dynamics och Lime i ett lager, men innebär ett nytt beroende och en ny kostnad.
- CallStream AI i Limes marknadsplats tyder på att det finns lokal konkurrens.

### Gaps
- Exakta endpoints för att skapa aktiviteter i Lime och Upsales, liksom rate limits, verifierades inte.

## 7. GPU-hosting i EU mot API

### Takeaway
En enda Hetzner GEX131 (RTX PRO 6000 Blackwell 96 GB, 889 EUR eller 989 USD/mån) kan med stor sannolikhet transkribera hundratusentals samtalstimmar i månaden med KB-Whisper. Marginalkostnaden blir då cirka 0,0005–0,002 USD/min, jämfört med 0,003–0,0125 USD/min via API. Brytpunkten ligger runt 100 000–300 000 samtalsminuter per månad.

### Cited Findings
- Hetzner GEX131: RTX PRO 6000 Blackwell 96 GB, 256 GB DDR5, 2 × 960 GB NVMe, 889 EUR eller 989 USD/mån, eller 1,4247 EUR/h med månadstak. Ingen setup-avgift. — [DataCentreNews UK](https://datacentrenews.uk/story/hetzner-unveils-gex131-blackwell-gpu-server-for-ai); [findstack](https://findstack.com/resources/runpod-vs-hetzner-ollama)
- GEX44 (RTX 4000 SFF Ada 20 GB, cirka 0,33 USD/h) och GEX130 går enligt en recension från oktober 2026 inte längre att beställa. De har ersatts av GEX45 (214 EUR netto/mån) och GEX63. — [wz-it.com, 2026-10-13](https://wz-it.com/en/blog/hetzner-gpu-server-comparison/); [getdeploying](https://getdeploying.com/hetzner-vs-shadeform)

### Inferences
- Antagande om genomströmning (inte källbelagt här och behöver benchmarkas): Whisper-large med faster-whisper/CTranslate2 på en modern GPU klarar storleksordningen 30–100 gånger realtid i batch. Vid 50 gånger realtid och 30 % beläggning: 720 h × 50 × 0,3 ≈ 10 800 ljudtimmar = 648 000 min/mån. 989 USD / 648 000 ≈ **0,0015 USD/min (0,016 SEK/min)**. Vid full beläggning cirka 0,0005 USD/min.
- Brytpunkt mot AssemblyAI EU (cirka 0,0035 USD/min): 989 / 0,0035 ≈ 280 000 min/mån. Mot ElevenLabs (0,0065 USD/min): cirka 150 000 min/mån. Under det är API billigare och enklare, förutsatt att den svenska kvaliteten räcker.
- GEX45 (214 EUR/mån) räcker sannolikt för en MVP med KB-Whisper small eller medium, eller för large med lägre genomströmning. Fördelar: data stannar i EU (Tyskland/Finland) och ingen tredjelandsöverföring sker.
- Självhostad realtid kräver alltid påslagen kapacitet dimensionerad för högsta samtidighet, vilket ger sämre beläggning och dyrare minuter än batch.

### Gaps
- Scaleway, OVH och Lambda (EU) söktes inte på grund av gränsen för antal verktygsanrop. Ingen uppmätt RTF för KB-Whisper på en specifik GPU hittades.

## 8. Latensbudget i realtid för agent assist

### Takeaway
Agent assist (förslag och checklistor till en mänsklig agent) tål betydligt mer latens än röstagenter. En rimlig budget är 1–3 s från att kunden yttrat sig till att kortet visas. Röstagenter siktar på 500–800 ms.

### Cited Findings
- Röstagenter: cirka 800 ms total budget (endpointing, ASR-final, LLM, verktyg, första TTS-chunk, nätverk). Mänskliga turbyten har en mediangap på cirka 200 ms; mer än 800 ms känns konstigt och mer än 1 500 ms känns trasigt. — [twig.so](https://www.twig.so/blog/voice-ai-agents-latency-budget-800ms)
- 500 ms-mål: ASR 80–200 ms (moln), LLM time-to-first-token 80–400 ms, TTS första ljud 60–120 ms. LLM TTFT är den största variansen. — [generalcompute.com](https://www.generalcompute.com/blog/voice-agents-and-the-500ms-window?agent=true)
- Strömmande ASR plus kvantiserad LLM plus TTS för telekom har visats med RTF under 1. — [arXiv 2508.04721](https://arxiv.org/html/2508.04721v1)
- ElevenLabs Scribe v2 Realtime uppger cirka 150 ms latens. — [ElevenLabs](https://elevenlabs.io/realtime-speech-to-text)

### Inferences
- Föreslagen budget för agent assist:
  - Medieväg (AudioHook/SIPREC/Media Streams till tjänsten): cirka 100–200 ms.
  - Strömmande ASR, partiell till final: cirka 150–500 ms.
  - Trigger-/intentdetektion med regler eller Haiku: cirka 300–800 ms.
  - Hämtning av kunskapsbas och generering av förslag med Haiku eller Sonnet och strömmad output: cirka 0,5–1,5 s.
  - UI-push: cirka 50 ms.

  Totalt cirka 1–3 s.
- Realtidskostnad för LLM: anropas var 15:e s under ett samtal på 10 min blir det cirka 40 anrop med ett växande, cachat transkript. Med Haiku 5.5 (cirka 75 nya tokens, cirka 1 500 cachade, 150 output per anrop) blir det cirka 0,0004 USD/min. Med Sonnet 5.5 cirka 0,005–0,009 USD/min. Cache-TTL på 5 min passar ett pågående samtal.

### Gaps
- Inga publicerade latensmätningar för svensk strömmande ASR. Inga uppgifter om Cresta- eller Gong-arkitekturers faktiska latens.

---

## Sammanställning: kostnad per samtalsminut (inference från ovan, kontrollera före användning)

| Post | MVP efter samtal (batch) | Realtid (agent assist) |
|---|---|---|
| Ljudintag | Växel-API/webhook: cirka 0 (ingår i kundens växel). Möten via Recall.ai: 0,0083 USD | AudioHook/Connect/Media Streams: CCaaS-avgift, ofta 0,005–0,012 USD (offert krävs) |
| ASR | KB-Whisper på Hetzner: 0,0005–0,002 USD. API: 0,0025–0,0125 USD | Strömmande API: 0,0025–0,017 USD (AssemblyAI EU 0,0025, ElevenLabs 0,0065, Azure 0,017) |
| Diarisering | Stereo: 0. pyannoteAI: cirka 0,002 USD | Stereo: 0 |
| Prosodimått | cirka 0 (CPU, ur tidsstämplar) | cirka 0 |
| LLM | Haiku 5.5: 0,0001. Sonnet 5.5 batch: 0,0007–0,002. Flera prompter: under 0,01 | Haiku: 0,0004. Sonnet: 0,005–0,009 |
| Drift, lagring, övrigt | cirka 0,0005–0,001 | cirka 0,001–0,003 |
| **Summa** | **cirka 0,002–0,015 USD/min (cirka 0,02–0,16 SEK/min)** | **cirka 0,01–0,045 USD/min (cirka 0,10–0,47 SEK/min)** |

Tolkning: en säljare med 1 000 samtalsminuter per månad kostar cirka 20–160 SEK/mån i rörlig COGS efter samtal och cirka 100–470 SEK/mån i realtid. Det ger mycket god bruttomarginal vid licenspris på 500–1 500 SEK per användare och månad, som är vanligt för konversationsintelligens (prisnivån har inte källbelagts här). De verkliga kostnadsdrivarna är CCaaS-avgifter för realtid, plattformsavgifter för mötesbottar och utvecklingskostnad för integrationer, inte AI-inferensen.
