"""
Lädt verschiedene Dokumentformate in eine gemeinsame Repräsentation.

Formatspezifische Parser extrahieren den Inhalt aus CSV-, HTML-, DOCX-
und PDF-Dateien. Das Ergebnis ist jeweils ein Document-Objekt, mit dem
die weiteren Schritte der RAG-Pipeline unabhängig vom Dateiformat
arbeiten können.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader

PROJECT_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_DIR / "data" / "teralune-rag-corpus" / "corpus"


@dataclass
class Document:
    """Repräsentiert ein eingelesenes Dokument mit Quelle und Inhalt."""

    document_id: str
    source: str
    text: str


def load_csv(path: Path) -> Document:
    """Liest eine CSV-Datei und erhält Zeilen und Spalten als Text."""
    lines: list[str] = []

    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file)

        for row in reader:
            lines.append(" | ".join(row))

    return Document(
        document_id=path.stem,
        source=str(path.relative_to(PROJECT_DIR)),
        text="\n".join(lines),
    )


def load_html(path: Path) -> Document:
    """Extrahiert lesbaren Text aus einem HTML-Dokument."""
    html: str = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    return Document(
        document_id=path.stem,
        source=str(path.relative_to(PROJECT_DIR)),
        text=soup.get_text("\n", strip=True),
    )


def load_docx(path: Path) -> Document:
    """Extrahiert die Absätze aus einem DOCX-Dokument."""
    document = DocxDocument(path)
    paragraphs: list[str] = [
        paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()
    ]

    return Document(
        document_id=path.stem,
        source=str(path.relative_to(PROJECT_DIR)),
        text="\n".join(paragraphs),
    )


def load_pdf(path: Path) -> Document:
    """Extrahiert Text aus allen Seiten eines PDF-Dokuments."""
    reader = PdfReader(path)
    pages: list[str] = []

    for page in reader.pages:
        text: str = page.extract_text() or ""
        pages.append(text)

    return Document(
        document_id=path.stem,
        source=str(path.relative_to(PROJECT_DIR)),
        text="\n".join(pages),
    )


files: list[Path] = [
    CORPUS_DIR / "public" / "D007.csv",
    CORPUS_DIR / "public" / "D020.html",
    CORPUS_DIR / "customer" / "D027.docx",
    CORPUS_DIR / "public" / "D031.pdf",
]

loaders = {
    ".csv": load_csv,
    ".html": load_html,
    ".docx": load_docx,
    ".pdf": load_pdf,
}

for path in files:
    document: Document = loaders[path.suffix](path)

    print("\n" + "=" * 70)
    print(f"Document: {document.document_id}")
    print(f"Format: {path.suffix}")
    print(f"Source: {document.source}")
    print(f"Characters: {len(document.text)}")
    print("-" * 70)
    print(document.text[:1000])
