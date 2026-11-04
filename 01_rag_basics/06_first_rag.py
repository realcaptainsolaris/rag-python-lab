"""
Baut aus semantischer Suche und einem Sprachmodell ein erstes
vollständiges RAG-System.

Zunächst werden die relevantesten Teralune-Orbit-Texte für eine Frage
ermittelt. Diese Texte werden anschließend als Kontext an das
Sprachmodell übergeben, das daraus eine Antwort erzeugt.
"""

from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

client = OpenAI()

documents = [
    "Orbit retries failed webhook deliveries for 72 hours.",
    "Orbit access tokens are valid for 60 minutes.",
    "Orbit retains telemetry data for 90 days.",
    "Orbit limits API clients to 1000 requests per minute.",
    "Orbit exports telemetry data in CSV and JSON format.",
]

question = "How long does Orbit retry a failed webhook delivery?"

embedding_response = client.embeddings.create(
    model="text-embedding-3-small",
    input=documents + [question],
)

embeddings = [item.embedding for item in embedding_response.data]

document_embeddings = embeddings[:-1]
question_embedding = embeddings[-1]

similarities = cosine_similarity(
    [question_embedding],
    document_embeddings,
)[0]

results = sorted(
    zip(documents, similarities),
    key=lambda item: item[1],
    reverse=True,
)

top_results = results[:2]

context = "\n".join(document for document, _ in top_results)

print("Retrieved context:")
print(context)

generation_response = client.responses.create(
    model="gpt-5.6",
    instructions=(
        "Answer the question using only the provided context. "
        "If the context does not contain enough information to answer "
        "the question, say that you do not know."
    ),
    input=f"""
Context:
{context}

Question:
{question}
""",
)

print("\nAnswer:")
print(generation_response.output_text)
