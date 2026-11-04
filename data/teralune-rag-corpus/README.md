# Teralune RAG Training Corpus

Version 1.0.0. Ein kontrollierter Lehr-, Experimentier- und Evaluationsdatensatz für RAG mit Python, geeignet als gemeinsamer Dokumentbestand für ein Fachbuch und eine drei- bis viertägige Schulung. Der Corpus ist kein wissenschaftlich validierter Benchmark.

Teralune Systems, Teralune Orbit, sämtliche Organisationen, Personen, Supportfälle und Geschäftsdaten sind vollständig synthetisch. Namensähnlichkeiten sind unbeabsichtigt; eine Markenverfügbarkeitsprüfung wird nicht behauptet. Die technischen Produkttexte wurden für dieses Projekt erstellt. Die Erstellung erfolgte mit KI-Unterstützung und einer strukturierten redaktionellen Faktenbasis.

## Was enthalten ist

48 Dokumente in fünf Formaten, 146 annotierte Evidenzstellen und 120 Evaluationsfragen. Die Produktwelt umfasst Geräteidentitäten, Messdaten, Authentifizierung, Webhooks, Alerts, Exporte, Rollen, Abrechnung und Betrieb. Die Dokumente enthalten keine wiederkehrenden Synthetic-Hinweise oder Erklärungen ihrer Rolle als Retrieval-Testfall. Diese Informationen stehen ausschließlich in Projektdateien und Metadaten.

| Merkmal | Verteilung |
|---|---|
| Sprache | 36 Englisch, 12 Deutsch |
| Dateiformat | 36 Markdown, je 3 HTML, CSV, PDF und DOCX |
| Zugriff | 35 PUBLIC, 6 CUSTOMER, 5 INTERNAL, 2 RESTRICTED |
| Produktgeneration | 3 Dokumente 1.8, 3 Dokumente 2.4, 42 Dokumente 3.0 |
| Evaluationssplit | 25 Smoke, 95 Test |

Die Dokumentklassen reichen von kurzen Tabellenreferenzen bis zu mehrteiligen Guides, Supportfällen, Runbooks und Incident-Berichten. Mehrere Dokumente besitzen verschachtelte Überschriften; PDF enthält echte Seitenumbrüche sowie wiederkehrende Header und Seitenzahlen. Die verschiedenen Formate sind eigenständige Dokumente, keine mehrfachen Kopien eines Handbuchs.

## Projektstruktur

| Pfad | Zweck |
|---|---|
| `corpus/` | Ausschließlich ingestierbare Produktdokumente, nach Zugriff gruppiert |
| `source/facts.yaml` | Single Source of Truth, JSON-kompatibles YAML 1.2 |
| `source/documents.json` | Editierbare Texte, kanonische Platzhalter, Tabellen und Hierarchie |
| `source/document_manifest.json` | Alle 48 Dokumente mit Sprache, Version, Zugriff, Status und Quellenautorität |
| `source/question_plan.json` | Redaktioneller Frage- und Ground-Truth-Plan |
| `source/evaluation_splits.json` | Feste Zuordnung der Frage-IDs zu Smoke und Test |
| `source_documents/` | Reproduzierbar erzeugte Einzelquellen pro Dokument |
| `evaluation/` | Fragen, Evidence, Rollen, Review und tatsächliche Prüfergebnisse |
| `AUTHOR_GUIDE.md` | Dokumentauswahl, Themenzuordnung und Chunking-Challenges |
| `EVALUATION.md` | Verhalten, Splits, Evidence-Zuordnung und Metrikdefinitionen |
| `CORPUS_REPORT_1.0.md` | Verteilungen, Änderungen, Prüfstand und Grenzen |
| `docs/history/` | Historischer Pilotbericht, kein aktueller Corpusinhalt |

Nur `corpus/` ingestieren. Faktenbasis, Autorenhandbuch, Fragen und Reports würden Lösungen und Lehrmetadaten in den Suchindex tragen. Zugriffs- und Versionsmetadaten separat anhand des Manifests an Dokumente und Chunks binden. Markdown enthält absichtlich kein Front Matter.

## Installation

Python 3.11 oder neuer. Getestet wurde Python 3.12 mit den direkt gepinnten Abhängigkeiten in requirements.txt; die genaue Umgebung steht in evaluation/validation_report.json. Keine GPU, kein API-Key und kein Modell-Download erforderlich.

```bash
python -m venv .venv
# Linux oder macOS
source .venv/bin/activate
# Windows PowerShell stattdessen:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/validate_corpus.py
python -m unittest discover -s tests -v
```

Dateien nach einer Quellenänderung neu erzeugen:

```bash
python scripts/build_corpus.py
python scripts/validate_corpus.py
python -m unittest discover -s tests -v
```

Der Build arbeitet ohne Netzwerk und ohne Sprachmodell. Er überschreibt generierte Dateien. Änderungen gehören in die strukturierten Quellen. Der alte Pilot-Initializer ist stillgelegt. PDF und DOCX werden aus editierbaren Dokumentquellen erzeugt; binäre Container-Zeitstempel sind normalisiert. Die Tests vergleichen die Ausgaben mit zwei erneuten Builds in einem temporären Verzeichnis. Bytegleichheit wird für die geprüfte Umgebung zugesichert, nicht pauschal für beliebige zukünftige Bibliotheksversionen.

## Versionen und Quellenautorität

Orbit 1.8 ist Legacy, 2.4 die frühere Generation, 3.0 die aktuelle Generation am eingefrorenen Stichtag 2026-10-15. API-Präfix, Tokenlaufzeit, Retryfrist, Retention, Requestbudget, Eventnamen und Schlüsselmodell unterscheiden sich. Ein korrekter alter Vertrag ist keine falsche aktuelle Dokumentation. Dokumentstatus und Autorität stehen im Manifest.

D011 enthält eine falsche aktuelle Retry-Aussage und eine harmlose indirekte Prompt Injection. D037 enthält eine veraltete Tokenbehauptung samt weiterer Injection in einer Kundenanlage. D010 enthält einen funktionslosen Übungsmarker. Diese drei Quellen sind maschinenlesbar als Security-Fixtures markiert, ohne dies im Retrievaltext zu erklären. Es werden keine realen Secrets oder externen Rückkanäle verwendet. Für Experimente den Fixture-Einschluss protokollieren.

## Zugriff und Benutzer

PUBLIC ist frei. CUSTOMER erfordert dieselbe Organisation, INTERNAL Staff und das zugeordnete Team, RESTRICTED zusätzlich die expliziten Rollen. Rollen bilden keine pauschale Rangordnung. Ein Kunden-Admin hat keinen internen Zugriff; Operations und Security haben unterschiedliche Teamgrenzen. Benutzer stehen in evaluation/users.json. Die deterministische Beispielrichtlinie befindet sich in scripts/common.py.

Die Zugriffsstufen simulieren Anwendungsberechtigungen über öffentlich verfügbare synthetische Dateien. Sie bieten keine echte Geheimhaltung des Repositorys. Zulässige Kandidaten vor Reranking und vor LLM-Kontext bestimmen. Die spätere Anwendung muss diesen Schutz selbst umsetzen; der Datensatz allein beweist ihn nicht.

## Evaluation

| expected_behavior | Erwartung |
|---|---|
| answer | Eindeutige Antwort mit zulässiger Evidenz |
| clarify | Notwendige Angabe fehlt, obwohl relevante Informationen vorhanden sind |
| no_answer | Benötigte Information fehlt im verfügbaren Corpus |
| deny | Evidenz existiert, ist für diesen Benutzer aber unzulässig |

`deny` ist eine interne Bewertungsklasse. Die öffentliche Antwort darf weder geschützte Inhalte noch deren Existenz bestätigen und kann wie `no_answer` formuliert sein.

questions.jsonl enthält den Gesamtbestand. smoke_questions.jsonl enthält die 25 bekannten Pilotfragen für Entwicklung und Sanity Checks, test_questions.jsonl die 95 neuen Fragen für systematischere Auswertungen. Die IDs sind disjunkt. Inhaltliche Themen überschneiden sich absichtlich; das ist kein blinder oder nach Faktenfamilien isolierter Benchmark. Gleicher Fragetext ist nur für ausdrücklich markierte ACL-Gegenstücke mit unterschiedlichem Benutzer erlaubt; solche Paare bleiben im selben Split.

Evidence referenziert stabile logische Passagen und bei Tabellen die strukturierten Zeilen mit Spaltennamen. Chunk-IDs werden nicht vorgegeben. Metriken müssen gegen die tatsächlich erhaltene Evidenz, nicht nur gegen eine ähnliche Überschrift ausgewertet werden. Die qrels sind kuratiert und nicht garantiert exhaustiv. Vor einer quantitativen Rangbewertung zusätzliche relevante Treffer nachannotieren. Für automatische Citation Precision/Recall fehlt noch eine vollständige atomare Claim-Annotation.

## Grenzen und Lizenz

Kurzer, kontrollierter technischer Bestand mit rund 13000 Wörtern in den annotierten Passagen. Keine OCR, keine gescannten PDFs, keine chaotischen Office-Altbestände und keine realen Kundendaten. Die vorhandenen Chunking-Fälle beschreiben mögliche Probleme, keine erwiesene Überlegenheit einer Strategie. Die frühere grobe Planung von 300 bis 800 Chunks wird für diese Fassung nicht als erreicht behauptet; die tatsächliche Anzahl hängt von Tokenizer, Fenster, Overlap und Strukturerhalt ab und wurde nicht experimentell bestimmt.

Inhalte und Evaluationsdaten: CC BY 4.0. Eigenständiger Code: MIT. LICENSE und LICENSE-CODE enthalten die Zuordnung und Namensnennung. Kommerzielle Nutzung in Büchern und Schulungen ist unter diesen Bedingungen vorgesehen. Es wurden keine Retrieval-, Embedding-, Chunking- oder Reranker-Benchmarks durchgeführt und keine Performance-Werte behauptet.
