"""
Erzeugt Embeddings für mehrere thematisch unterschiedliche Texte
aus der Teralune-Orbit-Dokumentation.

Das Beispiel bereitet die spätere Ähnlichkeitssuche vor. Jeder Text
wird durch einen eigenen Vektor repräsentiert.
"""

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

texts = [
    "Orbit retries failed webhook deliveries for 72 hours.",
    "Orbit access tokens are valid for 60 minutes.",
    "Orbit retains telemetry data for 90 days.",
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts,
)

for text, item in zip(texts, response.data):
    print(text)
    print(f"Dimensions: {len(item.embedding)}")
    print(f"First values: {item.embedding[:5]}")
    print()
