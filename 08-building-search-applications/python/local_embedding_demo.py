"""Local Embedding-style demo for Lesson 08.

This script uses TF-IDF vectors as an offline stand-in for model embeddings.
It is not a replacement for OpenAI/Azure embeddings, but it makes the search
pipeline visible without requiring an API key.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "embedding_index_3m.json"


def load_documents() -> list[dict]:
    with INDEX_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> int:
    query = " ".join(sys.argv[1:]).strip() or "what are jupyter notebooks"
    docs = load_documents()
    texts = [item.get("summary") or item.get("text") or item.get("title", "") for item in docs]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    doc_vectors = vectorizer.fit_transform(texts)
    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, doc_vectors).ravel()

    top_indices = scores.argsort()[::-1][:5]

    print(f"Query: {query}")
    print("Top matches:")
    for rank, index in enumerate(top_indices, start=1):
        item = docs[index]
        title = item.get("title", "(untitled)")
        start = item.get("start", "00:00:00")
        video_id = item.get("videoId", "")
        url = f"https://www.youtube.com/watch?v={video_id}&t={int(item.get('seconds', 0))}s"
        print(f"{rank}. score={scores[index]:.4f} | {title} | {start}")
        print(f"   {url}")
        print(f"   {texts[index][:180].replace(chr(10), ' ')}...")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
