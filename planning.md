# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Specialty coffee science and espresso extraction — covering the technical reasoning behind extraction variables, grinder mechanics, water chemistry, coffee processing methods, home roasting, and commercial equipment. This knowledge is valuable because it lives scattered across hobbyist forums, manufacturer brochures, YouTube transcripts, and niche coffee science blogs. Official sources (roaster manuals, coffee shop menus) either skip the science entirely or bury it in jargon, leaving the curious home barista without a single place to find grounded, practical answers.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Clive Coffee — Espresso Channeling guide | Explains what channeling is, how to diagnose it with a bottomless portafilter, and prevention via grind/distribution/tamping | `documents/01_espresso_channeling.txt` |
| 2 | Gevi Engineering Blog — Flat vs Conical Burr Grinders | Senior engineer analysis of burr geometry, particle size distribution (bimodal vs unimodal), and flavor implications | `documents/02_grinder_burrs.txt` |
| 3 | Colombian Coffee Traders — Washed vs Natural Processing | Flavor profile comparison of washed and natural Colombian coffee with brewing recommendations | `documents/03_colombian_processing.txt` |
| 4 | Reddit/r/coffee — UK Water Chemistry Guide | Hobbyist deep-dive into GH/KH hardness, bottled water, filters, RO, and DIY mineral recipes for coffee | `documents/04_water_chemistry_uk.txt` |
| 5 | Caffeine Magazine / Gold Mountain, Falcon, North Star — Processing 101 | Expert-sourced overview of washed, natural, and honey processing methods with flavor and environmental context | `documents/05_processing_101.txt` |
| 6 | Sweet Maria's — Roasting Dark in the Behmor | Step-by-step guide to reaching 2nd crack safely on the Behmor 1600/2000AB Plus home roaster | `documents/06_behmor_dark_roasts.txt` |
| 7 | Sweet Maria's — Roasted Coffee Color Card | Roast degree identification tool: color, temperature, and weight-loss percentage for each roast level | `documents/07_roast_color_card.txt` |
| 8 | La Marzocco — Strada X Feature Brochure | Commercial espresso machine specs, mass-based profiling, Smart Saturation, and paddle-based pressure control | `documents/08_strada_x_specifications.txt` |
| 9 | | | |
| 10 | | | |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 800 characters (~200 tokens)

**Overlap:** 150 characters (~1–2 sentences)

**Reasoning:** Documents range from short product brochures (~350 words) to long procedural guides (~1000 words). None are short one-liner reviews — each key concept (e.g., "how KH affects acidity", "what 2nd crack sounds like") takes 2–5 sentences of connected explanation. An 800-character ceiling keeps each chunk safely under the 256-token hard limit of `all-MiniLM-L6-v2` (~4 chars/token → ~200 tokens, leaving a ~50-token buffer for punctuation-heavy or technical text). The chunker snaps each boundary to the last sentence-ending punctuation (`.`, `?`, `!`) before the 800-char limit so no chunk cuts off mid-sentence; it falls back to a hard cut only when no sentence boundary exists in the window. The 150-character overlap exists specifically for the longer narrative docs (channeling guide, Behmor guide, water chemistry post) where a single idea sometimes spans a natural paragraph break. Actual chunk count across 8 documents: **88 chunks** (range: 5–18 per doc, proportional to document length).

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 4

**Production tradeoff reflection:** `all-MiniLM-L6-v2` is fast and small (22M parameters), which suits a local prototype with a small corpus. For real users, the main tradeoffs to weigh would be: (1) **accuracy on domain-specific text** — a model fine-tuned on scientific or culinary text (e.g., `multi-qa-mpnet-base-dot-v1` or OpenAI's `text-embedding-3-large`) would better distinguish semantically close terms like "GH hardness" vs "KH hardness" or "1st crack" vs "2nd crack"; (2) **context length** — at 256 tokens, MiniLM truncates our longer chunks, so a model with a longer window (e.g., `nomic-embed-text` at 8192 tokens) would embed the full chunk without loss; (3) **latency** — larger API-hosted models add round-trip cost per query, which matters at scale but not for a personal tool.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What causes channeling in espresso and how can I prevent it? | Water finds narrow paths through uneven puck density due to poor distribution or off-level tamping; prevent with even distribution (circular dosing + distribution tool), level tamp, and grind targeting 20–35s shots at 1:1–1:2.5 ratio |
| 2 | What is the difference between flat burr and conical burr grinders in terms of flavor? | Flat burrs produce unimodal (uniform) particle size → clean, bright, layered flavors; conical burrs produce bimodal distribution with more fines → syrupy, rounded, higher body |
| 3 | What does KH do to the taste of espresso, and what KH level is ideal? | KH is the alkalinity buffer; too high mutes acidity and flattens the cup, too low makes it harsh and overly acidic; target a balanced KH that preserves the coffee's natural acidity |
| 4 | What roast level does 2nd crack correspond to, and how does it change flavor? | 2nd crack marks Full City+ (FC+) and beyond; sweetness decreases, acidity disappears, and bittering roast tones and smokiness take over |
| 5 | What are the flavor differences between washed, natural, and honey processed coffees? | Washed = clean, bright acidity, clarity; Natural = intense fruit-forward, berry/stone fruit, wine-like, full body; Honey = between the two — fruity sweetness, rounded acidity, complex mouthfeel depending on mucilage level |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Cross-document concept overlap causing off-target retrieval.** Several documents share vocabulary — "channeling", "extraction", "puck" appear in both the channeling guide (doc 1) and the burr grinder doc (doc 2). A query about grinder flavor might pull channeling-related chunks because the embedding space conflates these overlapping terms. This could produce a partially correct but misleading answer that mixes grinder mechanics with extraction technique.

2. **Technical data split across chunk boundaries.** The water chemistry guide (doc 4) and the roast color card (doc 7) contain dense reference data (ppm values, temperature/weight-loss tables) that span multiple lines. If a chunk boundary falls between, say, the KH definition and its ppm recommendation, retrieval may return the concept without the concrete number — or the number without the explanation — leaving the model unable to give a complete answer.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OFFLINE (build once)                         │
│                                                                     │
│  documents/*.txt                                                    │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────┐     open() / pathlib      ┌──────────────────┐    │
│  │  Ingestion  │ ─────────────────────────▶│  Raw text list   │    │
│  └─────────────┘                           └────────┬─────────┘    │
│                                                     │              │
│       ┌─────────────────────────────────────────────┘              │
│       ▼                                                             │
│  ┌─────────────────────────────────────────┐                       │
│  │  Chunking  (chunk_text.py)              │                       │
│  │  • size = 1000 chars                    │                       │
│  │  • overlap = 150 chars                  │                       │
│  │  • sliding window over raw text         │                       │
│  └────────────────────┬────────────────────┘                       │
│                       │  ~40–55 chunks                             │
│                       ▼                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Embedding + Vector Store  (embed_and_store.py)              │  │
│  │  • sentence-transformers: all-MiniLM-L6-v2                   │  │
│  │  • chromadb (local persistent collection)                    │  │
│  │  • each chunk stored with source filename metadata           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        ONLINE (per query)                           │
│                                                                     │
│  User query (text)                                                  │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Retrieval  (query.py)                                       │  │
│  │  • embed query with same all-MiniLM-L6-v2 model              │  │
│  │  • chromadb cosine similarity search, top-k = 4              │  │
│  │  • filter: discard chunks with distance > threshold          │  │
│  └────────────────────┬─────────────────────────────────────────┘  │
│                       │  top 4 chunks + source filenames           │
│                       ▼                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Generation  (generate.py)                                   │  │
│  │  • groq SDK → llama-3.3-70b-versatile (or similar)           │  │
│  │  • system prompt: answer ONLY from the provided context;     │  │
│  │    if the answer isn't in the documents, say so              │  │
│  │  • user prompt: [chunks formatted as numbered sources]       │  │
│  │                 + user question                              │  │
│  │  • response includes source filenames for attribution        │  │
│  └────────────────────┬─────────────────────────────────────────┘  │
│                       │                                             │
│                       ▼                                             │
│             Answer + sources displayed                              │
│             (CLI print or Gradio/Streamlit UI)                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
- Tool: Claude Code
- Input: The Chunking Strategy section of this file + the Architecture diagram (ingestion and chunking stages)
- Expected output: Two functions — `load_documents(folder_path) -> list[dict]` that reads all `.txt` files from `documents/` and returns `{text, source}` dicts, and `chunk_text(text, chunk_size=1000, overlap=150) -> list[str]` that implements a sliding-window character split
- Verification: Print chunk count and first 3 chunks from one document; confirm no chunk is shorter than 200 chars or longer than 1100 chars; confirm overlap text appears at both the end of chunk N and start of chunk N+1

**Milestone 4 — Embedding and retrieval:**
- Tool: Claude Code
- Input: The Retrieval Approach section + Architecture diagram (embedding and retrieval stages) + the chunk_text() output format
- Expected output: `embed_and_store.py` that loads chunks, embeds with `all-MiniLM-L6-v2`, and persists a ChromaDB collection with source metadata; and `retrieve(query, top_k=4) -> list[dict]` that returns ranked chunks with their source filenames
- Verification: Run a test query ("what is channeling?") and confirm at least 2 of the top 4 results come from `01_espresso_channeling.txt`

**Milestone 5 — Generation and interface:**
- Tool: Claude Code
- Input: The Generation stage of the Architecture diagram + the grounding constraint (answer only from context) + the retrieve() output format
- Expected output: `generate.py` with a `answer_question(query)` function that calls retrieve(), formats chunks as numbered sources in the prompt, calls Groq API, and returns the response with source attribution; plus a minimal CLI loop (or Gradio UI)
- Verification: Run all 5 evaluation plan questions; confirm answers cite sources and that the model says "I don't know" for a question clearly outside the corpus (e.g., "What is the best espresso machine under $500?")
