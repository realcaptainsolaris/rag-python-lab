"""
Liest die Struktur eines Markdown-Dokuments aus.

Das Beispiel trennt Überschriften und zugehörige Textabschnitte,
ohne bereits Retrieval-Chunks daraus zu erzeugen.
"""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_FILE = (
    PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus" / "public" / "D022.md"
)


def parse_markdown(text):
    sections = []
    current_heading = None
    current_lines = []

    for line in text.splitlines():
        if line.startswith("#"):
            if current_heading is not None:
                sections.append(
                    {
                        "heading": current_heading,
                        "text": "\n".join(current_lines).strip(),
                    }
                )

            current_heading = line
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading is not None:
        sections.append(
            {
                "heading": current_heading,
                "text": "\n".join(current_lines).strip(),
            }
        )

    return sections


text = DOCUMENT_FILE.read_text(encoding="utf-8")
sections = parse_markdown(text)

print(f"Document: {DOCUMENT_FILE.name}")
print(f"Sections: {len(sections)}")

for section in sections:
    print("\n" + "-" * 60)
    print(section["heading"])
    print(f"Characters: {len(section['text'])}")
    print(section["text"][:250])
