# Agaton (agaton.ai): reconstruction of product, technology and business from public sources

Research date: 2026-10-17. Method: WebSearch only. WebFetch failed on every domain tried (agaton.ai, eu-startups.com, beinsure.com, dealroom.co: DNS ENOTFOUND in this environment), so the findings below rest on search-engine snippets of the cited pages, not on full-page reads. The quotes from agaton.ai pages come from search snippets of those pages. Company-reported metrics are marked as such. No login or non-public access was used.

## 1. What the product does (features, modules, real-time vs post-call)

### Takeaway
Agaton sells a "deep voice AI" platform for sales and customer-service calls. It scores how something is said (prosody, pace, energy, pauses) as well as what is said. From that it flags buying signals, churn risk, objections and competitor mentions, and it drives coaching and automated QA. The marketing names one module, "Revenue Mining", and also pitches "AI agents for sales teams". The product began as post-call analysis of recorded calls and now also claims live, in-call detection.

### Cited Findings
- Homepage: "Agaton is a deep voice AI platform. Revenue Mining finds the sales opportunities hidden in every call" (also churn risk and agent coaching). — [agaton.ai](https://www.agaton.ai/)
- Second positioning on the site: "We build secure, domain-specific AI Agents for sales teams that automate core workflows." — [agaton.ai](https://www.agaton.ai/)
- The homepage says it scores "thousands of vocal signals in every call", including pace, energy, confidence and "the half-second pause before a yes". It isolates the signals that predict a sale and explains why each one was flagged and what to say instead. — [agaton.ai](https://www.agaton.ai/)
- Coaching "before, during, and after calls", with objection indicators among the coaching areas. — [agaton.ai](https://www.agaton.ai/)
- About page: the AI "brain" spots engagement levels, buying signals, objections and competitive mentions during live calls, "like a manager listening in". — [agaton.ai/about-us](https://www.agaton.ai/about-us)
- Product page: it analyses customer calls with voice AI, integrates with existing sales tools, and acts automatically with personalised coaching. — [agaton.ai/product](https://www.agaton.ai/product)
- QA page: it listens to every conversation and scores each against the customer's own standards (scripts, disclosures, tone of voice). It spots "a missed disclosure, an off-script promise, or a pushy turn while the call is still happening". — [agaton.ai/quality-assurance](https://www.agaton.ai/quality-assurance)
- It detects churn signals from how customers speak, not only what they say. — [agaton.ai](https://www.agaton.ai/) (via search snippet)
- Press: unlike transcription tools, it detects sentiment changes, highlights sales opportunities, provides coaching insights and supports QA. — [Tech.eu](https://tech.eu/2026/02/19/agaton-raises-9-million-to-expand-its-ai-platform-for-sales-teams/); [TFN](https://techfundingnews.com/stealth-ai-startup-agaton-raises-9m-to-turn-calls-into-revenue-intel/)
- It identifies tone inflections and emotional shifts and sends the insights into coaching workflows and QA systems. — [EU-Startups](https://www.eu-startups.com/2026/02/stockholm-based-agaton-secures-e8-4-million-to-turn-customer-conversations-into-revenue-insights/)
- Breakit (Feb 2026) describes an AI agent that listens to customer calls companies have *recorded with the customer's consent*, to detect buying signals. — [Breakit](https://www.breakit.se/artikel/45501/agaton-bygger-ai-som-lyssnar-in-pa-kunderna-tar-in-90-miljoner-fran-inception-fund-och-sebastian-knutsson)
- There is a subdomain voice.agaton.ai, a voice agent demo page behind a demo key. — [voice.agaton.ai](https://voice.agaton.ai/) (via site: search)
- A proprietary tool, "Agaton Privacy Guard", automatically redacts PII from calls. — [agaton.ai](https://www.agaton.ai/) (via site: search)

### Inferences
- The product probably moved from post-call batch analysis of recorded calls (as Breakit framed it in Feb 2026) towards real-time assist. The live QA claim and the NVIDIA low-latency story (section 2) point that way. Real-time is likely newer and less mature than post-call.
- The product has three layers: (1) signal extraction (ASR plus acoustic/prosodic features), (2) prediction models that link signals to outcomes (sale, churn), and (3) an LLM-based layer that produces explanations, "what to say instead", coaching and QA scoring against customer rubrics.
- The voice.agaton.ai demo suggests they are experimenting with outbound or inbound voice agents, not only analytics. This is unconfirmed.
- I found no evidence of an explicit "next best action" feature name. The "what to say instead" coaching works as one in practice.

### Gaps
- No public documentation of the module list, dashboards, the API or the exact real-time delivery mechanism (agent desktop widget, CCaaS plugin, etc.).
- The full agaton.ai pages could not be fetched, so the details rest on snippets.

## 2. Technology (paralinguistics, Nordic languages, ASR, LLM, hosting, security)

### Takeaway
The core differentiator Agaton claims is acoustic/paralinguistic modelling on top of transcription. NVIDIA publicly lists it as using Nemotron (3.5 "Lightning") for low-latency real-time analysis. It claims EU-only infrastructure, a dedicated VPC per customer, ISO 27001 and ISO 42001, with SOC 2 in progress, though its own pages are inconsistent on the certification status.

### Cited Findings
- It scores "thousands of vocal signals" (pace, energy, confidence, pauses). — [agaton.ai](https://www.agaton.ai/)
- Its investor claims it detects buying and churn signals better than rivals (an investor quote in the funding coverage). — [EU-Startups](https://www.eu-startups.com/2026/02/stockholm-based-agaton-secures-e8-4-million-to-turn-customer-conversations-into-revenue-insights/)
- NVIDIA Nordic coverage (Oct 2026): Agaton uses NVIDIA Nemotron 3.5 Lightning in software that analyses customer conversations in real time. The coverage says it reduces response latency in live sales calls. — [ChannelLife](https://channellife.co.uk/story/nvidia-deepens-nordic-ai-bets-with-startups-partners); [CFOtech](https://cfotech.co.uk/story/nvidia-deepens-nordic-ai-bets-with-startups-partners); [NVIDIA blog](https://blogs.nvidia.com/blog/nordics-technology-ecosystem/)
- The same NVIDIA coverage mentions Klang's "Pianissimo", a Swedish transcription model claimed to reduce errors by 75%. This is a separate company, but it shows the Swedish ASR options available. — [ChannelLife](https://channellife.co.uk/story/nvidia-deepens-nordic-ai-bets-with-startups-partners)
- Security page: ISO 27001 and ISO 42001 certified, working towards SOC 2. AES-256 at rest, TLS 1.2+ in transit. "All infrastructure and operations located within EU borders". Customer data in "dedicated, isolated environments within Agaton's Virtual Private Cloud". Fully GDPR compliant, with DPAs and on-demand deletion. — [agaton.ai/security](https://www.agaton.ai/security)
- Homepage badge: "GDPR compliant. ISO 27001 Certified… SOC2 coming soon". Another section reads "SOC ll and ISO 27001: Coming soon". — [agaton.ai](https://www.agaton.ai/)
- "Customer data is not used to train or update services without explicit consent." — [agaton.ai](https://www.agaton.ai/) (via site: search)
- They say they don't collect, store or sell customer data. — [ContentGrip](https://www.contentgrip.com/agaton-seed-funding-ai-sales/) (summary)
- A Trust Center exists at trust.agaton.ai (likely a Vanta/Drata-style portal). Its contents could not be retrieved. — [trust.agaton.ai](https://trust.agaton.ai/)

### Inferences
- The Nemotron link suggests they self-host open-weight NVIDIA models, probably on EU GPU cloud, instead of sending audio or text to US API providers. That fits the "EU-only, dedicated VPC" claim. Which cloud or region is used is unknown.
- The likely stack: Swedish/Nordic-capable ASR (Whisper-family or similar, fine-tuned), diarisation, PII redaction (Privacy Guard), a prosodic feature extractor plus a classifier trained on customer outcome data (conversion/churn labels from CRM), and LLM summarisation/coaching/QA scoring. The "explains why" claim suggests the LLM verbalises the classifier's features.
- Their advantage most likely comes from outcome-labelled Nordic call data (4M calls, telecom sales) rather than a new model architecture.
- ISO 42001 (AI management system) is unusual for a seed company. It is aimed at enterprise and telecom procurement.

### Gaps
- No public certificate register entry, auditor name, scope statement or sub-processor list found. The certification status is self-reported and internally inconsistent.
- No information on the ASR vendor, on whether they train their own models, or on language coverage beyond the Nordic customer base.
- No engineering blog or GitHub presence found.

## 3. Integrations (telephony/CCaaS, CRM, BPO)

### Takeaway
Agaton says only that it "integrates with existing sales tools". No named telephony/CCaaS or CRM integrations (Genesys, Puzzel, Telavox, Teams, Salesforce) could be confirmed. Foundever, the BPO, is named as a partner and customer, but no standalone partnership announcement was found.

### Cited Findings
- Integrates with existing sales tools (no list given). — [agaton.ai/product](https://www.agaton.ai/product)
- Builds "domain-specific AI agents that integrate with existing enterprise systems". — [Startupintros / funding coverage](https://startupintros.com/orgs/agaton)
- Foundever appears in the seed-round coverage as a partner, described as the world's third-largest BPO with 150,000 agents. — [The Rise Post](https://www.therisepost.com/news/articles/stockholms-agaton-steps-out-of-stealth-with-dollar10m-to-turn-every-customer-call-into-a-revenue-signal-69979726b4b8c179357cbb20); [ContentGrip](https://www.contentgrip.com/agaton-seed-funding-ai-sales/)
- The website claims "-28% lower Churn Rates for Global BPO leader" (client unnamed, most likely Foundever). — [agaton.ai](https://www.agaton.ai/) (via snippet)
- A search for an Agaton–Foundever press release returned only other Foundever AI partnerships (Cognigy, M47 Labs). — [Foundever news](https://foundever.com/news/foundever-and-cognigy-strengthen-strategic-partnership-to-deliver-scalable-agentic-ai-solutions-across-the-globe/)

### Inferences
- Because the product starts from recorded calls, the simplest integration is pulling call recordings plus metadata from the CCaaS/PBX (Genesys Cloud, Puzzel, Telia/Telenor platforms, Teams) and pushing results to CRM. Real-time requires a media stream fork (e.g. Genesys AudioHook or SIPREC), but that is not documented.
- The Foundever relationship is probably a customer/pilot within Nordic delivery centres rather than a global reseller deal. It is not confirmed.

### Gaps
- No integration directory, marketplace listing (Genesys AppFoundry, Salesforce AppExchange) or API documentation found.

## 4. Customers, case results and claimed metrics

### Takeaway
Named customers: Telenor, Telia, Lendo, Axo Finans, and Foundever as a BPO partner. All metrics come from the company: 4M calls analysed, "doubled conversion" (for top performers), up to 80% less QA handling time, +64% sales conversion at a "Nordic telecom leader", -28% churn at a "global BPO leader", and 7x year-on-year revenue growth.

### Cited Findings
- Customers include Telenor, Telia, Lendo and Axo Finans. — [TFN](https://techfundingnews.com/stealth-ai-startup-agaton-raises-9m-to-turn-calls-into-revenue-intel/); [Tech.eu](https://tech.eu/2026/02/19/agaton-raises-9-million-to-expand-its-ai-platform-for-sales-teams/)
- 4 million customer calls analysed, clients report doubled conversion rates, 80% reduction in QA handling time. — [TFN](https://techfundingnews.com/stealth-ai-startup-agaton-raises-9m-to-turn-calls-into-revenue-intel/); [EU-Startups](https://www.eu-startups.com/2026/02/stockholm-based-agaton-secures-e8-4-million-to-turn-customer-conversations-into-revenue-insights/)
- "Additional days' worth of revenue each month through automated revenue mining". — [The Rise Post](https://www.therisepost.com/news/articles/stockholms-agaton-steps-out-of-stealth-with-dollar10m-to-turn-every-customer-call-into-a-revenue-signal-69979726b4b8c179357cbb20)
- 7x year-on-year revenue growth since launch (company claim). — [ContentGrip](https://www.contentgrip.com/agaton-seed-funding-ai-sales/)
- Website: "64% increase in Sales Conversion rate for Nordic telecom leader", "-28% lower Churn Rates for Global BPO leader". — [agaton.ai](https://www.agaton.ai/)
- Telenor testimonial from Soheil Adjoudani, Head of Customer Service Inhouse: the AI agents help reps improve continuously and boost sales efficiency. The blog has a Telenor case study. — [The Rise Post](https://www.therisepost.com/news/articles/stockholms-agaton-steps-out-of-stealth-with-dollar10m-to-turn-every-customer-call-into-a-revenue-signal-69979726b4b8c179357cbb20); [agaton.ai/blog](https://www.agaton.ai/blog)

### Inferences
- The beachhead is inbound customer service with upsell (telecom) and outbound/inbound loan sales (Lendo, Axo Finans are loan brokers), i.e. high-volume, conversion-measurable phone sales in Sweden and Norway.
- "Doubled conversion" appears to refer to top performers or specific cohorts, not account-wide averages.

### Gaps
- No independent or customer-published case studies with method or baseline. No customer count or ARR figure.

## 5. Team, founders, funding, hiring

### Takeaway
Agaton was founded in late 2024 in Stockholm by Andreas Kullberg (CEO) and John Kristensen (COO/co-founder), with Yi Fu as CTO. It came out of stealth in February 2026 with a ~$10M seed (≈90 MSEK, reported as €8.4M), co-led by Inception Fund and Alstin Capital. DI Digital reported a post-money valuation of about 400 MSEK. It has a US subsidiary, and the CEO has moved to New York.

### Cited Findings
- Founders: Andreas Kullberg (CEO), John Kristensen (COO), Yi Fu (CTO). Prior roles across the team: EF Education First, Aviva, H&M, Volvo Cars, Tele2, Tink, King, Gillion. — [EU-Startups](https://www.eu-startups.com/2026/02/stockholm-based-agaton-secures-e8-4-million-to-turn-customer-conversations-into-revenue-insights/); [The Rise Post](https://www.therisepost.com/news/articles/stockholms-agaton-steps-out-of-stealth-with-dollar10m-to-turn-every-customer-call-into-a-revenue-signal-69979726b4b8c179357cbb20)
- About page: the team previously built and led at Spotify, Tink, Astrid, Sana and EF. — [agaton.ai/about-us](https://www.agaton.ai/about-us)
- Yi Fu: previously at Hypertype, Closar AI, H&M Group and Tink. KTH master's degree (2008–2011). Some sources list him as Head of Engineering. — [LinkedIn (Yi Fu)](https://www.linkedin.com/in/yvesfu/); [RocketReach](https://rocketreach.co/yi-fu-email_4402220)
- John Kristensen's X bio: "Founder @ Agaton - Building AI agents for sales teams". — [X](https://x.com/Kristensen_John)
- A 2017 Breakit article names an Andreas Kullberg (ex-Pamoja Education) as the new CEO of Cool Company. It is unconfirmed whether this is the same person. — [Breakit 2017](https://www.breakit.se/artikel/7587/cool-company-grundaren-lamnar-over-andreas-kullberg-tar-over-som-ny-vd)
- Started late 2024. Seed of ≈90 MSEK, co-led by Inception Fund and Alstin Capital. Sebastian Knutsson (King co-founder) is an angel. DI Digital puts the valuation at ≈400 MSEK including the new money. Part of the money goes to US establishment, where a subsidiary already exists. — [Breakit](https://www.breakit.se/artikel/45501/agaton-bygger-ai-som-lyssnar-in-pa-kunderna-tar-in-90-miljoner-fran-inception-fund-och-sebastian-knutsson)
- Other participants: seed+speed Ventures, Foundry Ventures, and angels including Peter Sarlin (Silo AI founder) and Kieran Flanagan. — [EU-Startups](https://www.eu-startups.com/2026/02/stockholm-based-agaton-secures-e8-4-million-to-turn-customer-conversations-into-revenue-insights/); [seed+speed portfolio](https://www.seedandspeed.com/portfolio/agaton)
- The amount is reported as $9M, $9.9M, $10M or €8.4M. One outlet says $9M new money for $10M total seed. Founding year is given as 2024 or 2025 depending on the source. — [TFN](https://techfundingnews.com/stealth-ai-startup-agaton-raises-9m-to-turn-calls-into-revenue-intel/); [Startupintros](https://startupintros.com/orgs/agaton)
- Use of funds: go-to-market, product/AI development, international expansion. Plans to more than double the team within a year. — [Beinsure](https://beinsure.com/news/stockholm-startup-agaton-raises-10mn-seed/); [Bebeez](https://bebeez.eu/2026/03/05/swedish-agaton-raises-10-million-seed-to-turn-customer-conversations-into-revenue-intelligence/)
- Inception Fund is a €21M micro fund backing new Nordic AI founders. — [ArcticStartup](https://arcticstartup.com/inception-fund-launches-with-a-e21-million-micro-fund/)
- Job ads (aggregator, possibly stale): "AI / Voice ML Engineer" and "Enterprise Account Executive", Stockholm, in-office. — [The Anti Job Board](https://www.theantijobboard.com/startups/companies/agaton)
- Livia Moore has a LinkedIn profile listing Agaton (role unknown). — [LinkedIn](https://www.linkedin.com/in/liviamoore/)

### Inferences
- The team leans towards enterprise sales/transformation and fintech (Tink) engineering rather than speech research. The "Voice ML Engineer" opening suggests they are building in-house acoustic modelling expertise.
- The US push (CEO in New York) puts them up against well-funded US incumbents.

### Gaps
- No Teamtailor/LinkedIn job texts with stack details (languages, cloud, ML frameworks) could be retrieved. No headcount figure. No podcasts or long interviews found.

## 6. Pricing and target segments

### Takeaway
Pricing is not published ("contact sales@agaton.ai"). The targets are enterprise contact centres with phone sales: telecom, consumer finance/loan brokers, utilities, and BPOs.

### Cited Findings
- "Please reach out to sales@agaton.ai for more information on pricing." — [agaton.ai](https://www.agaton.ai/)
- Customers span telecom, financial services and utilities. — [ContentGrip](https://www.contentgrip.com/agaton-seed-funding-ai-sales/)
- Book-a-demo funnel. — [agaton.ai/book-a-demo](https://www.agaton.ai/book-a-demo)

### Inferences
- Enterprise sales motion with annual contracts, probably priced per agent seat or per analysed minute or call, possibly with outcome-linked framing ("revenue mining"). This is unverified.

### Gaps
- No price points, tiers or minimum contract sizes found.

## 7. Positioning, competitors and weaknesses (incl. EU AI Act Art. 5(1)(f))

### Takeaway
Agaton positions itself as "revenue intelligence from how customers speak" for Nordic enterprise contact centres, competing with Cresta, Balto, Observe.AI, CallMiner, Gong/Clari Wingman, and Nordic transcription/QA players. Its main risks are unverified vendor metrics, inconsistent compliance claims, and regulatory exposure under the EU AI Act's workplace emotion-recognition ban if its voice analysis of agents counts as inferring emotions from biometric data.

### Cited Findings
- Competing products: Cresta surfaces next best action for coaches; Wingman (Clari) flags competitor mentions and pricing stalls. — [Guideflow](https://www.guideflow.com/blog/call-coaching-software); [Cirrus Insight](https://www.cirrusinsight.com/blog/ai-sales-calls)
- AI Act Art. 5(1)(f) bans AI systems that infer emotions in workplaces and education institutions, except for medical or safety reasons. It applies only to systems using biometric data. The Commission Guidelines (C(2025) 884, 4 Feb 2025) read "workplace" broadly. — [FPF](https://fpf.org/blog/red-lines-under-eu-ai-act-unpacking-the-prohibition-of-emotion-recognition-in-the-workplace-and-education-institutions/); [Freshfields](https://technologyquotient.freshfields.com/post/102kfql/eu-ai-act-unpacked-25-european-commission-releases-critical-ai-act-implementati)
- A Lewis Silkin example: a call centre using voice recognition to track employee anger falls under the ban. — [Lewis Silkin](https://www.lewissilkin.com/en/insights/2025/02/17/understanding-the-eu-ai-acts-prohibited-practices-key-workplace-and-advertising-102k011)
- Commentary notes the Guidelines appear to permit emotion recognition for training purposes if results are not shared with HR and do not affect assessment or promotion. This carve-out is not in the Act's text. — [Wolters Kluwer blog](https://legalblogs.wolterskluwer.com/global-workplace-law-and-policy/the-prohibition-of-ai-emotion-recognition-technologies-in-the-workplace-under-the-ai-act/)
- Agaton's marketing explicitly scores "confidence", "energy" and "emotional shifts/tone inflections". — [agaton.ai](https://www.agaton.ai/); [EU-Startups](https://www.eu-startups.com/2026/02/stockholm-based-agaton-secures-e8-4-million-to-turn-customer-conversations-into-revenue-insights/)

### Inferences
- **AI Act risk:** Analysing *customers'* voices to infer buying intent or sentiment is not a workplace ban case, though it may count as emotion recognition and carry transparency duties (Art. 50) and possible high-risk treatment. Scoring *agents'* vocal confidence, energy or tone for coaching or QA is the exposed part. Voice prosody used to infer emotional states is plausibly "biometric data" under the Commission's reading. Coaching used only for training, kept away from HR evaluation, may fit the Guidelines' informal carve-out, but auto-QA scores that feed performance management are hard to defend. Agaton's likely defences: (a) it infers "signals" or "intent", not emotions; (b) agent-side analysis is limited to observable behaviour (talk ratio, pace, script adherence), which the Guidelines treat differently from emotion inference; (c) customer-side only. How they handle this is not documented publicly.
- **Other weaknesses:** every metric comes from the company; there are inconsistent ISO/SOC 2 statements on their own site; small team spread across Stockholm and New York; dependence on a few large Nordic telecom accounts; no visible integration ecosystem; narrow Nordic-language moat versus global players adding Nordic ASR; recorded-call consent rules (Breakit's "with the customer's consent" framing).

### Gaps
- No public Agaton statement on the AI Act, emotion recognition or works-council (MBL) handling. No independent reviews (G2 etc.) found.
