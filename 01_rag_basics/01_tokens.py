"""
Zeigt, wie ein Text vor der Verarbeitung durch ein Sprachmodell
in Tokens zerlegt wird.

Das Beispiel macht sichtbar, dass Sprachmodelle Texte nicht direkt als
Wörter verarbeiten, sondern als numerisch repräsentierte Token.
"""

import tiktoken

text = "Orbit retries failed webhook deliveries for 72 hours."

encoding = tiktoken.get_encoding("o200k_base")
tokens = encoding.encode(text)

print("Text:")
print(text)

print("\nToken IDs:")
print(tokens)

print(f"\nNumber of tokens: {len(tokens)}")

print("\nIndividual tokens:")

for token_id in tokens:
    token = encoding.decode([token_id])
    print(f"{token_id:>8} -> {token!r}")
