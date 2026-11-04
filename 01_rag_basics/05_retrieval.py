"""
Implementiert eine minimale semantische Suche über mehrere
Teralune-Orbit-Texte.

Die Texte und die Benutzerfrage werden als Embeddings repräsentiert.
Anschließend werden die Texte anhand ihrer Cosine Similarity zur
Frage sortiert und die relevantesten Treffer ausgegeben.
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

question = "What happens when a webhook delivery fails?"

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=documents + [question],
)

embeddings = [item.embedding for item in response.data]

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

print(f"Question: {question}\n")

for document, score in results[:3]:
    print(f"{score:.4f} | {document}")
