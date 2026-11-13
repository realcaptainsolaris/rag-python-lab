# RAG mit Python: Praxislabor

**Python-Experimente zu Retrieval-Augmented Generation (RAG), Embeddings, Vektordatenbanken und modernen Retrieval-Verfahren.**

Dieses Repository enthält den begleitenden Python-Code zum frei verfügbaren Online-Buch:

### [Einführung in RAG mit Python: Online-Buch lesen](https://rag.friendlybytes.net/)

Das Buch erklärt die theoretischen Grundlagen und technischen Entscheidungen hinter RAG-Systemen. Dieses Repository liefert die praktischen Experimente dazu.

Ziel ist es, die einzelnen Komponenten eines RAG-Systems zu verstehen und selbst zu implementieren, statt ihre Funktionsweise hinter umfangreichen Frameworks zu verbergen.

## Inhalte

Die Experimente orientieren sich an den Kapiteln des Buchs.

| Verzeichnis | Thema |
|---|---|
| `01_rag_basics/` | Grundlagen von RAG, Tokens und erste RAG-Pipelines |
| `02_documents_and_chunking/` | Dokumente einlesen, parsen und chunken |
| `03_embeddings_and_vector_database/` | Embeddings, Ähnlichkeitssuche und Vektordatenbanken |
| `04_retrieval/` | Retrieval-Verfahren, Ranking und Metadatenfilter |
| `05_context_engineering/` | Kontextaufbereitung und Grounding |
| `06_evaluation_and_debugging/` | Retrieval-Evaluation, Antwortqualität und Debugging |
| `09_advanced_rag/` | Fortgeschrittene Retrieval-Strategien |
| `data/` | Beispieldokumente und Testdaten |

Die Beispiele können einzeln ausgeführt, verändert und miteinander verglichen werden.

## Voraussetzungen

Für die Übungen werden benötigt:

* Python, entsprechend der Version in `.python-version`
* [uv](https://docs.astral.sh/uv/) als Python-Paketmanager
* Grundkenntnisse in Python
* Für Experimente mit OpenAI-Modellen ein gültiger OpenAI-API-Schlüssel

Erfahrung mit RAG, Embeddings oder Vektordatenbanken ist nicht erforderlich.

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/realcaptainsolaris/rag-python-lab.git
cd rag-python-lab
```

Alternativ kann das Repository über **Code → Download ZIP** heruntergeladen werden.

### 2. Abhängigkeiten installieren

```bash
uv sync
```

`uv` erstellt bei Bedarf eine virtuelle Python-Umgebung und installiert die in `pyproject.toml` definierten Abhängigkeiten.

### 3. API-Schlüssel konfigurieren

Einige Experimente verwenden die OpenAI API.

Kopiere die bereitgestellte Beispielkonfiguration:

```bash
cp env_example .env
```

Trage anschließend deinen API-Schlüssel in `.env` ein:

```dotenv
OPENAI_API_KEY=your-api-key
```

Die Datei `.env` darf nicht in Git eingecheckt werden.

### 4. Experimente ausführen

Die Python-Skripte lassen sich mit `uv run` starten.

Beispiel:

```bash
uv run python 01_rag_basics/01_tokens.py
```

Die konkreten Dateinamen und Ausführungsparameter sind den jeweiligen Experimenten zu entnehmen.

## Der Teralune-Corpus

Für viele Experimente verwenden wir den **Teralune-Corpus**, eine synthetische Unternehmensdokumentation eines fiktiven Cloud-Anbieters.

Der Corpus enthält unter anderem:

* Technische Produktdokumentationen
* Unterschiedliche Produktversionen
* Historische und aktuelle Informationen
* Bewusst eingebaute Widersprüche
* Metadaten und Referenzinformationen für Retrieval und Evaluation

Damit lassen sich typische Herausforderungen realer RAG-Systeme reproduzieren.

Beispielsweise kann ein Retrieval-System eine technisch korrekte Information finden, die jedoch aus einer veralteten Produktversion stammt.

Solche Fälle zeigen, warum semantische Ähnlichkeit allein nicht ausreicht und weshalb Metadatenfilter, Ranking und Evaluation wichtige Bestandteile einer RAG-Architektur sind.

Weitere Informationen enthält das Online-Buch:

[Anhang A: Der Teralune-Corpus](https://rag.friendlybytes.net/10-anhang-a-der-teralune-corpus/)

## Lernkonzept

Die Experimente verfolgen drei grundlegende Prinzipien.

**1. Verstehen statt abstrahieren**

Wir implementieren zentrale Mechanismen zunächst selbst, beispielsweise Kosinusähnlichkeit, Chunking-Strategien oder einfache Retrieval-Pipelines.

**2. Experimentieren statt nur ausführen**

Die Beispiele sollen verändert werden. Unterschiedliche Chunk-Größen, Suchparameter, Filter und Kontextstrategien können zu deutlich unterschiedlichen Ergebnissen führen.

**3. Ergebnisse kritisch bewerten**

Ein RAG-System kann überzeugende Antworten erzeugen und trotzdem falsche oder veraltete Informationen verwenden.

Deshalb betrachten wir nicht nur die Antwortgenerierung, sondern auch Retrieval-Qualität, Grounding und systematische Evaluation.

## Online-Buch

Die vollständigen theoretischen Erklärungen, Architekturdiagramme und Hintergrundinformationen stehen kostenlos zur Verfügung:

**[Einführung in RAG mit Python](https://rag.friendlybytes.net/)**

Das Buch behandelt den Weg von ersten Embeddings und Retrieval-Experimenten bis zu Architektur, Sicherheit, Evaluation und fortgeschrittenen RAG-Verfahren.

## Lizenz

Die Nutzungsbedingungen richten sich nach der Lizenz des Repositories. Eine Lizenzdatei sollte ergänzt werden, falls der Code ausdrücklich zur Weiterverwendung freigegeben werden soll.

## Autor

**Bernd Fischer**

[Online-Buch: Einführung in RAG mit Python](https://rag.friendlybytes.net/)
