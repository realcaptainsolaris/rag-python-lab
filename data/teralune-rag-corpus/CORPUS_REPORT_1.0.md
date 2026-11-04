# Teralune RAG Corpus 1.0 Abschlussbericht

Version 1.0.0, eingefrorener Produktstand 2026-10-15. Ausbau des freigegebenen Piloten 0.1.1 auf den vollständigen Manifestumfang. Alle 48 geplanten Dokumente sind vorhanden; es wurden keine beliebigen zusätzlichen Corpusdateien hinzugefügt.

## Umfang

48 Dokumente, 146 Evidence-Passagen und 120 Fragen. Die annotierte Prosa umfasst 13176 Wörter; Tabellenzellen sind in dieser Wortzählung nicht enthalten. Dokumente variieren von 42 bis 737 Wörtern Prosa. Kurze CSV-Referenzen und längere mehrteilige Guides sind bewusst unterschiedlich lang.

## Verteilung nach Dokumenttyp

| Wert | Anzahl |
|---|---:|
| guide | 11 |
| reference | 11 |
| legacy | 4 |
| migration | 1 |
| pricing_reference | 1 |
| support_case | 5 |
| runbook | 3 |
| security_fixture | 2 |
| policy | 2 |
| faq | 3 |
| release_notes | 2 |
| engineering | 1 |
| incident | 2 |

## Verteilung nach Sprache

| Wert | Anzahl |
|---|---:|
| en | 36 |
| de | 12 |

## Verteilung nach Dateiformat

| Wert | Anzahl |
|---|---:|
| md | 36 |
| html | 3 |
| csv | 3 |
| pdf | 3 |
| docx | 3 |

## Verteilung nach Access-Level

| Wert | Anzahl |
|---|---:|
| PUBLIC | 35 |
| CUSTOMER | 6 |
| INTERNAL | 5 |
| RESTRICTED | 2 |

## Verteilung nach Produktversion

| Wert | Anzahl |
|---|---:|
| 3.0 | 42 |
| 2.4 | 3 |
| 1.8 | 3 |

## Verteilung nach Erwartetes Verhalten

| Wert | Anzahl |
|---|---:|
| answer | 99 |
| clarify | 6 |
| no_answer | 6 |
| deny | 9 |

## Verteilung nach Fragetyp

| Wert | Anzahl |
|---|---:|
| version_specific | 7 |
| exact_identifier | 14 |
| paraphrase | 19 |
| multilingual | 6 |
| table_lookup | 8 |
| multi_evidence | 14 |
| conflict_resolution | 4 |
| ambiguous | 6 |
| unanswerable | 6 |
| access_restricted | 11 |
| exact_fact | 25 |

## Evidence, Splits und besondere Fälle

25 bekannte Pilotfragen bilden den Smoke-Satz; 95 neue Fragen bilden den Test-Satz. Die Frage-IDs überschneiden sich nicht. Gleicher Wortlaut ist nur bei markierten ACL-Gegenstücken mit anderem Benutzer vorgesehen; solche Paare bleiben im selben Split. Es gibt bewusst thematische und faktische Überlappung zwischen Entwicklung und Test. Das ist kein blinder wissenschaftlicher Benchmark.

14 Fragen sind als multi_evidence klassifiziert. Davon referenzieren 11 mehrere Passagen; drei bündeln mehrere Fakten innerhalb einer Passage. Insgesamt referenzieren 35 Antwortfragen mehr als eine Passage, teilweise als alternative Belege, und 20 Fragen mehr als ein Dokument. Diese Zahlen sind keine Garantie, dass jeder aufgeführte Beleg logisch unverzichtbar ist; die Claim-Unterstützung muss bei der Auswertung berücksichtigt werden.

13 Dokumente sind als Chunking-Challenges markiert und im AUTHOR_GUIDE einzeln mit IDs, strukturellen Besonderheiten und logischen Zusammenhängen beschrieben. Verschachtelte Child-Abschnitte haben zusätzliche Parent-Referenzen außerhalb des Produkttexts. Es wird keine optimale Größe oder Strategie behauptet.

Es gibt 3 maschinenlesbar markierte Security-Fixtures: D010, D011 und D037. Davon enthalten zwei indirekte Injection und falsche aktuelle Vertragsbehauptungen. Der Dokumenttyp security_fixture zählt nur zwei, weil D037 weiterhin ein Supportfall ist. D034 enthält historisch korrekte alte Werte und ist davon zu unterscheiden. D040 besitzt einen weiteren funktionslosen Übungsmarker in einem normalen Security-Runbook.

## Kanonische Welt und minimale Korrekturen

Alle bereits im Pilot vorhandenen Faktenwerte wurden rekursiv gegen 0.1.1 geprüft und beibehalten. Neue Fakten für die manifestgeplanten Themen wurden zuerst festgelegt: Geräte-Lifecycle, Messwertschema, Pagination, Alertregeln, Rotation, Teamverwaltung, Abrechnungsgrenzen, Retention-Cleanup, Eventkatalog und Worker-Recovery. Texte verwenden gebundene Platzhalter und strukturierte Tabellen. Die Ground Truth ist ein eigener redaktioneller Frageplan, keine nachträgliche Extraktion aus zufälligem Output.

D036 war im alten Plan trotz Cobalt-Titel Amber zugeordnet. Die Zuordnung wurde auf org-cobalt korrigiert und mit passenden positiven/negativen Benutzerfällen versehen. Der übrige Access-Mechanismus wurde nicht neu entworfen.

Das vierteilige Verhaltensmodell bleibt answer, clarify, no_answer, deny. Eine kleine Überverallgemeinerung des Pilotvalidators wurde korrigiert: Nicht jede Rückfrage bedeutet eine unbekannte Generation. clarification_field benennt die fehlende Angabe; bei unbekanntem Plan, unbekannter Rolle oder unbekanntem Alerttyp darf eine bekannte Version erhalten bleiben. Bei fehlender Version bleibt sie null. Die booleschen Altfelder wurden nicht wieder eingeführt.

Der Faktenresolver wurde für verschachtelte Eventnamen mit Punkten verallgemeinert. Bestehende Versionspfade wie versions.2.4 bleiben gültig. Evidence-IDs des Piloten bleiben stabil. Die Builder unterstützen jetzt mehrere unterschiedliche CSV-/HTML-/DOCX-Tabellen aus denselben strukturierten Quellen statt fest eingebauter Plan- oder Rollentabellen.

## Validierung und Tests

Validator: PASS. Tests: 23 von 23 PASS. Tatsächliche Umgebung, Abhängigkeiten und Prüfergebnisse stehen in evaluation/validation_report.json. Das vollständige Testprotokoll steht in evaluation/test_results.txt.

Geprüft werden Dokument-/Frage-/Evidence-/Benutzer-IDs, vollständige Manifestumsetzung, genau 48 tatsächliche Dateien, Versionen, Sprachen, Zugriffe, Rollen, Feature-Tags, kanonische Bindungen, ausgabeseitige Textpräsenz und Tabellenwerte, Parent-Referenzen, qrels, Split-Zuordnung und vier Verhaltensklassen. no_answer und clarify haben keine positive Ground Truth. deny benötigt existierende, tatsächlich unzulässige Evidence und einen Offenlegungsschutz. Positive qrels müssen im angegebenen Benutzerkontext zugänglich sein.

Negative Tests decken unbekannte Features, kaputte Evidence, unzulässige positive Fakten, verwechslte Rückfragen, ACL-Grenzen, fehlende Fixture-Metadaten, bekannte Corpus-Metaleaks, überlappende Splits und Dokumentduplikate ab. Der Duplikatcheck verwendet normalisierte Fünfwort-Shingles mit Jaccard-Schwelle 0,65. Er ist eine deterministische Kopierprüfung, keine semantische Plagiatserkennung. Der höchste beobachtete Wert ist 0.0125 für D013, D031; das ist eine Corpus-QA-Kennzahl, kein Retrieval-Ergebnis.

Ein Test kopiert das Release in ein temporäres Verzeichnis und baut es zweimal neu. Alle Corpusdateien, Einzelquellen sowie Evidence-, Fragen-, Split- und Checksummen-Ausgaben bleiben bytegleich. Dafür ist kein Netzwerkzugriff erforderlich. PDF und DOCX werden vollständig aus editierbaren Quellen erzeugt. Alle sechs PDF-Seiten und fünf gerenderten DOCX-Seiten wurden visuell geprüft. Ein beschädigtes temporäres PNG der Sichtprüfung wurde neu gerendert; die PDF-Datei und ihre Textextraktion waren gültig. QA-Bilder sind kein Bestandteil des Releases.

## Bekannte Grenzen

Der Corpus ist ein kontrollierter Lehr- und Evaluationsbestand, nicht unabhängig wissenschaftlich validiert. Freie Prosa und natürlichsprachliche Musterantworten sind redaktionell formuliert; die Validatoren beweisen keine vollständige semantische Widerspruchsfreiheit. Faktenbindungen und Prüfungen tatsächlicher Dateiinhalte reduzieren gemeinsame Fehler, ersetzen aber keine zweite fachliche Redaktion.

Die qrels sind kuratiert und nicht exhaustiv. Zusätzliche gültige Quellen müssen vor quantitativen Vergleichen nachannotiert werden. Für vollautomatische Citation Precision/Recall fehlt noch eine vollständige atomare Claim-Annotation. Der öffentliche Test-Satz ist nicht nach Faktenfamilien isoliert und verliert nach wiederholter Optimierung seinen Holdout-Charakter.

Die Texte sind überwiegend kompakt. Es gibt keine OCR, keine gescannten Seiten und keine stark beschädigten Office-Dokumente. Die frühere grobe Planung von 300 bis 800 Chunks wird nicht als erreicht behauptet. Tatsächliche Chunkzahlen hängen vom gewählten Tokenizer, Fenster, Overlap und Strukturerhalt ab und wurden nicht experimentell ermittelt. Die längeren Guides und mehrteiligen Kontextfälle sind für erste strukturbezogene Vergleiche vorgesehen, nicht als Ersatz für große reale Handbücher.

ACL ist eine Anwendungssimulation über öffentliche synthetische Dateien. Fixture-Markierungen liegen nur in Metadaten; ein späterer Lauf muss ihren Einschluss ausdrücklich dokumentieren. Der Corpus enthält keine realen Secrets oder aktiven Angriffsrückkanäle. Die Namenswahl ist fiktiv und beinhaltet keine Markenfreigabe.

## Abschluss

README, WORLD, EVALUATION und AUTHOR_GUIDE sind für 1.0 aktualisiert. Der historische Pilotbericht liegt ausdrücklich unter docs/history. Die Lizenzzuordnung bleibt CC BY 4.0 für Inhalte und MIT für eigenständigen Code.

Es wurden keine Retrieval-, Embedding-, Chunking-, Hybrid- oder Reranker-Benchmarks ausgeführt. Es wurden keine Rankings oder Performance-Werte erfunden, keine ButterBeaver-Integration gebaut und keine Buchinhalte erzeugt. Das Release endet hier und wird als teralune-rag-corpus-1.0.0.zip zur technischen und redaktionellen Prüfung vorgelegt.
