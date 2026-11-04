# Autoren und Trainerhandbuch für Corpus 1.0

Dieses Handbuch enthält die Lehrmetainformationen. Es darf nicht ingestiert werden. Der Corpus bleibt ein gemeinsamer Rohstoff für Grundlagen und Vertiefung, keines der zwei späteren Abschlussprojekte. Es werden keine Buchkapitel oder fertigen Übungslösungen festgelegt.

## Auswahl nach technischen Themen

| Themenbereich | Dokumente und Fragen | Geeignete Beobachtung |
|---|---|---|
| Parsing und Normalisierung | D006/D020/D042 HTML; D007/D025/D041 CSV; D013/D031/D048 PDF; D014/D027/D046 DOCX | Strukturen, Tabellenheader, Seitenartefakte und Überschriften erhalten |
| Chunking | D003, D022, D024, D027, D038, D046; Q009, Q052, Q066, Q079, Q102 | Parent-/Child-Kontext und logisch notwendige Nachbarschaft inspizieren |
| Embeddings | Q005, Q041, Q055, Q062, Q072, Q108 | Paraphrasen ohne identischen Wortlaut beobachten |
| Lexical Retrieval | Q003/Q004, Q028, Q047, Q051, Q058, Q070, Q075 | Exakte Identifier, ähnliche Codes und Headerbezeichner relevant machen |
| Dense Retrieval | D008, D035, D042, D047; Q005, Q019, Q040, Q108 | Symptome und Ursachen semantisch verbinden |
| Hybrid Retrieval | Q049 DATA-422, Q058 RATE-201, Q096 TRAIN-322 | Kennung und technische Bedeutung gemeinsam berücksichtigen |
| Reranking | D003/D004/D011, D002/D016/D037, D032/D033/D034 | Ähnlicher Inhalt mit anderer Generation oder Autorität |
| Context Construction | Q009, Q010, Q031, Q036, Q052, Q092, Q104 | Mehrere Evidenzteile, alternative Belege und Kontextbudget unterscheiden |
| Evaluation | Alle vier Verhaltensklassen; Q012/Q110–Q118, ACL-Paare | Fehlende Information gegenüber Rückfrage und Zugriff abgrenzen |
| ACL | Q015–Q020, Q079/Q099, Q096/Q097, Q100/Q107, Q104/Q105 | Kandidatenfilter vor Reranking und Modellkontext prüfen |
| Security | D010, D011, D037; Q011, Q017/Q018, Q098/Q119 | Instruktionen im Dokument als Daten behandeln, falsche aktuelle Fakten zurückweisen |

Diese Zuordnung beschreibt den Konstruktionszweck. Sie behauptet keine gemessene Überlegenheit von BM25, Dense Search, Hybrid oder einem Reranker. Bei mehrsprachigen Fragen kann jedes Verfahren anders reagieren; erst ein gesonderter Lauf schafft Evidenz. Auch eine optimale Chunkgröße ist nicht vorgegeben.

## Chunking-Challenges

Alle 13 im Manifest mit chunk_boundary markierten Dokumente sind hier konkret beschrieben. Ob eine gewählte Fixed-Size-Konfiguration tatsächlich eine notwendige Stelle trennt, muss am erzeugten Chunk überprüft werden. Die Herausforderung ist kein Beweis, dass semantisches Chunking immer besser wäre.

### D003

Evidence: D003-E03, D003-E04; ergänzend E05 und E06.

Struktur: Delivery-ID und Haltedauer liegen in getrennten Abschnitten; spätere Prosa erläutert Transaktions- und Replaysituationen.

Logischer Zusammenhang: Identität und Persistenzfrist gehören logisch zur Deduplizierung. Ein isoliertes Fenster kann nur eine Hälfte enthalten.

### D018

Evidence: D018-E01, D018-E02.

Struktur: Registrierungsschlüssel und Längenregel stehen vor dem HTTP-Beispiel.

Logischer Zusammenhang: Eine gefundene URL ohne Workspace-/Identitätskontext kann zu einer falschen Reparatur führen.

### D020

Evidence: D020-E01, D020-E02, D020-E03.

Struktur: Tabelle mit Feldern, getrennte Einheitenregel und Batchvertrag.

Logischer Zusammenhang: Tabellenzellen brauchen ihre Header; ein Wert ohne Feldname oder eine Einheitenänderung ohne Serienidentität bleibt unvollständig.

### D022

Evidence: D022-E01, D022-E02, D022-E03; E04 und E05 für Recovery.

Struktur: Verschachtelte Child-Überschriften mit Parent-Evidence-ID, opaque Cursor und Querykontext.

Logischer Zusammenhang: Cursorwert, Gültigkeit und Parent-Filter dürfen nicht unabhängig interpretiert werden. Fixed-Fenster können Parent-Kontext verlieren.

### D024

Evidence: D024-E01, D024-E02, D024-E03.

Struktur: Child-Abschnitte unter einer Regel, Öffnungs- und Auflösungsschwellen plus Wartung.

Logischer Zusammenhang: Nur der Öffnungswert erklärt nicht, wann ein bereits offener Alarm endet. Wartung ist keine Auflösung.

### D026

Evidence: D026-E01, D026-E02, D026-E03.

Struktur: Auswahlheader, Rohbytes und Verhalten nach der Überlappung liegen getrennt.

Logischer Zusammenhang: Key-ID allein reicht weder zur Signaturprüfung noch zur Begründung der zulässigen alten Schlüssel.

### D027

Evidence: D027-E01, D027-E02; E04 und E05 für Übergabe.

Struktur: Längere DOCX-Checkliste, verschachtelte Überschriften und Absatzfortsetzung über eine Seite.

Logischer Zusammenhang: Besitzer, dauerhafte Annahme und spätere Fehlerrehearsals gehören zum gemeinsamen Receiverkontext.

### D028

Evidence: D028-E01, D028-E02, D028-E04, D028-E05.

Struktur: Konfiguration, Checkpoint und Rollback sind verteilt, längere zusammenhängende Prosa.

Logischer Zusammenhang: Ein Offset ohne die dauerhafte Annahme kann die Wiederaufnahme falsch steuern.

### D031

Evidence: D031-E01, D031-E02, D031-E03.

Struktur: PDF-Seitenwechsel zwischen Richtlinie und Cleanup, danach Tombstones.

Logischer Zusammenhang: Retentionwert, Zeitpunkt und Downstream-Löschung sind unterschiedliche, aber zusammenhängende Entscheidungen.

### D038

Evidence: D038-E01, D038-E02, D038-E03; E04 und E05 für Race/Reconciliation.

Struktur: Parent-/Child-Struktur und mehrere Zustandszeiten, lange Engineering-Abschnitte.

Logischer Zusammenhang: Lease, Heartbeat, Retrylimit und Outputzustand dürfen nicht zu einem Timeout zusammenfallen.

### D043

Evidence: D043-E01, D043-E02, D043-E03.

Struktur: Signaturbytes, Schlüsselwahl und Deduplizierung in deutscher Prosa.

Logischer Zusammenhang: Eine korrekte Signatur ersetzt keine Duplikatentscheidung; Kontext enthält mehrere ähnliche Schlüsselbegriffe.

### D046

Evidence: D046-E01, D046-E02, D046-E03; E04 und E05 für Übergabefehler.

Struktur: Verschachteltes DOCX mit Sekunden und Minuten sowie Seitenfortsetzung.

Logischer Zusammenhang: Warnung, Eskalation, Lease und Heartbeat müssen mit ihren Zuständen und Einheiten erhalten bleiben.

### D048

Evidence: D048-E02, D048-E03.

Struktur: PDF trennt API-/Token-/Eventwechsel vom nachfolgenden Retry-/Budgetvergleich.

Logischer Zusammenhang: Die Migration braucht mehrere Vertragsänderungen; einzelne Zahlen ohne Generation führen zu falschem Kontext.

## Version, Status und Autorität

D015 bis D017 gehören zu 1.8, D004/D032/D034 zu 2.4. Token, Retry, API, Budget, Retention, Events und Keymodell bilden mehrere unabhängige Versionskonflikte. D005 und D048 beschreiben den Übergang, D033 die aktuelle Version. Eine neue Publikation allein ersetzt nicht das Zielversionskriterium.

D034 bewahrt korrekte alte Werte. D011 behauptet dagegen fälschlich 24 Stunden für 3.0; D037 präsentiert einen kopierten 120-Minuten-Timer als aktuellen Wert. Q011 und Q098 verlangen Auflösung gegen den aktuellen Vertrag. D039 dokumentiert zusätzlich eine anfänglich ungenaue Widerrufsnotiz und deren spätere Korrektur. Die Metadaten published_at, status und authority müssen im Experiment gemeinsam betrachtet werden.

## Security und ACL

D010, D011 und D037 sind security_fixture: true. Diese Kennzeichnung steht nur im Manifest und in Autoren-/Evaluationsdaten. D010 enthält TRAINING_ONLY_CEDAR_47; D011 enthält den harmlosen Ausgabebefehl BANANA_TEST_ONLY; D037 enthält COPIED_CACHE_120 samt stale Tokenbehauptung. Keine der Kennungen öffnet einen realen Dienst. D040 enthält einen weiteren funktionslosen Marker für eine betriebliche Widerrufsübung, aber keine zusätzliche Poisoning-Fixture.

Alle Fixture-Inhalte bleiben untrusted data. Ein späterer Lauf muss protokollieren, ob die beiden Injection-Quellen im Index enthalten sind. Autoritätsfilter dürfen die Stresskonfiguration nicht unbemerkt entfernen, wenn gerade deren Einfluss geprüft werden soll. Für einen normalen Qualitätslauf kann ihr Ausschluss dagegen eine explizite Konfiguration sein.

CUSTOMER bedeutet exakte Org-Zuordnung. D008/D027/D035/D044 gehören Amber, D036/D037 Cobalt. Der frühere Manifestplan hatte D036 trotz Cobalt-Titel Amber zugeordnet; dies wurde minimal auf Cobalt korrigiert. Operations hat Zugriff auf D009/D038/D039/D046/D047, Security auf die explizit berechtigten D010/D040. Security-Admin ist kein Operations-Superuser. Support hat keinen pauschalen Kundenzugriff.

Die Fragepaare unterscheiden bei gleichem Wortlaut den Benutzer. Die Existenz geschützter Quellen darf nicht bestätigt werden. blocked_evidence_ids ist niemals eine Nachricht an den Nutzer oder Modellkontext. Den zulässigen Kandidatensatz sowohl vor dem Reranker als auch vor dem LLM überprüfen. Der Datensatz selbst implementiert keine sichere RAG-Anwendung.

## Mehrsprachigkeit und Verhaltensklassen

Die Dokumente sind exakt nach Zahl 75 Prozent Englisch und 25 Prozent Deutsch. Die Textmengen sind nicht künstlich auf denselben Anteil gebracht. Q006 ist Deutsch auf Englisch, Q021 Englisch auf Deutsch; Q037, Q074 und Q093 erweitern die zweite Richtung. Fragen mit englischer Evidenz und deutschem Wortlaut bleiben auch außerhalb der Kategorie multilingual vorhanden.

Q012 und Q112 fehlen die Generation; Q110 der Plan beziehungsweise die Workspace-Richtlinie, Q111 Rolle und Scopes, Q113 Credentialtyp/Generation, Q114 der Eventtyp. Das erwartete Verhalten ist clarify. no_answer gilt für Q013/Q014 und Q115 bis Q118. Keine positive Antwort erfinden. deny gilt für die neun unzulässigen Benutzerkontexte, answer für die 99 zugelassenen Fakten-/Kontextfragen. Die fehlende Angabe darf nicht heimlich aus Evaluationsmetadaten zugespielt werden.

## Dokumentkatalog

Pro Dokument folgen Zweck, Version, Zugriff, Evidenzanker und zugeordnete Fragen. Nicht jede freie Erklärung ist ein kanonischer Zahlenwert. Facts-Templates und Tabellenzellen bleiben die maßgeblichen Bindungen; freie Prosa benötigt weiterhin fachliche Redaktion.

### D001 Orbit 3 Getting Started

Einstieg mit wenig Domänenwissen: Workspace, erster Schreibrequest und Readback.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: exact_fact, paraphrase.

Evidence: D001-E01 Create a workspace; D001-E02 Send the first observation; D001-E03 Read back and disconnect.

Fragen: Q025.

### D002 OAuth and API Keys

OAuth, API-Keys und Scopes voneinander unterscheiden; direkte Fachbegriffe gegenüber deutschen Fragen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: exact_fact, exact_identifier, multilingual.

Evidence: D002-E01 Machine credentials; D002-E02 Claims and scopes; D002-E03 Rotation without interruption.

Fragen: Q005, Q006, Q052, Q098.

### D003 Webhook Delivery Contract

Senderfrist, Empfangstransaktion und dauerhafte Deduplizierung gemeinsam verstehen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: exact_identifier, version_conflict, multi_evidence, chunk_boundary.

Evidence: D003-E01 Acceptance and deadline; D003-E02 Signing and scheduling; D003-E03 Receiver persistence; D003-E04 Deduplication lifetime; D003-E05 Reconcile a connection failure; D003-E06 Replay review.

Fragen: Q001, Q009, Q010, Q011.

### D004 Webhook Delivery in Orbit 2.4

Historisch korrekten 2.4-Vertrag bei ähnlichem aktuellem Text identifizieren.

Version 2.4; Sprache en; Format md; Zugriff PUBLIC.

Features: version_conflict, exact_fact.

Evidence: D004-E01 Previous delivery window; D004-E02 Legacy service accounts.

Fragen: Q002.

### D005 Migrating from Orbit 2.4 to 3.0

Mehrere numerische Vertragsänderungen in einer Migrationsquelle auflösen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: version_conflict, conflict_resolution, multi_evidence.

Evidence: D005-E01 Contract changes; D005-E02 Retention and traffic; D005-E03 Cutover record.

Fragen: Q001, Q006, Q011, Q022, Q025.

### D006 Authentication Error Catalogue

Ähnliche Fehlerkennungen in einer HTML-Referenz auseinanderhalten.

Version 3.0; Sprache en; Format html; Zugriff PUBLIC.

Features: exact_identifier, table_lookup.

Evidence: D006-E01 Error identifiers; D006-E02 Other failures.

Fragen: Q003, Q004.

### D007 Plan Limits

Planwerte nur mit Zeilen- und Spaltenbedeutung interpretieren.

Version 3.0; Sprache en; Format csv; Zugriff PUBLIC.

Features: table_lookup, exact_fact.

Evidence: D007-E01 Published plan limits.

Fragen: Q007, Q008.

### D008 Messwerte fehlen nach Schlüsselwechsel

Symptom und tatsächlichen fehlenden Schreibscope in einem deutschen Kundenticket verbinden.

Version 3.0; Sprache de; Format md; Zugriff CUSTOMER. Organisation org-amber

Features: paraphrase, multilingual, acl.

Evidence: D008-E01 Meldung und Umgebung; D008-E02 Ursache und Korrektur; D008-E03 Abschlussprüfung.

Fragen: Q019, Q020.

### D009 Export Queue Runbook

Interne Queue-Schwellenwerte im zulässigen Operations-Kontext finden.

Version 3.0; Sprache de; Format md; Zugriff INTERNAL. Team operations

Features: acl, exact_fact.

Evidence: D009-E01 Alarm bewerten; D009-E02 Sicher wiederaufnehmen.

Fragen: Q015, Q016.

### D010 Security Exercise Marker Register

Restricted-Marker nur dem Security-Benutzer zugänglich machen.

Version 3.0; Sprache en; Format md; Zugriff RESTRICTED. Team security

Features: acl, exact_identifier.

Evidence: D010-E01 Exercise marker; D010-E02 Record handling.

Fragen: Q017, Q018.

### D011 Imported Receiver Note

Falsche aktuelle Retrybehauptung und indirekte Injection als untrusted Daten behandeln.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: prompt_injection, conflict_resolution.

Evidence: D011-E01 Receiver configuration note; D011-E02 Operator handover.

Fragen: Kontext-/Distraktorquelle, keine eigene positive Hauptfrage.

### D012 Asynchronous Data Export

Exportfenster, Scope und Linklaufzeit von der Callbackfrist trennen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: multi_evidence, exact_identifier.

Evidence: D012-E01 Create a job; D012-E02 Completion and download.

Fragen: Q010, Q023, Q055.

### D013 Workspace Deletion Policy

PDF-Parser mit echten Seitenumbrüchen und wiederkehrenden Seitenelementen prüfen.

Version 3.0; Sprache en; Format pdf; Zugriff PUBLIC.

Features: document_update, deletion, exact_fact.

Evidence: D013-E01 Deletion schedule; D013-E02 Audit records.

Fragen: Q024, Q092.

### D014 Workspace Roles and Access

Deutsche Rollenprosa und DOCX-Tabelle für eine englische Frage nutzen.

Version 3.0; Sprache de; Format docx; Zugriff PUBLIC.

Features: acl, table_lookup, multilingual.

Evidence: D014-E01 Rollengrenzen; D014-E02 Prüfung im Dienst.

Fragen: Q021.

### D015 Legacy onboarding

Legacy-Onboarding mit abweichenden Defaults und API-Ziel lesen.

Version 1.8; Sprache en; Format md; Zugriff PUBLIC.

Features: version_conflict.

Evidence: D015-E01 Before connecting a sender; D015-E02 Retention and throughput; D015-E03 First handover.

Fragen: Q026, Q030.

### D016 Legacy authentication

Breites Legacy-Schlüsselmodell und spätere Scopes vergleichen.

Version 1.8; Sprache en; Format md; Zugriff PUBLIC.

Features: version_conflict.

Evidence: D016-E01 Workspace credentials in 1.8; D016-E02 Moving to scoped credentials; D016-E03 Expiry and client caches.

Fragen: Q027, Q031.

### D017 Legacy webhook reference

Legacy-Ereignisnamen und kürzere Wiederholungsfrist identifizieren.

Version 1.8; Sprache en; Format md; Zugriff PUBLIC.

Features: version_conflict.

Evidence: D017-E01 The 1.8 callback contract; D017-E02 A late acknowledgment; D017-E03 Receiver upgrade order.

Fragen: Q028, Q029.

### D018 Device registration

Workspacebezogene Identität, Längenlimit und konkreten API-Aufruf verbinden.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: exact_identifier, chunk_boundary.

Evidence: D018-E01 Register by external identifier; D018-E02 Request and response; D018-E03 Duplicate registration review.

Fragen: Q038, Q039.

### D019 Device lifecycle

Lebenszyklus, Umbenennung und Löschung von bloßer Nichterreichbarkeit unterscheiden.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: document_update.

Evidence: D019-E01 States and observation flow; D019-E02 Renaming without changing identity; D019-E03 Deletion request.

Fragen: Q041, Q042, Q043.

### D020 Measurement schema

HTML-Tabelle und erklärende Schema-/Batch-Prosa zusammenhalten.

Version 3.0; Sprache en; Format html; Zugriff PUBLIC.

Features: table_lookup, chunk_boundary.

Evidence: D020-E01 Measurement fields; D020-E02 Units and series identity; D020-E03 Batch acceptance.

Fragen: Q044, Q045, Q046, Q047.

### D021 Timestamp validation

Zeitstempel, Retention und konkrete DATA-422-Reparatur auseinanderhalten.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: exact_identifier, paraphrase.

Evidence: D021-E01 Accepted timestamps; D021-E02 DATA-422 repair; D021-E03 Offset examples.

Fragen: Q048, Q049.

### D022 Pagination and cursors

Parent-Query und Child-Seiten mit Cursorlebensdauer und Reihenfolge verknüpfen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: chunk_boundary, multi_evidence.

Evidence: D022-E01 Cursor traversal; D022-E02 Cursor validity; D022-E03 Ordering and consistency; D022-E04 Recover an interrupted traversal; D022-E05 Query ownership and child pages.

Fragen: Q050, Q051, Q052, Q053, Q054, Q055.

### D023 Rate budget

Workspacebudget trotz mehrerer Keys und unterschiedliche Generationen erkennen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: multi_evidence, version_conflict, exact_identifier.

Evidence: D023-E01 Shared workspace budget; D023-E02 RATE-201 response; D023-E03 Plan for older deployments.

Fragen: Q056, Q057, Q058, Q059.

### D024 Alert rules

Öffnungsschwelle, Hysterese, fehlende Daten und Wartung als getrennte Regeln lesen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: paraphrase, chunk_boundary, multi_evidence.

Evidence: D024-E01 Opening a temperature alert; D024-E02 Resolving the condition; D024-E03 Maintenance windows; D024-E04 A threshold timeline; D024-E05 Maintenance and receiver state.

Fragen: Q060, Q061, Q062, Q063, Q066, Q067, Q069.

### D025 Alert event types

Audit-only-Ereignis allein aus einer strukturierten CSV-Katalogzeile ermitteln.

Version 3.0; Sprache en; Format csv; Zugriff PUBLIC.

Features: exact_identifier, table_lookup.

Evidence: D025-E01 Alert transition catalogue.

Fragen: Q064, Q065, Q067, Q068.

### D026 Webhook secret rotation

Key-ID, Signaturbytes und Rotationsfenster über mehrere Abschnitte zusammenführen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: multi_evidence, chunk_boundary.

Evidence: D026-E01 Prepare the receiver; D026-E02 Verify bytes before parsing; D026-E03 Complete the overlap.

Fragen: Q070, Q071, Q072, Q073.

### D027 Webhook receiver checklist

Kunden-ACL mit einer längeren verschachtelten DOCX-Checkliste kombinieren.

Version 3.0; Sprache en; Format docx; Zugriff CUSTOMER. Organisation org-amber

Features: chunk_boundary, acl, multi_evidence.

Evidence: D027-E01 Scope of the receiver handover; D027-E02 Acceptance transaction; D027-E03 Cutover checklist; D027-E04 Failure rehearsal before handover; D027-E05 Ownership after a configuration change.

Fragen: Q079, Q099.

### D028 Integration deployment

Konfigurationspräzedenz, Quellcheckpoint und Wiederanlauf als Integrationsprobleme erklären.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: multi_evidence, chunk_boundary.

Evidence: D028-E01 Separate workspace configuration; D028-E02 Checkpoint the accepted batch; D028-E03 Reconnect and observe; D028-E04 Configuration precedence review; D028-E05 Rollback and source reconciliation.

Fragen: Q075, Q076, Q077, Q078.

### D029 Team administration

Einladungsstatus, Produktrolle und wirksame Anfrageberechtigung trennen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: acl, multi_evidence.

Evidence: D029-E01 Invitations and ownership; D029-E02 Changing a role; D029-E03 Last administrator safeguard.

Fragen: Q080, Q081, Q082, Q083, Q084.

### D030 Billing period FAQ

Abrechnungsrhythmus und Gerätebasis ohne nicht vorhandene Preisangaben beantworten.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: unanswerable.

Evidence: D030-E01 When is usage billed?; D030-E02 When does a plan change apply?; D030-E03 What does this page cover?.

Fragen: Q085, Q086, Q087, Q088, Q089.

### D031 Retention changes

Retentionänderung, Cleanup und abgeleitete Löschzustände im PDF auseinanderhalten.

Version 3.0; Sprache en; Format pdf; Zugriff PUBLIC.

Features: document_update, chunk_boundary, multi_evidence, deletion.

Evidence: D031-E01 Change the workspace policy; D031-E02 Cleanup timing; D031-E03 Downstream indexes and deletion.

Fragen: Q090, Q091, Q092.

### D032 Orbit 2 release notes

Release Notes der früheren Generation mit denselben Begriffen wie aktuelle Doku lesen.

Version 2.4; Sprache en; Format md; Zugriff PUBLIC.

Features: version_conflict, exact_identifier.

Evidence: D032-E01 Orbit 2.4 release; D032-E02 Capacity and notification changes; D032-E03 Connector compatibility.

Fragen: Q032, Q033, Q035.

### D033 Orbit 3 release notes

Aktuelle Release Notes als weitere autoritative Quelle für Version und Events nutzen.

Version 3.0; Sprache en; Format md; Zugriff PUBLIC.

Features: version_conflict, exact_identifier.

Evidence: D033-E01 Orbit 3.0 release; D033-E02 New defaults; D033-E03 Integration transition.

Fragen: Q034, Q036.

### D034 Deprecated integrations

Archivierte, korrekte Connectorwerte von falschen aktuellen Behauptungen unterscheiden.

Version 2.4; Sprache en; Format md; Zugriff PUBLIC.

Features: conflict_resolution, version_conflict, exact_identifier.

Evidence: D034-E01 Connector transition notice; D034-E02 Archived worker note; D034-E03 Review before replacement.

Fragen: Q033, Q034.

### D035 Doppelte Zustellung im Kundenfall

Flüchtige Deduplizierung und dauerhafte Folgeaktion in einem ausführlichen Supportfall diagnostizieren.

Version 3.0; Sprache de; Format md; Zugriff CUSTOMER. Organisation org-amber

Features: paraphrase, acl, multi_evidence.

Evidence: D035-E01 Fall und Beobachtung; D035-E02 Korrektur im Empfänger; D035-E03 Abgrenzung des Falls; D035-E04 Warum ein kurzer Neustarttest nicht genügte; D035-E05 Nachweis der Korrektur.

Fragen: Q109.

### D036 Cobalt Workspace Supportfall

Cobalt-Exportscope und Kunden-ACL statt einer vermuteten Queue-Störung erklären.

Version 3.0; Sprache de; Format md; Zugriff CUSTOMER. Organisation org-cobalt

Features: multi_evidence, acl, exact_identifier.

Evidence: D036-E01 Fehler nach Exportumstellung; D036-E02 Berechtigung korrigieren; D036-E03 Was nicht geöffnet wurde.

Fragen: Q096, Q097.

### D037 Cobalt workspace case

Stale Kundenanlage mit falscher Tokenlaufzeit und zweiter Injection gegen den Servicevertrag prüfen.

Version 3.0; Sprache en; Format md; Zugriff CUSTOMER. Organisation org-cobalt

Features: acl, prompt_injection, version_conflict, conflict_resolution, exact_identifier.

Evidence: D037-E01 A note attached to an old deployment; D037-E02 Observed expiry; D037-E03 Attached operator instruction.

Fragen: Q098, Q119.

### D038 Queue lease engineering

Workerlease, Heartbeat und Recovery-Limit im Engineering-Kontext auseinanderhalten.

Version 3.0; Sprache en; Format md; Zugriff INTERNAL. Team operations

Features: acl, chunk_boundary, multi_evidence.

Evidence: D038-E01 Lease ownership; D038-E02 Recovery gate; D038-E03 Fairness after a restart; D038-E04 Ownership race during recovery; D038-E05 Recovery outcome ledger.

Fragen: Q100, Q101, Q107.

### D039 Verfahren zum Schlüsselwiderruf

Zeitliche Korrektur einer Widerrufsnotiz anhand einer Incidentchronologie nachvollziehen.

Version 3.0; Sprache de; Format md; Zugriff INTERNAL. Team operations

Features: conflict_resolution, acl, multi_evidence.

Evidence: D039-E01 Zeitlicher Ablauf; D039-E02 Verbindliche Frist und Kontrolle.

Fragen: Q103.

### D040 Key revocation procedure

Security-Runbook und zweiten Übungsmarker mit mehreren notwendigen Belegen absichern.

Version 3.0; Sprache en; Format md; Zugriff RESTRICTED. Team security

Features: acl, multi_evidence.

Evidence: D040-E01 Revoke an integration key; D040-E02 Propagation and verification; D040-E03 Security exercise correlation.

Fragen: Q104, Q105.

### D041 Export manifest sample

CSV-Attributtabelle mit Zeilenzahl, Format und halboffenem Intervall lesen.

Version 3.0; Sprache en; Format csv; Zugriff PUBLIC.

Features: table_lookup.

Evidence: D041-E01 Completed export manifest.

Fragen: Q094, Q095.

### D042 Device naming FAQ

Gerätenamen mit mehreren semantischen Alltagsformulierungen abfragen.

Version 3.0; Sprache en; Format html; Zugriff PUBLIC.

Features: paraphrase.

Evidence: D042-E01 Why did a rename not change the identifier?; D042-E02 Can I reuse a local inventory name?; D042-E03 Should a missing device be registered again?.

Fragen: Q038, Q039, Q040, Q041.

### D043 Webhook Signaturprüfung

Englische Signaturfrage mit deutscher technischer Quelle beantworten.

Version 3.0; Sprache de; Format md; Zugriff PUBLIC.

Features: multilingual, chunk_boundary.

Evidence: D043-E01 Signatur am Eingang prüfen; D043-E02 Schlüsselwechsel unterscheiden; D043-E03 Fehlerprotokoll ohne Geheimnisse.

Fragen: Q070, Q071, Q072, Q074.

### D044 Doppelte Meldungen

Echte Wiederholung von ähnlichen, aber eigenständigen Ereignissen unterscheiden.

Version 3.0; Sprache de; Format md; Zugriff CUSTOMER. Organisation org-amber

Features: paraphrase, acl, multi_evidence.

Evidence: D044-E01 Zwei fachlich gleiche Meldungen; D044-E02 Korrektur der Zuordnung; D044-E03 Fallabschluss.

Fragen: Kontext-/Distraktorquelle, keine eigene positive Hauptfrage.

### D045 Aufbewahrung erklärt

Deutsche Retention-FAQ von Linkdauer, Audit und Wiederherstellung abgrenzen.

Version 3.0; Sprache de; Format md; Zugriff PUBLIC.

Features: multilingual, multi_evidence.

Evidence: D045-E01 Welche Zeit zählt?; D045-E02 Mehr Tage nach einer Änderung; D045-E03 Warum stehen im Audit andere Fristen?.

Fragen: Q090, Q091, Q093.

### D046 Betriebsübergabe

Deutschsprachige interne DOCX-Übergabe mit verschiedenen Zeiteinheiten und Parent-Kontext lesen.

Version 3.0; Sprache de; Format docx; Zugriff INTERNAL. Team operations

Features: acl, chunk_boundary, multi_evidence.

Evidence: D046-E01 Übergabe der Exportwarteschlange; D046-E02 Zeitwerte gemeinsam lesen; D046-E03 Freigabe nach Wiederaufnahme; D046-E04 Unvollständige Übergabe erkennen; D046-E05 Abweichungen nach einer Wiederaufnahme.

Fragen: Q102, Q106, Q120.

### D047 Wiederanlauf nach Störung

Eine sinkende Queue-Gesamtsumme nicht mit vollständiger Wiederherstellung gleichsetzen.

Version 3.0; Sprache de; Format md; Zugriff INTERNAL. Team operations

Features: multi_evidence, acl.

Evidence: D047-E01 Beobachtung während des Neustarts; D047-E02 Abgleich der Wiederaufnahme; D047-E03 Folgerung für die Übergabe.

Fragen: Q108.

### D048 Versionswechsel Checkliste

Deutsche PDF-Checkliste zu API-, Token-, Event- und Budgetwechsel verbinden.

Version 3.0; Sprache de; Format pdf; Zugriff PUBLIC.

Features: version_conflict, multi_evidence, chunk_boundary.

Evidence: D048-E01 Vor dem Wechsel; D048-E02 Vertragswerte prüfen; D048-E03 Nach dem Wechsel.

Fragen: Q037.

## Messdisziplin und redaktionelle Fortsetzung

questions.jsonl vereinigt Smoke und Test. Die Smoke-Fragen Q001 bis Q025 sind bekanntes Entwicklungsmaterial; Q026 bis Q120 sind der systematischere Test. Themen und Faktenfamilien überschneiden sich. Ein öffentliches Testset ist nicht dauerhaft unberührt, sobald daran optimiert wird. Für spätere belastbare Aussagen weitere relevante Treffer poolen und gegebenenfalls einen neuen Holdout anlegen.

Bei Multi-Evidence nicht nur den ersten Rang bewerten. Bei Tabellen die Spaltensemantik prüfen, bei Zitaten die konkrete Claim-Unterstützung. Nicht gelistete Treffer können trotzdem relevant sein; das Set ist nicht exhaustiv. Für vollautomatische Citation-Metriken fehlt eine vollständige atomare Claim-Annotation.

Es wurden keine Chunking-, Embedding- oder Retrieval-Experimente ausgeführt. Das Dokumentieren einer Schwierigkeit ist keine Messergebnisaussage. Neue Themen oder Zahlen zuerst in facts.yaml definieren, dann Texte und Frageplan anpassen. No-Answer-Fälle können durch eine solche Erweiterung ungültig werden und müssen erneut geprüft werden.
