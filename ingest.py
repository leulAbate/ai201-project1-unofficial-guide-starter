"""
Milestone 3 — Document ingestion and chunking.

Loads all .txt files from documents/, cleans them, and splits into
overlapping chunks that respect sentence boundaries and stay within
the 256-token limit of all-MiniLM-L6-v2 (~800 chars max).
"""

import re
import random
from pathlib import Path

DOCUMENTS_DIR = Path("documents")
CHUNK_SIZE = 800   # characters; ~200 tokens at 4 chars/token
OVERLAP = 150      # characters of overlap between consecutive chunks
MIN_CHUNK = 80     # discard fragments shorter than this


def load_documents(folder: Path = DOCUMENTS_DIR) -> list[dict]:
    """Read every .txt file in folder; return list of {text, source} dicts."""
    docs = []
    for path in sorted(folder.glob("*.txt")):
        if path.name == ".gitkeep":
            continue
        text = path.read_text(encoding="utf-8").strip()
        if text:
            docs.append({"text": text, "source": path.name})
    return docs


def clean_text(text: str) -> str:
    """
    Remove non-content artifacts while keeping substantive text.
    - Collapse runs of blank lines to a single blank line
    - Normalize horizontal whitespace (tabs → space, multiple spaces → one)
    - Strip HTML entities and any leftover angle-bracket tags
    """
    text = re.sub(r"<[^>]+>", " ", text)           # strip HTML tags if any
    text = re.sub(r"&[a-z]+;", " ", text)           # strip HTML entities
    text = re.sub(r"[ \t]+", " ", text)             # collapse horizontal whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)          # max one blank line between paragraphs
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = OVERLAP,
) -> list[str]:
    """
    Split text into chunks of at most chunk_size characters.

    Each chunk boundary snaps backward to the last sentence-ending
    punctuation (. ? !) before the limit so no chunk cuts mid-sentence.
    Consecutive chunks share `overlap` characters so concepts that span
    a boundary appear in full in at least one chunk.
    """
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)

        # Snap to sentence boundary only when more text follows
        if end < length:
            window = text[start:end]
            # Find the last sentence-ending punctuation in the window
            last_boundary = None
            for m in re.finditer(r'[.?!]["\']?\s', window):
                last_boundary = m
            if last_boundary:
                end = start + last_boundary.end()

        chunk = text[start:end].strip()
        if len(chunk) >= MIN_CHUNK:
            chunks.append(chunk)

        # Once we've consumed the last character, stop — don't let the
        # overlap calculation pull start back inside the document and spin.
        if end >= length:
            break

        next_start = end - overlap
        start = max(next_start, start + 1)

    return chunks


def extract_title(text: str) -> str:
    """
    Pull the document title from the first line if it starts with 'Title:'.
    Falls back to an empty string so chunks still work without a title.
    """
    first_line = text.splitlines()[0] if text else ""
    if first_line.startswith("Title:"):
        return first_line[len("Title:"):].strip()
    return ""


def build_chunk_corpus(
    folder: Path = DOCUMENTS_DIR,
) -> list[dict]:
    """
    Full pipeline: load → clean → chunk.

    Each chunk gets the document title prepended before embedding so that
    chunks mid-document still carry topic context (e.g. every chunk from
    the water-chemistry doc embeds with 'Water for Coffee Guide - KH Buffer...'
    at the top, preventing generic phrases like 'espresso taste' from
    pulling the wrong document to the top of retrieval results).

    Returns list of {text, source} dicts. 'text' is the title-prefixed
    version used for both embedding and storage.
    """
    docs = load_documents(folder)
    corpus = []
    for doc in docs:
        cleaned = clean_text(doc["text"])
        title = extract_title(cleaned)
        header = f"[{title}]\n" if title else ""
        for chunk in chunk_text(cleaned):
            corpus.append({"text": f"{header}{chunk}", "source": doc["source"]})
    return corpus


# ---------------------------------------------------------------------------
# Diagnostic output — run this file directly to inspect chunks before
# embedding. Verify: no fragments, no HTML, no empty strings, ~45–60 total.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    corpus = build_chunk_corpus()

    print(f"\n{'='*60}")
    print(f"Total chunks: {len(corpus)}")

    # Per-document breakdown
    from collections import Counter
    counts = Counter(c["source"] for c in corpus)
    print("\nChunks per document:")
    for source, n in sorted(counts.items()):
        print(f"  {source}: {n}")

    # 5 random chunks for manual inspection
    print(f"\n{'='*60}")
    print("5 random chunks — read each one and ask: is it self-contained?\n")
    samples = random.sample(corpus, min(5, len(corpus)))
    for i, chunk in enumerate(samples, 1):
        print(f"--- Chunk {i} | source: {chunk['source']} | {len(chunk['text'])} chars ---")
        print(chunk["text"])
        print()
