# Teralune Pilotbericht 0.1.1

Stand 2026-10-15. Kleine redaktionelle und konzeptionelle Revision des freigegebenen Piloten 0.1.0. Der Umfang bleibt bei 14 tatsächlichen Dokumenten, 33 Evidence-IDs und 25 Fragen. Die übrigen 34 Dokumente sind ausschließlich geplant. Nach dieser Fassung wird ohne Skalierung gestoppt.

## Änderungen an den Dokumenten

Alle D001 bis D014 wurden neu erzeugt. Die kanonischen Fakten, Fragenformulierungen, Dokument-IDs, Evidence-IDs, Versionswerte und ACL-Zuordnungen bleiben erhalten.

| Dokumente | Änderung |
|---|---|
| Alle Markdown-Dateien | Identischen Synthetic-Absatz und Front Matter entfernt; Metadaten ausschließlich im Manifest |
| D006 HTML | Wiederkehrenden Synthetic-Absatz entfernt |
| D007 CSV | Spalte synthetic_notice und ihren wiederholten Inhalt entfernt; Planwerte unverändert |
| D013 PDF | Synthetic-Absatz sowie Synthetic-/Fictional-Text aus Header und Footer entfernt; Seitenstruktur erhalten |
| D014 DOCX | Synthetic-Absatz entfernt; Rollenprosa und Tabelle erhalten |
| D001 | fictional aus der Beschreibung der Organisation entfernt |
| D008 | Fiktiv-Hinweis und Erklärung der für den Datensatz erfundenen Kennungen entfernt |
| D010 | Erklärung des Fixture-Status entfernt; als betriebliches Register einer Sicherheitsübung formuliert |
| D011 | Erklärung der absichtlich falschen Aussage und des harmlosen Testpayloads entfernt; falsche 24-Stunden-Behauptung und zitierter Injection-Satz als importierte Betriebsnotiz erhalten |

D010 und D011 behalten security_fixture: true in Manifest und strukturierten Quellen. Zusätzliche fixture_notes erklären die Funktion ausschließlich außerhalb des Retrievaltexts. D011 bleibt unreviewed und untrusted; seine Behauptung ist weiterhin als intentional_conflicts mit dem kanonischen 72-Stunden-Fakt verknüpft. Historische 24 Stunden in D004 bleiben historisch korrekt. Realistische Versions- und Archivhinweise wurden nicht entfernt.

Der Corpus besitzt jetzt 2865 Wörter in den annotierten Passagen. Die Formate bleiben 10 Markdown sowie je einmal HTML, CSV, PDF und DOCX. Der Sprachmix bleibt 11 englische und 3 deutsche Dokumente. Das vollständige Manifest enthält unverändert 48 Dokumente mit geplantem Sprachmix 36/12.

## Evaluationsschema 1.1

expected_behavior ersetzt die redundanten Felder answerable und expected_action. Es gelten genau vier Werte:

| Wert | Bedeutung | Anzahl |
|---|---|---:|
| answer | Eindeutig mit zulässiger Evidenz beantwortbar | 19 |
| clarify | Information vorhanden, notwendige Eingrenzung fehlt | 1 |
| no_answer | Information im verfügbaren Corpus nicht vorhanden | 2 |
| deny | Benötigte Evidenz vorhanden, für Benutzer unzulässig | 3 |

Alle 25 Fragen wurden einzeln geprüft; Begründungen stehen in evaluation/question_review.json. Kein Fragetext wurde umgeschrieben.

Q012 bleibt inhaltlich mehrdeutig und erwartet clarify. Die alte Zielversionsvorgabe 3.0 wurde entfernt: product_version ist nun null. Es gibt keine positive Evidenz oder einzelne Musterantwort. Die erwartete Rückfrage richtet sich auf die Orbit-Version.

Q013 und Q014 wurden vom alten Sammelwert abstain zu no_answer umgestellt. Q016, Q018 und Q020 wurden von abstain zu deny umgestellt. Ihre blockierten Evidence-IDs bleiben interne Prüfdaten, niemals positive qrels oder Modellkontext. Q015, Q017 und Q019 bleiben die zulässigen ACL-Gegenstücke mit answer. Die übrigen 16 Antwortfragen behalten ihren fachlichen Status; auch versionsspezifische und mehrsprachige Fälle bleiben erhalten.

Ein deny darf nach außen keine Existenz, Titel oder Fakten geschützter Quellen bestätigen. Seine Formulierung kann deshalb einer no_answer-Antwort entsprechen. Unterschiedliche interne Bewertung bedeutet keine zusätzliche Offenlegung.

## Ground Truth und Build

Die Faktenbasis ist bytegleich zur 0.1.0-Fassung. Der Frageplan ist weiterhin unabhängig vom gerenderten Dokumenttext. Die Evidence-Texte von D001, D008, D010 und D011 wurden entsprechend der Textrevision aktualisiert; Evidence-IDs und Faktenbindungen bleiben stabil. Alle anderen Passagentexte sind unverändert. Die Smoke-Suite enthält weiterhin dieselben 25 Fragen und ist kein unabhängiger Holdout.

Der Build liest die überarbeiteten Quellen und erzeugt ausschließlich die 14 Pilotdateien. Der alte author_pilot.py-Initializer ist stillgelegt, damit er die neue Redaktion nicht versehentlich auf 0.1.0 zurücksetzt. Normale Builds verwenden unverändert scripts/build_corpus.py. source_documents/ und Checksummen werden daraus reproduzierbar erzeugt.

## Validierung und Tests

Der Validator prüft weiterhin IDs, Referenzen, kanonische Faktenbindungen, tatsächlich extrahierte PDF-/DOCX-Passagen, CSV-Werte, Manifestkonsistenz und ACL. Zusätzlich prüft er:

- ausschließlich gültige expected_behavior-Werte und Ausschluss alter Verhaltensfelder;
- answer nur mit zulässiger positiver Evidenz;
- clarify ohne feste Zielversion, ohne positive Fakten und mit Rückfrage;
- no_answer ohne positive und ohne blockierte Evidenz;
- deny mit tatsächlich unzugänglicher blockierter Evidenz und Offenlegungsschutz;
- Security-Fixture-Markierungen und Notizen im Manifest statt im Dokumenttext;
- bekannte Metaformulierungen in allen extrahierten Ausgabeformaten.

Die Meta-Prüfung erkennt unter anderem SECURITY FIXTURE, SYNTHETIC, fictional, fiktiv, deliberately incorrect und designed to test. Sie ist eine kuratierte Regressionsprüfung, keine allgemeine semantische Erkennung jeder möglichen Metaaussage. Der eigentliche Injection-Satz bleibt absichtlich erhalten und ist kein zu entfernender redaktioneller Hinweis.

Die Suite umfasst jetzt 16 Tests statt 6. Zehn neue Tests prüfen Verhaltenswerte, semantische Nicht-Antwort-Regeln, Clarify-Abgrenzung, unzugängliche ACL-Belege, fehlende Evidence-IDs, Fixture-Metadaten, bekannte Metaphrasen auch im extrahierten Dokumenttext und die dokumentierte Prüfung aller 25 Fragen. Die alten sechs Tests bleiben bestehen. Die direkten semantischen Fragetests greifen unabhängig von der Gleichheit zwischen Frageplan und JSONL, damit ein Fehler nicht nur als Dateidrift erkannt wird.

Ergebnis: Validator PASS, 16 von 16 Tests PASS. Zwei aufeinanderfolgende Builds erzeugen bytegleiche Corpus-Dateien und identische Evidence-/Frage-JSONL sowie Einzelquellen. Alle 14 Dateichecksummen unterscheiden sich erwartungsgemäß von 0.1.0 wegen der entfernten Boilerplates. PDF mit zwei Seiten und DOCX mit einer Seite wurden neu gerendert und vollständig visuell geprüft. Umgebung und Prüfergebnisse stehen in evaluation/validation_report.json; das Testprotokoll steht in evaluation/test_results.txt.

## Dokumentation und verbleibende Grenzen

README, AUTHOR_GUIDE, EVALUATION, Weltmodell und Lizenzattribution sind an 0.1.1 angepasst. Synthetic-Herkunft und Fixture-Zwecke sind dort weiterhin eindeutig dokumentiert. Die Lizenzzuordnung bleibt CC BY 4.0 für Inhalte und MIT für eigenständigen Code.

Die verbleibenden Grenzen des Piloten ändern sich nicht: kleines Datenvolumen, redaktionelle statt unabhängiger Annotation, keine exhaustive Relevanzbeurteilung und noch keine vollständige atomare Claim-Annotation für automatische Citation-Metriken. ACL wird über öffentliche synthetische Dateien simuliert. Die strukturellen Prüfungen ersetzen keine unabhängige fachliche Prüfung freier Prosa.

Es wurden keine weiteren Dokumente erzeugt, keine Retrieval-Benchmarks oder Chunking-Experimente durchgeführt, keine Embedding-Modelle verglichen und keine RAG-Anwendung oder Buchinhalte gebaut. Der vollständige Pilot 0.1.1 wird erneut zur redaktionellen Prüfung vorgelegt.
