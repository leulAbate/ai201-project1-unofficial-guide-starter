"""
Milestone 4 — Embed chunks and load into ChromaDB.

Run this script once (or re-run to rebuild the collection).
Reads chunks from ingest.py, embeds with all-MiniLM-L6-v2,
and persists a ChromaDB collection at ./chroma_db/.
"""

from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

from ingest import build_chunk_corpus

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "coffee_guide"
MODEL_NAME = "all-MiniLM-L6-v2"


def build_vector_store() -> chromadb.Collection:
    corpus = build_chunk_corpus()

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Embedding {len(corpus)} chunks...")
    texts = [c["text"] for c in corpus]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Always rebuild clean — drop stale collection if it exists
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Dropped existing collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[
            {"source": c["source"], "chunk_index": i}
            for i, c in enumerate(corpus)
        ],
        ids=[f"chunk_{i}" for i in range(len(corpus))],
    )

    print(f"\nVector store ready: {len(corpus)} chunks in '{COLLECTION_NAME}'")
    print(f"Persisted at: {Path(CHROMA_PATH).resolve()}")
    return collection


if __name__ == "__main__":
    build_vector_store()
