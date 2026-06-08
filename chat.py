"""
Quick test script — ask a question, see a grounded response.
This is a preview of the full Milestone 5 generation pipeline.

Usage:
    python chat.py                  # interactive loop
    python chat.py "your question"  # single query
"""

import sys
from dotenv import load_dotenv
from groq import Groq
from retrieve import retrieve

load_dotenv()
client = Groq()

SYSTEM_PROMPT = """You are a specialty coffee reference assistant.
Answer using ONLY the exact content of the source excerpts provided.
Rules:
- Do not infer, extrapolate, or draw conclusions beyond what the excerpts state.
- Do not use phrases like "it can be inferred", "likely", or "suggests".
- If the excerpts do not contain enough information to answer, say exactly: "My documents don't cover that."
- Cite the source filename for every claim you make."""


def ask(question: str) -> str:
    chunks = retrieve(question, top_k=5)

    context = "\n\n".join(
        f"[Source {i+1}: {c['source']}]\n{c['text']}"
        for i, c in enumerate(chunks)
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(ask(" ".join(sys.argv[1:])))
    else:
        print("Specialty Coffee Guide — type a question or 'quit' to exit\n")
        while True:
            q = input("You: ").strip()
            if q.lower() in ("quit", "exit", "q"):
                break
            if q:
                print(f"\nAssistant: {ask(q)}\n")
