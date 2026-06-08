"""
Milestone 5 — Grounded generation.

ask(question) -> {"answer": str, "sources": list[str]}

Grounding guarantees:
- Context is built only from retrieved chunks (no external knowledge injected).
- System prompt forbids inference beyond the provided documents.
- Source list is assembled programmatically from retrieval metadata —
  it is never extracted from the LLM's response text.
- Chunks from the same document are merged so the model sees each source once.
- Chunks with cosine distance > DISTANCE_CUTOFF are dropped before generation.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv
from groq import Groq
from retrieve import retrieve

load_dotenv()
client = Groq()

MODEL = "llama-3.3-70b-versatile"
TOP_K = 5
DISTANCE_CUTOFF = 0.65   # drop chunks with weak semantic match

SYSTEM_PROMPT = """\
You are a specialty coffee reference assistant.
Answer using ONLY the exact content of the source documents provided below.
Rules you must follow:
1. Do not use any knowledge from outside the provided documents.
2. Do not infer, extrapolate, or speculate. No phrases like "likely", "probably", "it can be inferred", or "suggests".
3. If the documents do not contain enough information to answer, respond with exactly: "My documents don't cover that."
4. Do not include source filenames in your answer — they are shown to the user separately.
"""


def ask(question: str) -> dict:
    """
    Retrieve relevant chunks, build a grounded prompt, call the LLM.
    Returns {"answer": str, "sources": list[str]}.
    Sources are derived from retrieval metadata, not from the LLM output.
    """
    raw_chunks = retrieve(question, top_k=TOP_K)

    # Drop chunks that are too far from the query
    chunks = [c for c in raw_chunks if c["distance"] <= DISTANCE_CUTOFF]

    if not chunks:
        return {
            "answer": "My documents don't cover that.",
            "sources": [],
        }

    # Merge chunks from the same source so the model sees each document once
    by_source: dict[str, list[str]] = {}
    for c in chunks:
        by_source.setdefault(c["source"], []).append(c["text"])

    context = "\n\n---\n\n".join(
        f"[Document: {source}]\n" + "\n\n".join(texts)
        for source, texts in by_source.items()
    )

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Documents:\n{context}\n\nQuestion: {question}",
            },
        ],
    )

    return {
        "answer": response.choices[0].message.content.strip(),
        "sources": list(by_source.keys()),   # programmatic — not from LLM
    }


if __name__ == "__main__":
    test_queries = [
        "How does water hardness (specifically KH vs. GH) alter the taste profile of a coffee brew?",
        "What specific technologies or profiling features are introduced in the La Marzocco Strada X?",
        "Can you compare the flavor expectations and mechanical steps between washed and natural coffee processing?",
        "What specific temperature should milk be steamed to for a perfect cappuccino?",
    ]
    for q in test_queries:
        result = ask(q)
        print(f"\n{'='*65}")
        print(f"Q: {q}")
        print(f"{'='*65}")
        print(result["answer"])
        print(f"\nSources: {', '.join(result['sources']) or 'none'}")
