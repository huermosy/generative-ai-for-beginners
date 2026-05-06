from __future__ import annotations

from pathlib import Path

import numpy as np
from openai import OpenAI


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
KEY_PATH = Path(r"C:\OpenaiKey.txt")
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"


def load_client() -> OpenAI:
    assert KEY_PATH.exists(), f"Key file not found: {KEY_PATH}"
    api_key = KEY_PATH.read_text(encoding="utf-8").strip()
    assert api_key, f"Key file is empty: {KEY_PATH}"
    return OpenAI(api_key=api_key)


def chunk_markdown(text: str) -> list[str]:
    chunks = []
    current = []
    for line in text.splitlines():
        if line.startswith("#") and current:
            chunks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current).strip())
    return [chunk for chunk in chunks if chunk]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va = np.array(a)
    vb = np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def build_chunks() -> list[dict]:
    items = []
    for path in sorted(DATA_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for index, chunk in enumerate(chunk_markdown(text), start=1):
            items.append(
                {
                    "source": path.name,
                    "chunk_id": index,
                    "text": chunk,
                }
            )
    return items


def main() -> None:
    client = load_client()
    query = "What is a perceptron and how is it used in neural networks?"

    chunks = build_chunks()
    chunk_texts = [item["text"] for item in chunks]

    chunk_embeddings = client.embeddings.create(
        model=EMBED_MODEL,
        input=chunk_texts,
    ).data
    query_embedding = client.embeddings.create(
        model=EMBED_MODEL,
        input=query,
    ).data[0].embedding

    scored = []
    for item, embedding_item in zip(chunks, chunk_embeddings):
        score = cosine_similarity(query_embedding, embedding_item.embedding)
        scored.append({**item, "score": score})

    top_chunks = sorted(scored, key=lambda item: item["score"], reverse=True)[:3]
    context = "\n\n".join(
        f"[{item['source']}#{item['chunk_id']} score={item['score']:.4f}]\n{item['text']}"
        for item in top_chunks
    )

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Answer only from the provided context. If the context is insufficient, say so plainly."
            },
            {
                "role": "user",
                "content": f"Question: {query}\n\nContext:\n{context}"
            },
        ],
    )

    print("Query:")
    print(query)
    print("\nTop retrieved chunks:")
    for item in top_chunks:
        print(f"- {item['source']}#{item['chunk_id']} score={item['score']:.4f}")

    print("\nFinal answer:")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
