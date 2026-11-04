"""
01_context_budget.py
Experiment 5.01: Select retrieved evidence within a token budget.

Workflow:
1. Load current Orbit 3.0 chunks from the existing Chroma collection.
2. Rank candidates with BM25, dense retrieval, and reciprocal rank fusion.
3. Rerank the candidates with the existing cross-encoder.
4. Format each source and count its tokens for the generation model.
5. Keep complete sources that fit the context budget and report the result.

Expected result: Some relevant sources are skipped because they exceed the budget.
Run: uv run python 05_context_engineering/01_context_budget.py
"""

import re
from pathlib import Path

import chromadb
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"

COLLECTION_NAME = "teralune_corpus"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
GENERATION_MODEL = "gpt-4.1-mini"

TOP_K = 10
RRF_K = 60
CONTEXT_BUDGET = 650
QUESTION = "How long is an Orbit 3 access token valid?"


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def format_source(chunk_id: str, text: str, metadata: dict) -> str:
    title = metadata.get("title", "Untitled")
    version = metadata.get("version", "unknown")
    return (
        f"[Source: {chunk_id}]\nTitle: {title}\nVersion: {version}\nContent:\n{text}\n"
    )


def main() -> None:
    load_dotenv(PROJECT_DIR / ".env")
    client = OpenAI()

    # 1. Load the same current-version evidence used in Chapter 4.
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(
        COLLECTION_NAME
    )
    records = collection.get(
        where={"$and": [{"version": "3.0"}, {"status": "current"}]},
        include=["documents", "metadatas"],
    )
    chunks = {
        chunk_id: (document, metadata or {})
        for chunk_id, document, metadata in zip(
            records["ids"], records["documents"], records["metadatas"]
        )
    }
    if not chunks:
        raise RuntimeError("No current Orbit 3.0 chunks found. Build the index first.")

    # 2. Combine lexical and semantic rankings with RRF.
    ids = list(chunks)
    corpus_tokens = [tokenize(chunks[chunk_id][0]) for chunk_id in ids]
    bm25 = BM25Okapi(corpus_tokens)
    bm25_scores = bm25.get_scores(tokenize(QUESTION))
    lexical_ids = sorted(
        ids, key=lambda chunk_id: bm25_scores[ids.index(chunk_id)], reverse=True
    )[:TOP_K]

    query_embedding = (
        client.embeddings.create(model="text-embedding-3-small", input=QUESTION)
        .data[0]
        .embedding
    )
    dense_result = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        where={"$and": [{"version": "3.0"}, {"status": "current"}]},
    )
    dense_ids = dense_result["ids"][0]
    fused_scores: dict[str, float] = {}
    for ranking in (lexical_ids, dense_ids):
        for rank, chunk_id in enumerate(ranking, start=1):
            fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + 1 / (
                RRF_K + rank
            )
    candidate_ids = sorted(fused_scores, key=fused_scores.get, reverse=True)[:TOP_K]

    # 3. Rerank the hybrid candidates, just as in Chapter 4.
    reranker = CrossEncoder(RERANKER_MODEL)
    scores = reranker.predict(
        [(QUESTION, chunks[chunk_id][0]) for chunk_id in candidate_ids]
    )
    ranked_ids = [
        chunk_id
        for chunk_id, _ in sorted(
            zip(candidate_ids, scores), key=lambda item: float(item[1]), reverse=True
        )
    ]

    # 4. Count the complete formatted source blocks with the generation tokenizer.
    encoding = tiktoken.encoding_for_model(GENERATION_MODEL)
    selected: list[str] = []
    used_tokens = 0
    print(f"Question: {QUESTION}")
    print(f"Context budget: {CONTEXT_BUDGET} tokens ({GENERATION_MODEL})\n")
    print(f"{'Rank':<6}{'Chunk':<20}{'Tokens':>8}  Decision")

    # 5. Select whole source blocks without exceeding the budget.
    for rank, chunk_id in enumerate(ranked_ids, start=1):
        document, metadata = chunks[chunk_id]
        source = format_source(chunk_id, document, metadata)
        source_tokens = len(encoding.encode(source + "\n"))
        fits = used_tokens + source_tokens <= CONTEXT_BUDGET
        if fits:
            selected.append(source)
            used_tokens += source_tokens
        print(
            f"{rank:<6}{chunk_id:<20}{source_tokens:>8}  {'INCLUDED' if fits else 'SKIPPED'}"
        )

    context = "\n".join(selected)
    print(f"\nSelected: {len(selected)} / {len(ranked_ids)} sources")
    print(f"Used: {used_tokens} / {CONTEXT_BUDGET} tokens")
    print("\n--- SELECTED CONTEXT ---")
    print(context or "(No source fits the budget.)")
    print("--- END CONTEXT ---")


if __name__ == "__main__":
    main()
