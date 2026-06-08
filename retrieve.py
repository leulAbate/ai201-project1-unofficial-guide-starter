from __future__ import annotations

"""
Milestone 4 — Retrieval function.

retrieve(query, top_k) embeds the query with the same model used at index time
and returns the top_k closest chunks from ChromaDB with distance scores.

ChromaDB uses cosine distance: 0.0 = identical, 1.0 = orthogonal.
Good retrieval: distance < 0.4. Weak match: distance > 0.6.
"""

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "coffee_guide"
MODEL_NAME = "all-MiniLM-L6-v2"

# Module-level singletons — loaded once, reused across calls
_model: SentenceTransformer | None = None
_collection: chromadb.Collection | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """
    Return the top_k most relevant chunks for the query.
    Each result: {text, source, chunk_index, distance}
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query], convert_to_numpy=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "text": doc,
                "source": meta["source"],
                "chunk_index": meta["chunk_index"],
                "distance": round(dist, 4),
            }
        )
    return chunks


# ---------------------------------------------------------------------------
# Test retrieval with 3 evaluation plan queries before wiring in the LLM.
# For each result ask: is this chunk actually relevant to the question?
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_queries = [
        "What causes channeling in espresso and how can I prevent it?",
        "What is the difference between flat burr and conical burr grinders in terms of flavor?",
        "What does KH do to the taste of espresso, and what KH level is ideal?",
    ]

    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"QUERY: {query}")
        print("=" * 70)
        results = retrieve(query, top_k=4)
        for i, r in enumerate(results, 1):
            print(f"\n  Result {i} | source: {r['source']} | distance: {r['distance']}")
            print(f"  {r['text'][:300]}{'...' if len(r['text']) > 300 else ''}")
