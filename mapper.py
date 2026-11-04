uv run python - <<'PY'
import chromadb

collection = chromadb.PersistentClient(
    path="data/chroma"
).get_collection("teralune_corpus")

data = collection.get(
    ids=["D001-chunk-2", "D003-chunk-1", "D004-chunk-1"],
    include=["documents", "metadatas"],
)

for chunk_id, document, metadata in zip(
    data["ids"],
    data["documents"],
    data["metadatas"],
):
    print(f"\n{chunk_id}")
    print(f"Headings: {metadata.get('headings')}")
    print(f"Access: {metadata.get('access')}")
    print(f"Text: {document[:350]!r}")
PY
