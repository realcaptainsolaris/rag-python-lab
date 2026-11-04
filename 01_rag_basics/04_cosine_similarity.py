"""
Vergleicht eine Benutzerfrage mit mehreren Teralune-Orbit-Texten.

Die semantische Ähnlichkeit wird mit Cosine Similarity bestimmt.
Dadurch lässt sich erkennen, welcher Text inhaltlich am besten zur
gestellten Frage passt.
"""

from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

client = OpenAI()

texts = [
    "Orbit retries failed webhook deliveries for 72 hours.",
    "Orbit access tokens are valid for 60 minutes.",
    "Orbit retains telemetry data for 90 days.",
]

question = "How long are failed webhooks retried?"

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts + [question],
)

embeddings = [item.embedding for item in response.data]

document_embeddings = embeddings[:-1]
question_embedding = embeddings[-1]

similarities = cosine_similarity(
    [question_embedding],
    document_embeddings,
)[0]

for text, score in zip(texts, similarities):
    print(f"{score:.4f} | {text}")
