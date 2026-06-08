# The Unofficial Guide — Project 1

---

## Domain

Specialty coffee science and espresso extraction — covering the technical reasoning behind extraction variables, grinder mechanics, water chemistry, coffee processing methods, home roasting, and commercial espresso equipment. This knowledge is valuable because it sits at the intersection of food science and craft, but it's scattered across manufacturer brochures, hobbyist forums, YouTube transcripts, and niche coffee science blogs with no single authoritative source. Official channels (roaster manuals, coffee shop menus) either skip the science entirely or use jargon without explanation, leaving the curious home barista without a place to find grounded, practical answers to questions like "why does my water make my espresso taste flat?" or "what is the actual difference between flat and conical burrs?"

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Clive Coffee — Espresso Channeling guide | Article | `documents/01_espresso_channeling.txt` |
| 2 | Gevi Engineering Blog — Flat vs Conical Burr Grinders | Technical article | `documents/02_grinder_burrs.txt` |
| 3 | Colombian Coffee Traders — Washed vs Natural Processing | Blog post | `documents/03_colombian_processing.txt` |
| 4 | Reddit/r/coffee — UK Water Chemistry for Coffee | Forum guide | `documents/04_water_chemistry_uk.txt` |
| 5 | Caffeine Magazine — Coffee Processing 101 | Expert-sourced guide | `documents/05_processing_101.txt` |
| 6 | Sweet Maria's — Roasting Dark in the Behmor | How-to guide | `documents/06_behmor_dark_roasts.txt` |
| 7 | Sweet Maria's — Roasted Coffee Color Card | Reference guide | `documents/07_roast_color_card.txt` |
| 8 | La Marzocco — Strada X Feature Brochure | Product specification | `documents/08_strada_x_specifications.txt` |
| 9 | | | |
| 10 | | | |

---

## Chunking Strategy

**Chunk size:** 800 characters maximum per chunk (~200 tokens at 4 chars/token)

**Overlap:** 150 characters between consecutive chunks

**Why these choices fit my documents:** Documents range from short product brochures (~350 words) to long procedural guides (~1,000 words). None are short one-liner reviews — each key concept takes 2–5 connected sentences to explain. An 800-character ceiling keeps every chunk safely under the 256-token hard limit of `all-MiniLM-L6-v2`, leaving a ~50-token buffer for punctuation-heavy or technical text. The chunker snaps each boundary to the last sentence-ending punctuation (`. ? !`) before the 800-char limit so no chunk cuts off mid-sentence; it falls back to a hard cut only when no sentence boundary exists in the window. The 150-character overlap exists specifically for the longer narrative documents — the channeling guide, the Behmor guide, and the water chemistry post — where a single idea sometimes spans a natural paragraph break. I also prepend each chunk with the document title in brackets (e.g., `[Water for Coffee Guide - KH Buffer and Magnesium Hardness Dynamics]`) before embedding, so that mid-document chunks carry topic context even when the title line is in a different chunk. One bug caught during testing: the initial chunking loop produced 655 chunks instead of 88 because the overlap calculation pulled `start` back inside the document after reaching the end, causing ~150 extra 1-char-advance iterations per document. Fixed by breaking immediately when `end >= len(text)`.

**Final chunk count:** 88 chunks across 8 documents (range: 5–18 per document, proportional to document length)

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, running locally

**Production tradeoff reflection:** `all-MiniLM-L6-v2` is fast and small (22M parameters), which is appropriate for a local prototype with a small corpus — no API key, no rate limits, and it embeds 88 chunks in under 2 seconds. For real users, the main tradeoffs to weigh would be: (1) **accuracy on domain-specific text** — the model struggled to distinguish "KH alkalinity" from "espresso taste" across documents because it's a general-purpose model with no coffee-science fine-tuning; a retrieval-optimized model like `multi-qa-mpnet-base-dot-v1` or OpenAI's `text-embedding-3-large` would better separate domain-specific chemistry terms; (2) **context length** — at 256 tokens, MiniLM silently truncates longer chunks, which is why the chunk size ceiling was set to 800 characters rather than the 1,000 originally planned; a model with a longer window (e.g., `nomic-embed-text` at 8,192 tokens) would embed full chunks without loss; (3) **latency** — larger API-hosted embedding models add round-trip cost per query, acceptable for a personal tool but significant at scale.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a specialty coffee reference assistant.
Answer using ONLY the exact content of the source documents provided below.
Rules you must follow:
1. Do not use any knowledge from outside the provided documents.
2. Do not infer, extrapolate, or speculate. No phrases like "likely", "probably",
   "it can be inferred", or "suggests".
3. If the documents do not contain enough information to answer, respond with
   exactly: "My documents don't cover that."
4. Do not include source filenames in your answer — they are shown to the user separately.
```

The strictness of rule 2 was added after testing revealed the model inserting a sentence beginning with "It can be inferred that..." when comparing a color card to drum speed adjustments — producing a logically plausible but unsourced answer. With rule 2 in place, the model correctly returns the refusal string for questions outside the corpus.

**How source attribution is surfaced in the response:** Source attribution is programmatic, not LLM-generated. After retrieval, chunks are grouped by source filename (`by_source` dict in `generate.py`). The list of source filenames is returned directly from retrieval metadata as a separate `"sources"` field in the response dict and displayed in a dedicated "Retrieved from" panel in the Gradio UI. The LLM is explicitly told not to mention filenames in its answer, preventing inconsistent or hallucinated citations. If multiple chunks from the same document are retrieved, they are merged into a single context block before being sent to the LLM, so each document appears exactly once as a source.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What causes channeling in espresso and how can I prevent it? | Uneven puck density from poor distribution or off-level tamping; prevent with even distribution, level tamp, 20–35s shots at 1:1–1:2.5 ratio | Correctly identified uneven distribution, improper tamping, and grinding too fine as causes; gave specific prevention steps including grind ratio and depth-calibrated tampers | Relevant | Accurate |
| 2 | What is the difference between flat burr and conical burr grinders in terms of flavor? | Flat = unimodal particles → clean, bright, layered; conical = bimodal with more fines → syrupy, rounded, higher body | Correctly contrasted bimodal (conical, syrupy/rounded) vs unimodal (flat, clean/bright/layered) distributions with specific flavor descriptors | Relevant | Accurate |
| 3 | What does KH do to the taste of espresso, and what KH level is ideal? | KH is the alkalinity buffer; too high mutes acidity and flattens the cup, too low makes it harsh; target balanced KH | Correctly explained KH as the alkalinity buffer with both failure directions; accurately stated the documents don't specify a target ppm, which is correct — the source gives qualitative guidance only | Relevant | Partially accurate |
| 4 | What roast level does 2nd crack correspond to, and how does it change flavor? | 2nd crack = Full City+ and beyond; sweetness decreases, acidity disappears, bittering roast tones take over | Correctly identified Full City+ and described sweetness giving way to bittering tones and loss of acidity | Relevant | Accurate |
| 5 | What are the flavor differences between washed, natural, and honey processed coffees? | Washed = clean/bright acidity; Natural = intense fruit-forward, berry/stone fruit, wine-like; Honey = between the two with rounded sweetness and complex mouthfeel | Correctly described all three profiles; washed description was slightly vague ("taste what's on the inside") but natural and honey descriptions were specific and accurate | Partially relevant | Partially accurate |

---

## Failure Case Analysis

**Question that failed:** "How do physical visual cues like a color card contrast with operational machine adjustments (like drum speed or smoke suppression) when executing a dark roast?"

**What the system returned:** "My documents don't cover that."

**Root cause (tied to a specific pipeline stage):** The failure is in the **retrieval stage**. The drum speed instruction ("Use the fast drum speed by hitting `<D>` to keep the coffee high in the drum") exists in `06_behmor_dark_roasts.txt`, but the chunk containing it never appeared in the top 5 results. The query asks for a cross-document comparison across two specific sub-topics simultaneously — color card visual assessment and drum speed / smoke suppression as operational controls. The single embedding vector for the full query averages across both aspects, pulling the color card document correctly but surfacing adjacent Behmor chunks (fire safety, preheating steps) rather than the specific drum speed chunk. With top_k=5 and 18 Behmor chunks in the corpus, the probability of the right chunk ranking in the top 5 for a broad comparison query is low. The system then correctly refused to answer because the retrieved context didn't contain the requested information — this is the grounding working as intended, but the retrieval gap means the question goes unanswered even though the answer exists in the corpus.

**What you would change to fix it:** Run two separate retrieval passes — one per sub-topic extracted from the query — and merge the top-k results before generation. For this query that would mean one pass for "color card roast identification" and one for "Behmor drum speed dark roast," guaranteeing coverage of both documents. A simpler band-aid would be increasing top_k to 8–10, accepting some context dilution to improve coverage of multi-topic queries.

---

## Spec Reflection

**One way the spec helped you during implementation:** The architecture diagram in `planning.md` was the most useful artifact during implementation. Because each pipeline stage was labeled with the specific library and function name — `chunk_text.py` with character size and overlap, `embed_and_store.py` with `all-MiniLM-L6-v2` and ChromaDB, a named `retrieve()` function returning top-k chunks — I could feed exactly one section of the diagram to Claude at a time and get code that matched the rest of the system. Without that specificity, AI-generated code across multiple sessions tends to drift in variable names, return formats, and assumptions about what the previous stage produces. The spec acted as a shared contract between stages.

**One way your implementation diverged from the spec, and why:** The original spec set chunk size at 1,000 characters, which I had to reduce to 800 during implementation. The reason was a token math problem I hadn't worked through at planning time: `all-MiniLM-L6-v2` has a 256-token hard limit, and English text averages ~4 characters per token, so 1,000 characters translates to ~250 tokens — right at the boundary, with no buffer for punctuation-dense or technical text. When I caught this before embedding, I lowered the ceiling to 800 characters (~200 tokens) to leave a safe margin. I also added contextual chunk headers (document title prepended to each chunk) after discovering that mid-document chunks from the water chemistry guide were losing in retrieval to the channeling guide because the query phrase "espresso taste" matched the channeling document more strongly than the chemistry terms that only appeared in the title of doc 04.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy section from `planning.md` (chunk size 800 chars, 150-char overlap, sentence-boundary snapping requirement) and asked it to implement `chunk_text()` and `load_documents()`.
- *What it produced:* A sliding window character split with a regex that found the last sentence-ending punctuation before the chunk limit. Structurally correct, but with a bug: the loop used `while start < length` with `next_start = end - overlap`, which — at the end of each document — set `next_start` to `length - 150`, pulling `start` back inside the document and causing ~150 extra 1-char iterations. Result was 655 chunks instead of the expected 88.
- *What I changed or overrode:* I ran the diagnostic output, identified the spin loop by tracing start/end positions, and directed the fix: `if end >= length: break` immediately after appending the final chunk. This collapsed 655 chunks back to 88 and verified the per-document counts against expected ranges.

**Instance 2**

- *What I gave the AI:* The retrieval test results showing Query 3 (KH water chemistry) failing — the correct document ranked second (distance 0.4849) behind a channeling chunk (0.4731) — along with a description of why: "taste of espresso" in the query matched the channeling document because it uses "espresso" heavily, while the water chemistry document uses "coffee." I asked it to implement a fix.
- *What it produced:* An `extract_title()` function that reads the `Title:` line from the first line of each document and a modification to `build_chunk_corpus()` that prepends `[Document Title]` as a header to every chunk before embedding, so that mid-document chunks carry topic context.
- *What I changed or overrode:* I verified the fix by re-running retrieval on Query 3 and confirmed the correct document moved to rank 1 (distance 0.4079) with a 0.09 gap over the channeling document. I kept the LLM-generated code but added the requirement that the title be prepended to the embedded text only — the original produced version prepended it to both the stored text and the displayed text, which I accepted since the title provides useful context in the Gradio UI as well.
