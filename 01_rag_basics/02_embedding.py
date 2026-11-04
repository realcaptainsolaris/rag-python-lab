"""
Erzeugt ein Embedding für einen kurzen Text über Teralune Orbit.

Das Beispiel zeigt, dass ein Embedding-Modell einen Text in einen
hochdimensionalen numerischen Vektor umwandelt.
"""

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

text = "Orbit retries failed webhook deliveries for 72 hours."

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text,
)

embedding = response.data[0].embedding

print("Text:")
print(text)

print(f"\nVector dimensions: {len(embedding)}")

print("\nFirst 10 values:")
print(embedding[:10])
