# Contact-center conversation AI platforms (Agaton competitors / analogues)

Scope: vendors that analyse customer-service and inside-sales calls (real-time agent assist, auto-QA, coaching, speech analytics, sentiment, compliance, AI agents). Research date 2026-10-17. Method: WebSearch only (WebFetch to uctoday.com / cxtoday.com failed with DNS errors). Most pricing comes from third-party blogs (often competitor-written: eesel, CloudTalk, Ringly, JustCall, getmacha); treat as estimates. Items marked **[training knowledge, unverified]** come from the researcher's background knowledge (cutoff mid-2026), not from a source found in this session. Do not cite them as facts without checking.

## Q1. Typical auto-QA and real-time assist capabilities, claimed ROI, and vendor profiles

### Takeaway
The category has converged on one bundle: transcribe 100% of calls → LLM auto-scores every call against a QA form → targeted coaching. On top of that come real-time assist (live prompts, knowledge answers, next best action, summaries) and, since 2024–25, autonomous AI agents/voicebots. Point solutions (Cresta, Observe.AI, Level AI, Balto, CallMiner, Convin, Enthu) compete with CCaaS suites (NICE, Genesys, Talkdesk, Dialpad, Amazon Connect, Google) that bundle the same features. Claimed ROI is all vendor-reported: about 7–40% lower AHT, 20–30% conversion uplift, "77% ROI" on QA automation. None of it is independently audited.

### Cited Findings

**Category-level / ROI claims (all vendor-reported)**
- Observe.AI: Conversation Intelligence "automatically QA's 100% of human and AI interactions" — [Sacra](https://sacra.com/chat/h/0377fe28-7f0f-4d97-90ac-7312e268caec/)
- Observe.AI customer ServiceFirst (BPO, 2,000 agents) reports 77% ROI from QA automation. Before that, manual QA allowed only ~2 evaluations per agent per month — [Observe.AI ServiceFirst case](https://observe.ai/customers/servicefirst)
- Observe.AI demo page claims a 25% AHT reduction and 10% revenue uplift across 350+ enterprise customers (aggregate marketing claim) — [Observe.AI demo](https://observe.ai/demo)
- Cresta / Snap Finance: AHT down 40%, moved from random sampling to 100% automated QA, containment up from 6% to 33% — [Cresta Snap Finance](https://cresta.com/customers/snap-finance)
- Cresta-hosted announcement (customers unnamed): +20% conversion rate, +25% average order value — [cresta.com](https://cresta.com/?p=19043)
- Holiday Inn story attributed to Cresta (via aggregator Cuspera, page unreliable): bookings conversion +30%, agent attrition from 120% to 60% — [Cuspera](https://cuspera.com/products/cresta-x-13091/customer-story)
- Puzzel Conversational Intelligence (Nordic analogue). Rejsekort (DK): −12% calls, −15% call duration. DSB (DK): tagging accuracy 95–98%, saving 400 h/yr. JFM (DK): +62% CSAT. Spar Nord (DK): +40% CSAT, −25% contact-centre cost (vendor-reported) — [Puzzel CI](https://www.puzzel.com/products/better-experiences-faster-growth-with-conversational-intelligence); [Puzzel EU leaders](https://www.puzzel.com/conversational-intelligence-eu-leaders)

**Analyst positioning**
- 2025 Gartner MQ for CCaaS: Genesys and NICE both claim Leader (11th consecutive year each). These are vendor claims. — [NICE analyst reports](https://www.nice.com/lps/analyst-bundle-reports); [Genesys](https://www.genesys.com/en-gb/resources/the-future-of-the-contact-centre)
- Cognigy claims Leader in the 2025 Gartner MQ for Conversational AI. NICE acquired Cognigy in September 2025. — [Cognigy](https://www.cognigy.com/gartner-magic-quadrant-conversational-ai-2025); [getmacha NICE guide](https://www.getmacha.com/blog/nice-cxone-mpower-complete-guide)
- No 2025/2026 Gartner MQ specifically for "conversation intelligence" or contact-center QA was found. — (search returned none)

### Vendor profiles

**Cresta** (US, point solution, enterprise)
- Modules sold separately: Agent Assist, AI Agent, Conversation Intelligence, Quality Management — [eesel Cresta pricing](https://www.eesel.ai/en/blog/cresta-pricing)
- Real-time voice translation (ES, FR, PT, DE first). AI Agents in 30+ languages (list not public). — [Cresta press release](https://cresta.com/press/cresta-breaks-down-language-barriers-with-real-time-translation-and-multilingual-ai); [Cresta blog](https://cresta.com/blog/cresta-expands-global-reach-with-real-time-voice-translation-and-multilingual-ai-across-the-platform)
- Strengths: strongest real-time + sales-conversion story, which is the closest analogue to Agaton's "buying signals + next best action". Weaknesses: enterprise-only, expensive, US-centric. No confirmed Swedish. **[training knowledge, unverified]** Cresta was spun out of Stanford AI Lab, and its differentiator is mining top performers' behaviours to build real-time hints. It integrates with Genesys, Five9, NICE, Salesforce, Zendesk and Amazon Connect.

**Observe.AI** (US/India, point solution, mid-market–enterprise)
- 100% auto-QA, real-time assist, AI agents ("VoiceAI agents"), runs on AWS. 350+ enterprise customers (vendor claim). — [Sacra](https://sacra.com/chat/h/0377fe28-7f0f-4d97-90ac-7312e268caec/); [Observe.AI demo](https://observe.ai/demo); [CloudTalk](https://www.cloudtalk.io/de/blog/observe-ai-preise/)
- Launched a generative AI suite built on its own "Contact Center LLM" — [Observe.AI](https://observe.ai/customers/servicefirst)
- Weaknesses: implementation costs estimated at $20K–50K+. Enterprise tier with a 100-seat minimum (third-party). — [toolradar](https://toolradar.com/tools/observe-ai/pricing); [getmacha](https://www.getmacha.com/blog/observe-ai-complete-guide)
- No Swedish language info found.

**CallMiner** (US, post-call speech analytics veteran)
- Quote-only pricing. Third-party estimates: $85–100+ per agent/month, average annual contract about $101,865. — [Ringly](https://www.ringly.io/blog/callminer-alternatives); [getmacha](https://www.getmacha.com/blog/callminer-complete-guide)
- **[training knowledge, unverified]** CallMiner Eureka: deep post-call analytics, 100% interaction scoring, compliance/redaction and real-time "RealTime" alerts. Historically has acoustic "emotion"/agitation scoring. Strong in collections and regulated industries. Weakness: heavy, analyst-oriented, slower time to value.

**Balto** (US, real-time guidance specialist)
- Multilingual conversation AI live in 20+ languages (not listed) — [Balto blog](https://www.balto.ai/blog/baltos-multilingual-conversation-ai-is-now-live-in-20-languages/)
- Quote-based pricing. 60-agent minimum, average annual contract about $102K (Vendr data cited on Balto's own comparison page). SelectHub says "from $100/month". — [Balto vs CallMiner](https://www.balto.ai/compare/balto-vs-callminer/); [SelectHub](https://www.selecthub.com/p/call-center-software/balto-ai)
- **[training knowledge, unverified]** Real-time checklists, objection-handling cards, compliance prompts and auto-QA. Strong in US inside sales, insurance and collections. Differentiator is the real-time "guidance" UX overlay.

**Cogito (Verint)**
- Verint acquired Cogito. Real-time AI coaching, CX/EX monitoring, and "proprietary AI models to measure emotional connections between customers and agents". — [parse.gl Verint profile](https://www.parse.gl/brands/verint-com-4); [Dealroom](https://app.dealroom.co/companies/cogito_1_1)
- Most exposed product under EU AI Act Art. 5(1)(f), because it scores agent voice/behaviour in real time (see Q2). No EU-specific statement from Verint found.

**Uniphore**
- "Emotion AI" detects customer tone and sentiment during interactions. Virtual agents identify tone and sentiment at every turn. — [G2 Uniphore](https://g2.com/products/uniphore-uniphore/reviews); [Uniphore brochure](https://www.uniphore.com/brochures/a-new-approach-to-automating-conversations/)
- Capterra language list: English, French, Indonesian, Japanese, Spanish, Vietnamese. No Swedish. — [Capterra](https://www.capterra.co.uk/software/180755/uniphore)
- **[training knowledge, unverified]** Has pivoted to an enterprise "AI agent / business AI cloud" platform. Its Q for Sales acquisition (Emotion AI for video) was a sales product.

**NICE CXone Mpower / Enlighten** (suite)
- CXone Mpower launched June 2024: CXone + Copilot, Autopilot, Actions — [BusinessWire](https://www.businesswire.com/news/home/20240611678712/en); [Silicon UK](https://www.silicon.co.uk/press-release/nice-unveils-cxone-mpower-the-ultimate-cx-aware-ai-offering-providing-continuous-memory-driven-human-and-ai-collaboration)
- Enlighten brand covers Autopilot (self-service), Copilot for Agents, Copilot for Supervisors, XO (voice/text analytics) and Actions. Copilot for Agents gives live summaries, email drafts and KB answers. Cognigy AI agents in 100+ languages (acquired Sept 2025). — [getmacha NICE guide](https://www.getmacha.com/blog/nice-cxone-mpower-complete-guide)
- **[training knowledge, unverified]** Enlighten AI for CX auto-scores "soft-skill behaviours" (empathy, ownership, active listening) on 100% of interactions. Interaction analytics (former Nexidia) is mature. Strong in the Nordics through large enterprises and BPOs.

**Level AI** (US, point solution)
- About $185/agent/month (third-party) — [Ringly](https://www.ringly.io/nl/blog/level-ai-alternatives)
- **[training knowledge, unverified]** Strengths are semantic (intent-based rather than keyword) auto-QA, "QA-GPT", real-time agent assist and VoC analytics. Has received Gartner/G2 recognition in the mid-market.

**Genesys Cloud AI** (suite)
- Speech & text analytics with Swedish (sv-SE) listed as supported. Sentiment and agent empathy analysis for sv-SE (plus da-DK, fi-FI, nb-NO) since April 2024. Extended voice transcription (third-party engine) for Swedish since January 2023. — [Genesys languages](https://help.genesys.cloud/articles/genesys-cloud-supported-languages/); [Release notes April 22, 2024](https://help.genesys.cloud/release-notes/genesys-cloud/april-22-2024/); [Release notes, STA tag](https://help.genesys.cloud/release-notes/genesys-cloud/tag/speech-and-text-analytics/)
- **[training knowledge, unverified]** Genesys Cloud AI includes Agent Copilot (real-time knowledge, summaries, wrap-up codes), AI-assisted evaluation scoring and virtual agents. AI capabilities are sold via "AI tokens" on CX 1–4 licences. Strong Nordic installed base.

**Talkdesk** (CCaaS)
- CX Cloud list prices: Digital Essentials $85, Voice Essentials $105, Elite $145–165 per user/month. Industry Experience Clouds $225+. Typically a 3-year commitment. Estimated real TCO $200–300/user/month. — [TrustRadius](https://tr-web.dev.trustradius.com/compare-products/dialpad-support-vs-talkdesk); [Ringly Talkdesk](https://www.ringly.io/blog/talkdesk-pricing); [Vendr](https://www.vendr.com/marketplace/talkdesk)
- **[training knowledge, unverified]** Talkdesk AI (Copilot, AI Agents, auto-QA, "Interaction Analytics") is bundled.

**Dialpad AI** (UCaaS/CCaaS, own ASR)
- Dialpad Support tiers: Essentials $80, Advanced $115, Premium $150 per user/month (annual). Some editions require a 3-year commitment. — [Ringly Dialpad](https://www.ringly.io/blog/dialpad-pricing); [CloudTalk Dialpad](https://www.cloudtalk.io/blog/dialpad-pricing/)
- **[training knowledge, unverified]** Proprietary ASR and real-time "Ai Recaps", live coach cards, sentiment and auto-QA ("Ai Scorecards"). Language coverage outside EN/ES/FR/DE is limited.

**Convin** (India, budget) and **Enthu.ai** (India/US, SMB auto-QA)
- Enthu.ai: no public price on G2 — [G2](https://g2.com/products/enthu-ai/pricing). Convin: no pricing found.
- **[training knowledge, unverified]** Both are low-cost auto-QA and coaching tools for BPOs. Convin also offers real-time assist and voicebots. They are strong on Indian languages; no known Nordic presence.

**Sprinklr** (Sprinklr Service)
- No useful search results in this session.
- **[training knowledge, unverified]** An omnichannel CCaaS-plus-social platform with AI QM, Copilot and conversational AI. Enterprise-only and complex.

**Google CCAI (Customer Engagement Suite) — baseline**
- Conversational Insights: voice $0.015/min (Standard) or $0.025/min (Enterprise). Quality AI is $50 per named agent/month or $60 per concurrent agent/month. — [Google Insights pricing](https://cloud.google.com/contact-center/insights/pricing)
- Agent Assist: $0.03/min (Standard) or $0.05/min (Enterprise) for voice. Chat summarization $0.006/session. — [Google Agent Assist pricing](https://cloud.google.com/agent-assist/pricing)

**Amazon Connect Contact Lens — baseline**
- Real-time and post-contact conversational analytics are billed per voice minute or per chat message, with no commitments — [AWS Contact Lens](https://aws.amazon.com/connect/contact-lens/features); [AWS 2020 launch](https://aws.amazon.com/about-aws/whats-new/2020/12/contact-lens-amazon-connect-launches-real-time-contact-center-analytics/)
- Swedish (sv-SE) transcription since September 2024 (post-call). Moved to real-time analytics on March 31, 2025. — [AWS Sept 2024](https://aws.amazon.com/about-aws/whats-new/2024/09/amazon-connect-contact-lens-transcriptions-10-languages); [AWS March 2025](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-connect-contact-lens-conversational-analytics-new-languages/); [AWS supported languages](https://docs.aws.amazon.com/connect/latest/adminguide/supported-languages.html)
- Rate: older figure $0.015/min for the first 5M minutes. Current rate not reliably extracted ($0.038/min appears on the pricing page but is not clearly tied to analytics). — [AWS Connect pricing](https://aws.amazon.com/connect/pricing); [getvoip](https://getvoip.com/blog/amazon-connect-pricing/)

**Puzzel (Nordic CCaaS, a relevant extra)**
- Own ASR "trained for European languages and accents". Classification and sentiment run on its transcripts. Danish case studies listed above. — [Puzzel CI](https://www.puzzel.com/products/better-experiences-faster-growth-with-conversational-intelligence)

### Inferences

Feature matrix. ✓ = confirmed in a cited source this session; (✓) = training knowledge, unverified; ? = unknown; ✗ = not offered / not supported per source.

| Vendor | RT agent assist | Auto-QA 100% | Coaching | Speech analytics | Sentiment / emotion | Compliance monitoring | AI agents / voicebots | Swedish |
|---|---|---|---|---|---|---|---|---|
| Cresta | ✓ | ✓ | (✓) | (✓) | (✓) sentiment | (✓) | ✓ (30+ lang) | ? |
| Observe.AI | ✓ | ✓ | (✓) | ✓ | (✓) | (✓) | ✓ | ? |
| CallMiner | (✓) | (✓) | (✓) | (✓) core | (✓) acoustic emotion | (✓) strong | ✗/(partner) | ? |
| Balto | (✓) core | (✓) | (✓) | (✓) | (✓) | (✓) strong | ? | ? (20+ lang, unlisted) |
| Cogito / Verint | ✓ core | (✓) via Verint | ✓ | (✓) via Verint | ✓ emotion/behaviour | (✓) | (✓) Verint bots | ? |
| Uniphore | (✓) | (✓) | ? | (✓) | ✓ "Emotion AI" | ? | ✓ | ✗ per Capterra |
| NICE CXone Mpower | ✓ Copilot | (✓) Enlighten | ✓ Copilot Supervisor | ✓ XO | (✓) | (✓) | ✓ Autopilot/Cognigy | (✓) |
| Level AI | (✓) | (✓) core | (✓) | (✓) | (✓) | (✓) | (✓) | ? |
| Genesys Cloud AI | (✓) Copilot | (✓) | (✓) | ✓ | ✓ sentiment + empathy (sv-SE) | (✓) | (✓) | ✓ |
| Talkdesk | (✓) | (✓) | (✓) | (✓) | (✓) | (✓) | (✓) | ? |
| Dialpad AI | (✓) | (✓) | (✓) | (✓) | (✓) | ? | (✓) | ? (likely ✗) |
| Convin | (✓) | (✓) | (✓) | (✓) | (✓) | (✓) | (✓) | ? |
| Enthu.ai | ✗/(?) | (✓) core | (✓) | (✓) | (✓) | (✓) | ✗ | ? |
| Sprinklr | (✓) | (✓) | (✓) | (✓) | (✓) | (✓) | (✓) | ? |
| Google CCAI | ✓ | ✓ Quality AI | ? | ✓ | (✓) | ? | ✓ (Dialogflow) | (✓) |
| Amazon Contact Lens | ✓ RT alerts | (✓) evaluations | ? | ✓ | (✓) sentiment | (✓) | ✓ (Lex/Q) | ✓ RT since 3/2025 |

- Real-time vs post-call: Cresta, Balto and Cogito are real-time-first. CallMiner, Enthu and Convin are post-call-first. Observe.AI and Level AI started post-call (QA) and added real-time. The suites do both.
- Closest Agaton analogues on the sales side (buying signals + NBA): Cresta and Balto. On QA + coaching: Observe.AI, Level AI and Enthu. Puzzel is the Nordic CCaaS whose built-in Conversational Intelligence competes directly for Nordic CI budgets.
- Integrations (Genesys/NICE/Five9/Salesforce/Zendesk): **[training knowledge, unverified]** Point solutions (Cresta, Observe.AI, Level AI, Balto, CallMiner) all market Genesys, NICE, Five9, Amazon Connect, Twilio, Salesforce and Zendesk connectors. **No source found** showing a native integration with Puzzel, Telavox or Microsoft Teams (as telephony) for any US point solution. That gap is likely a local-player advantage for Agaton.

### Gaps
- Integration lists per vendor (especially Puzzel, Telavox, Teams) could not be verified, because vendor pages were not fetched.
- No independent (non-vendor) ROI studies found.
- No Forrester Wave or Gartner MQ specific to conversation intelligence found for 2025–2026.
- Sprinklr, Convin, Enthu and Level AI feature details rest mostly on training knowledge.

## Q2. Emotion detection under EU AI Act Art. 5(1)(f): who removed or relabeled it; sentiment vs emotion

### Takeaway
Article 5(1)(f), applicable since 2 Feb 2025, bans AI inferring the emotions of natural persons in the workplace, except for medical or safety reasons. Scoring agents' stress, emotion or tone from voice is therefore prohibited. Inferring customer emotion is not banned, but it is high-risk (Annex III 1(c)) with Art. 50 transparency duties. Text-based sentiment classification, which is not biometric, falls outside the ban. **No source found naming any specific vendor that removed or relabeled emotion detection for the EU.** This was searched for Cogito/Verint, NICE, Uniphore and others. Trade press (UC Today, CX Today) explicitly asks "why is your vendor still selling it?"

### Cited Findings
- Art. 5(1)(f) bans emotion-recognition AI in workplaces and education (medical/safety exception) from 2 Feb 2025. A call-center tool that scores agents' stress from voice is listed as prohibited. — [complylayer](https://complylayer.com/use-cases/ai-emotion-recognition); [Oliver Patel](https://oliverpatel.substack.com/p/emotion-recognition-and-the-eu-ai); [technologyslegaledge (Apr 2025)](https://www.technologyslegaledge.com/2025/04/eu-ai-act-spotlight-on-emotional-recognition-systems-in-the-workplace/)
- The ban covers providers (vendors) and deployers (employers) regardless of where the vendor is headquartered, if the system affects people in the EU (trade press) — [UC Today](https://www.uctoday.com/workplace-management/eu-ai-act-shock-emotion-recognition-is-now-illegal-at-work-so-why-is-your-vendor-still-selling-it/)
- The Commission's Guidelines on prohibited AI practices were published 4 Feb 2025 — [Modulos](https://www.modulos.ai/blog/emotion-recognition-systems-prohibited-under-eu-ai-act/)
- A call centre using voice recognition to track **customers'** emotions (anger, impatience) is not prohibited by Art. 5(1)(f). The Commission guidelines' example is quoted in commentary. — [Oliver Patel](https://oliverpatel.substack.com/p/emotion-recognition-and-the-eu-ai)
- Customer-voice emotion analysis is high-risk (Annex III 1(c)) and requires Art. 50(3) disclosure. A system that reports agent emotional state pulls the whole deployment back into the prohibition, so the advice is to scope analysis to the customer side and require the vendor to show agents aren't scored. — [cavefish](https://cavefish.ai/eu-ai-act-emotion-recognition/); [threll.ai](https://threll.ai/en/blog/emotion-recognition-customer-calls-high-risk)
- Distinction: sentiment analysis classifies negative language (text/keywords), while emotion AI infers states from biometric data such as voice characteristics. Text-only sentiment does not trigger 5(1)(f), though GDPR and labour-law risks remain. — [CX Today](https://www.cxtoday.com/contact-center/contact-center-emotion-ai-eu-rules/); [teamed.global](https://www.teamed.global/insights/is-emotion-recognition-at-work-legal-in-eu)
- Use solely for the agent's personal training may be allowed if results are not shared with HR and cannot affect assessment or promotion (commentary, contested) — [euai-act.com](https://www.euai-act.com/articles/emotion-recognition-ai-compliance)
- Dates conflict for high-risk obligations. One source says Aug 2026; others say 2 Dec 2027, reflecting the Digital Omnibus postponement. — [cavefish](https://cavefish.ai/eu-ai-act-emotion-recognition/); [ziptone.nl](https://www.ziptone.nl/en/emotiedetectie-in-klantcontact-deze-toepassingen-vallen-straks-onder-streng-toezicht/)
- Vendors still market emotion features. Cogito/Verint "measure emotional connections between customers and agents". Uniphore markets "Emotion AI". Genesys offers "agent empathy analysis" in Swedish. — [parse.gl](https://www.parse.gl/brands/verint-com-4); [G2 Uniphore](https://g2.com/products/uniphore-uniphore/reviews); [Genesys release notes](https://help.genesys.cloud/release-notes/genesys-cloud/april-22-2024/)

### Inferences
- The highest-risk features in the EU are agent-side ones: Cogito-style real-time behavioural/emotional cues on the agent's voice, acoustic agent stress scores (CallMiner-type), and possibly "agent empathy" scores if derived from voice prosody rather than words. Text/transcript-based "empathy behaviour" scoring (did the agent say X?) is arguably a behaviour or QA criterion, not emotion inference.
- The industry pattern appears to be quiet repositioning rather than announced removals: "sentiment" (transcript-based, customer-focused) and "behaviours/soft skills" instead of "emotion". This is inferred from vendor wording, not a documented change.
- For Agaton, positioning "buying signals" as transcript/intent-based (not biometric) and customer-side is the defensible line. Any agent "tone/stress" scoring should be avoided in the EU.

### Gaps
- No primary vendor statement found (Verint/Cogito, NICE, CallMiner, Uniphore, Observe.AI, Cresta) about EU-specific disabling or relabelling of emotion features. UC Today and CX Today pages could not be fetched to see which vendors they named.
- Whether Genesys's sv-SE "agent empathy analysis" is text-based or acoustic was not verified.

## Q3. Swedish language quality and Nordic customers

### Takeaway
Confirmed Swedish (sv-SE) analytics support exists among the platforms: Genesys Cloud (transcription, sentiment, empathy since 2024), Amazon Contact Lens (real-time since March 2025), and Puzzel (own European ASR, Danish customer cases). None of the US point solutions (Cresta, Observe.AI, Balto, Level AI, CallMiner) publicly confirm Swedish. Uniphore's listed languages exclude it. No independent Swedish WER/quality benchmarks were found.

### Cited Findings
- Genesys Cloud: sv-SE supported. Sentiment and agent empathy analysis added April 2024 for sv-SE, da-DK, fi-FI and nb-NO. Extended (third-party engine) transcription for Swedish from January 2023. — [Genesys languages](https://help.genesys.cloud/articles/genesys-cloud-supported-languages/); [Genesys April 22, 2024](https://help.genesys.cloud/release-notes/genesys-cloud/april-22-2024/)
- Amazon Contact Lens: sv-SE transcription added September 2024. Moved to real-time analytics in March 2025. — [AWS Sept 2024](https://aws.amazon.com/about-aws/whats-new/2024/09/amazon-connect-contact-lens-transcriptions-10-languages); [AWS March 2025](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-connect-contact-lens-conversational-analytics-new-languages/)
- Puzzel: ASR trained for European languages and accents. Nordic CI customers: Telmore (telecom, 80 agents), DSB, Rejsekort, JFM, Spar Nord (all Denmark). — [Puzzel CI](https://www.puzzel.com/products/better-experiences-faster-growth-with-conversational-intelligence); [Puzzel EU leaders](https://www.puzzel.com/conversational-intelligence-eu-leaders)
- Cresta: real-time translation in ES/FR/PT/DE; AI agents in 30+ languages (unlisted). Balto: 20+ languages (unlisted). Observe.AI and Level AI: no language list found. — [Cresta press](https://cresta.com/press/cresta-breaks-down-language-barriers-with-real-time-translation-and-multilingual-ai); [Balto blog](https://www.balto.ai/blog/baltos-multilingual-conversation-ai-is-now-live-in-20-languages/)
- Uniphore (Capterra): EN, FR, ID, JA, ES, VI — [Capterra](https://www.capterra.co.uk/software/180755/uniphore)
- Cention (Swedish contact-centre vendor) markets speech analytics that score 100% of calls, with translation — [Cention blog](https://blog.cention.com/revolutionizing-quality-assurance-in-contact-centers)

### Inferences
- Swedish quality is a real moat for a local player. The big suites support sv-SE but often through third-party engines, and US point solutions are English-first. A Swedish-native vendor with telecom references (Telenor, Telia) and lender references (Lendo) has a defensible niche, especially for sales-signal detection, which needs nuance beyond generic sentiment.
- The multilingual LLM/ASR wave (Whisper-class models, Cresta's 30+ languages) is eroding this moat over time.

### Gaps
- No Swedish WER or accuracy benchmarks per vendor found.
- No named Swedish customers found for Cresta, Observe.AI, Balto, Level AI, CallMiner or Cogito. Which vendors Telia and Telenor use besides Agaton is unknown.
- Telavox AI analytics capability was not found.

## Q4. Pricing (per agent/month or per minute)

### Takeaway
Point-solution conversation intelligence typically costs about $70–200 per agent/month on annual contracts, often with seat minimums. Cloud baselines are metered: Google charges $0.015–0.05/min plus $50–60 per agent/month for Quality AI, and AWS bills Contact Lens per minute. CCaaS suites run $80–165+ per user/month list, with AI often extra. Almost no point vendor publishes prices. AWS Marketplace listings are the only verifiable figures.

### Cited Findings
- Cresta: no public pricing. AWS Marketplace lists Agent Assist Voice at $150,000/12 months for up to 100k calls ($1.50/call overage) and Chat at $150k for 125k chats ($1.20/chat). Buyer-reported $100–200/agent/month. — [eesel](https://www.eesel.ai/en/blog/cresta-pricing); [CloudTalk Cresta](https://www.cloudtalk.io/blog/cresta-ai-pricing/)
- Observe.AI: AWS Marketplace Real-time AI at $828/agent/year ($69/month). Full stack estimated at $100–150+/agent/month. A 100-seat deployment estimated at $60k–180k/yr. — [CloudTalk](https://www.cloudtalk.io/de/blog/observe-ai-preise/); [JustCall](https://justcall.io/hub/cost/observe-ai-pricing/); [toolradar](https://toolradar.com/tools/observe-ai/pricing)
- CallMiner: about $85–100+/agent/month. Average annual contract about $101,865, up to about $140k. — [Ringly](https://www.ringly.io/blog/callminer-alternatives); [getmacha](https://www.getmacha.com/blog/callminer-complete-guide)
- Balto: 60-agent minimum, average contract about $102K/yr (Vendr data via Balto). "From $100/month" per SelectHub. — [Balto](https://www.balto.ai/compare/balto-vs-callminer/); [SelectHub](https://www.selecthub.com/p/call-center-software/balto-ai)
- Level AI: about $185/agent/month — [Ringly](https://www.ringly.io/nl/blog/level-ai-alternatives)
- Enthu.ai: no public price — [G2](https://g2.com/products/enthu-ai/pricing). Convin: none found.
- General CI benchmark: about $75–200/agent/month — [prospeo](https://prospeo.io/s/observeai-alternatives)
- Talkdesk: $85–165/user/month list, 3-year terms, estimated real TCO $200–300 — [TrustRadius](https://tr-web.dev.trustradius.com/compare-products/dialpad-support-vs-talkdesk); [Ringly](https://www.ringly.io/blog/talkdesk-pricing); [Vendr](https://www.vendr.com/marketplace/talkdesk)
- Dialpad Support: $80/$115/$150 per user/month (annual) — [Ringly](https://www.ringly.io/blog/dialpad-pricing)
- Google: Insights $0.015–0.025/min. Quality AI $50 named or $60 concurrent per agent/month. Agent Assist $0.03–0.05/min. — [Google Insights](https://cloud.google.com/contact-center/insights/pricing); [Google Agent Assist](https://cloud.google.com/agent-assist/pricing)
- Amazon Contact Lens: per-minute, no commitment. Historic $0.015/min. Current rate unclear. — [AWS pricing](https://aws.amazon.com/connect/pricing); [getvoip](https://getvoip.com/blog/amazon-connect-pricing/)

### Inferences
- Example: a 100-agent Swedish centre handling about 1,000 min/agent/month would pay roughly $15–25/agent/month for Google Insights analytics alone, plus $50 for Quality AI and about $30–50 for Agent Assist. That compares with $70–200 for a point solution. Hyperscaler baselines therefore cap price at roughly $100–150/agent/month for comparable bundles, before integration work.
- Seat minimums (Balto 60, Observe.AI enterprise 100) and contracts of about $100k/yr exclude many Nordic mid-size centres (20–80 agents). That is a pricing gap a local vendor can fill.

### Gaps
- No public pricing for NICE Enlighten/Mpower add-ons, Genesys AI tokens, Sprinklr, Uniphore, Convin, Enthu or Verint/Cogito.
- The current AWS Contact Lens per-minute rate was not verified.
- No Nordic SEK pricing found for any vendor.
