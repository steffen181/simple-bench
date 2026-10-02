# Luna/Sonnet Campaign Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task in the current session. Status update: implementation and offline verification completed; approved live campaign completed: 434 calls, audit PASS, $0.5169024, 86 offline tests passed. The sections below preserve the original implementation checklist. Steps use checkbox syntax. No automatic commits/pushes.

**Goal:** Ein reproduzierbarer Vergleich GPT-6 Luna / Claude Sonnet 5 ohne Reasoning, mit adaptivem Smoke, frischer Hauptmessung, BBH-Referenz und lokalem Dashboard für insgesamt höchstens 4,00 USD.

**Architecture:** Bestehende Transport-, Budget- und Replay-Funktionen wiederverwenden. Erweiterte Leiter als versioniertes v2-Modul; eigene Kampagnensteuerung friert Auswahl/Seals ein. Ein statischer Dashboard-Exporter liest nur geprüfte Auswertungsdaten.

**Tech Stack:** Python >=3.10, bestehende pytest/PyYAML/Jinja2-Infrastruktur, optional python-igraph/Bliss für große Strukturgraphen; HTML/CSS/JavaScript/SVG ohne externe Laufzeitdienste.

**Spec:** [Design und Messprotokoll](../specs/2026-09-29-luna-sonnet-campaign-design.md). [Geprüfte öffentliche Routen](2026-09-29-luna-sonnet-capabilities.json).

## Global Constraints

- Nutzer bestätigt: Sonnet **5**, nicht 5.5; beide Modelle Reasoning aus.
- Kosten einschließlich Gate, Fehlern und Smoke <=4,00 USD; 3,75 USD Arbeitsbudget und 0,25 USD unverplante Reserve.
- Stufen N=3,5,7,10,16,24,32,48,64; zunächst K=32/R=16, Stress K=64/128 separat; gleiche Fragen für beide Modelle.
- `max_tokens=32`; keine gemeinsamen Temperature-/top_p-/API-Seed-Zusagen, da Routen sie nicht gemeinsam anbieten.
- Keine native `acc_norm` erfinden: BBH in dieser Kampagne als separate generative Teilstichprobe.
- Neue Laufordner, keine Änderungen alter Befunde. Schlüssel nie speichern/anzeigen; nicht mit Shell-Code aus der env-Datei ausführen.
- Keine Python-Paket-/CLI-Umbenennung nebenbei; bestehenden Namen tracking-bench beibehalten.

## Review Focus

1. Parameter im globalen Modellkatalog, aber nicht auf der konkreten Route: vor jedem Freeze mit Route prüfen (Task 2).
2. Große N mit symmetrischen/fast leeren Strukturen: kein faktorieller Ausfall oder falscher Frischebeleg (Task 1).
3. Unsicherer Timeout bzw. fehlende Abrechnung: keine Freigabe reservierten Geldes und kein doppelter Versuch (Task 2/3).
4. Adaptives Screening erreicht keine Grenze oder Budgetende mitten in einer Zelle: Unvollständigkeit sichtbar, keine extrapolierte Grenze (Task 3/4).
5. Modell-/Fehlertexte enthalten HTML oder private Metadaten: Dashboard-Ausgabe bleibt escaped und frei von Secret-/Requestdaten (Task 5).

## Task 1: Skalierbare, versionierte Aufgabenleiter

**Files:** Create `src/tracking_bench/structure_large.py`, `src/tracking_bench/ladder_v2.py`, `tests/test_ladder_v2.py`; modify `src/tracking_bench/cli.py`, `pyproject.toml`, `docs/DIFFICULTY.md`.

**Interfaces:** `structure_large.solve(episode) -> int`, `structure_large.canonical_id(episode) -> str`; `ladder_v2.generate(entities, steps, relevant_updates, tasks, per_cell, seed, blocked) -> corpus`. V2-CLI-Auswahl explizit; v1-Defaults unverändert.

- [x] RED: N=10/32/64, unabhängiger Solver/Text-Replay, exakte relevante Updates, Umbenennungsinvarianz, Swap-Symmetrie, gerichtete Give-Rollen, Rotationsgruppierung, Seed-Determinismus und Split-Ausschluss.
- [x] RED: alte/neue Canonical-Klassen auf kleinen N müssen dieselbe Gleichheitsrelation liefern; Alt-ID-Ausschlüsse werden erkannt; viele unbeteiligte Knoten dürfen keine falsche Gleichheit erzeugen.
- [x] Implementieren: farbige Graphkodierung und optionalen exakten Kanonisierer prüfen/pinnen; zeitlich markierte Ereignisse, Rollen und Query; v2 mit 64 festen eindeutigen Namen/Objektwörtern. Kein bloßer Text-Hash als Strukturersatz.
- [x] `pytest -q tests/test_ladder_v2.py tests/test_benchmark_structure.py tests/test_public_package.py`; Ressourcenprobe N=64/K=128 ohne Inferenz. PASS und dokumentierte praktische Laufzeitgrenze vor Smoke.

## Task 2: Routen-, Reasoning- und Kostenvertrag

**Files:** Create `src/tracking_bench/campaign_contract.py`, `tests/test_campaign_contract.py`; modify `openrouter.py`, `run.py`, `budget.py` im selben Package, `docs/CLOSED_MODELS.md`.

**Interfaces:** `resolve_route(model_id, catalog, endpoints) -> RouteContract`; `quote_request(request, contract) -> ReservationQuote` mit belegtem Inputbound, maximaler Abrechnung und Preis-Snapshot; `check_response(raw, contract) -> AuditResult`. `load_key(path) -> str` liest ausschließlich die Schlüsselzuweisung und gibt Fehler ohne Dateiinhalt aus.

- [x] RED: Sonnet5.5 mandatory wird bei off abgewiesen; fehlende Reasoning-Zähler sind nicht null; Reasoning-Text oder >0 Tokens stoppt; Katalog/Route-Konflikte und nicht verfügbare Parameter werden nicht ignoriert.
- [x] RED: off-Anfragen enthalten keine Goldlabels, kein Logging des Keys; Datenzeilen mit Shell-Ausdrücken werden nicht ausgeführt; Alias-/Provider-Mismatch stoppt.
- [x] RED: Decimal-Kosten inkl. Cache-/Tarifstufen, 4-Dollar-Gesamtcap, Scope-Grenzen, unsichere Calls/Timeouts, fehlende Kosten, Providerüberschreitung und Reservation vor Request. Modellkontext darf nicht künstlich als Kostenoptimierung verkleinert werden.
- [x] Implementieren: konservativen dokumentierten Input-/Chat-Tokenansatz für beide Plain-Text-Routen prüfen. Nach fehlender exakter Zählmöglichkeit hat der Nutzer ausdrücklich die UTF8-/4096-Envelope-Annahme freigegeben; keine Providerzertifizierung behaupten. Kein auf beobachteten Smoke-Durchschnitten beruhender Bound.
- [x] ReservationQuote durch den eigenen Kampagnenrunner mit Reserve/Receipt/Audit durchreichen; bestehende ältere Run-Verträge unverändert erhalten (dokumentierte Implementierungsentscheidung). Antworten müssen innerhalb des Bounds liegen; Überschreitung stoppt.
- [x] `pytest -q tests/test_campaign_contract.py tests/test_benchmark_transport.py`; Fixture-Läufe müssen Kostenstopps reproduzieren. Noch keine Live-Probes vor den übrigen Offline-Prüfungen.

## Task 3: Kampagnensteuerung und unabhängige Bestätigung

**Files:** Create `src/tracking_bench/frontier_campaign.py`, `tests/test_frontier_campaign.py`, `examples/frontier-config.json`; modify `src/tracking_bench/cli.py`.

**Interfaces:** `freeze(config, catalog, endpoints, out) -> manifest`; `select_frontier(smoke_results, frozen_rule) -> selected_cells`; `execute_phase(campaign, phase, key_file) -> summary`; `audit_campaign(campaign) -> audit`. CLI `tracking-bench campaign freeze|gate|smoke|confirm|audit` als explizite Schritte. Netzwerkzugriffe nur bei bezahlten Ausführungsschritten.

- [x] RED: Auswahlregel <=75% und >=20pp Verlust, zwei benachbarte Stufen, gemeinsamer Bereich für beide Modelle, fehlende Basis/kein Einbruch/Budgetende; Auswahl ausschließlich aus Smoke-Belegen.
- [x] RED: Rotationen niemals getrennte Gruppen; frische Seeds, keine Smoke-/Gate-Gruppen in Bestätigung; eingefrorene Parameter/Quellhashes dürfen sich zwischen Freeze und Ausführung nicht ändern.
- [x] RED: Zell-/Modellreihenfolge ausgeglichen; vor einer Zelle Geld für beide Modelle vorsehen; bei Teilabbruch Abdeckung und ungepaarte Restfälle sichtbar. Unbekannte Calls nicht erneut senden.
- [x] Implementieren: Protokollstatus FROZEN → GATE → SMOKE → CONFIRMATION_FROZEN → MEASURED/STOPPED → AUDITED, Zustandswechsel und Belege append-only. Weniger Stichproben nur vorab nach Kostenregel; keine Ergebnisanpassung der Hauptmessung.
- [x] `pytest -q tests/test_frontier_campaign.py`; vollständige Offline-Fixture-Kampagne inklusive Abbruch/Replay.

## Task 4: BBH-Referenz und statistische Auswertung

**Files:** Create `src/tracking_bench/frontier_analysis.py`, `tests/test_frontier_analysis.py`; reuse `bbh.py`, `reference.py`, `bbh_fresh.py`, `report.py`.

**Interfaces:** `make_bbh_reference(sources, seed, per_n, fresh_per_n) -> corpus`; `analyze_campaign(campaign) -> PublicResults` mit getrennten Abschnitten für smoke, confirmation, bbh und diagnostic.

- [x] RED: Originalfragen hashgebunden; identische ausgewählte Originale/Prompts/Modelle; 30 bzw. 15 pro N ausschließlich durch vorab gesetzte Kostenregel; frische BBH-Fälle separat; native-Likelihood-Feld bleibt unavailable.
- [x] RED: Accuracy-Denominator/Abdeckung, invalide Antworten vs. API-Ausfälle, Seed-/Task-Strata, gruppiertes Bootstrap mit beiden Rotationen/Modellen, keine Zusammenlegung von N/K/R oder Smoke/Confirmation.
- [x] Implementieren: gepaarte Genauigkeiten und punktweise 95%-Intervalle mit 2.000 Replikaten, Chance 1/N, Optionsstabilität, Kosten/Latenz/Token und Reasoning-Audit; fehlende Messungen als null/Status.
- [x] `pytest -q tests/test_frontier_analysis.py tests/test_bbh_likelihood.py tests/test_bbh_likelihood_confirmation.py`; Auswertung aus gespeicherten Fixtures reproduzierbar und ohne neue API-Aufrufe.

## Task 5: Vergleichs-Dashboard im Repository

**Files:** Create `src/tracking_bench/dashboard.py`, `src/tracking_bench/templates/dashboard.html`, `tests/test_dashboard.py`; modify `pyproject.toml` package-data, `cli.py`, `README.md`.

**Interfaces:** `dashboard.export(results: PublicResults, out: Path) -> manifest`; CLI `tracking-bench dashboard --campaign ... --out dashboard/luna-sonnet-20260929`.

- [x] RED: keine Secrets, Kontodaten, lokalen Schlüsselpfade oder Request-IDs; JS-/HTML-Injection escaped; ungemessene Felder nicht als 0 dargestellt; Protokolle und Reasoningstatus sichtbar.
- [x] Implementieren: eigenständiges HTML mit eingebetteten bereinigten Daten, interaktive SVG-Kurven/Heatmap, Filter, Tabellen und Downloads. Paketiert ohne CDN; statische Datei lässt sich direkt öffnen.
- [x] `pytest -q tests/test_dashboard.py`; Browserprüfung mit guten/schlechten/unvollständigen Fixture-Daten: Filter, Kurven, CSV, BBH-Kennzeichnung und Budgetanzeige. Noch keine erfundenen Live-Werte.

## Task 6: Technische Abnahme und tatsächliche Kampagne

**Files:** new private `runs/luna-sonnet-20260929-<unique>/`; public `dashboard/luna-sonnet-20260929/` with index.html, results.json, results.csv, protocol.json, REPORT.md and SHA256SUMS; refresh source inventory only after final changes.

- [x] Vollständige Offline-Regression `pytest -q`, Wheel-/Source-Build, installierter CLI-Smoke, Herkunfts-/Prompt-/Parseraudit. Keine kostenpflichtigen Tests in CI.
- [x] Direkt vor Ausführung öffentliche Modell-/Route-Metadaten erneut prüfen. Externen API-Key sicher laden; Auth/Guthaben nur lesend prüfen. Effektiver Cap nie größer als 4 USD oder verfügbares Guthaben.
- [x] Gesamtkampagne/Scopes einfrieren, Gate bis 0,15 USD; nur bei belegtem Reasoning-off, validen Kosten und Identitäten weiter.
- [x] Smoke bis 0,60 USD, BBH-Block bis 0,60 USD; Regeln aus Spec anwenden. Hauptmatrix kostenbasiert fixieren und versiegeln; Fragen erst danach frisch erzeugen. Unverplante 0,25 USD nicht als zusätzliche Versuche ausgeben.
- [x] Hauptmessung bis 2,40 USD mit mehreren Seeds und gleichen Aufgaben; alle Antworten und Fehler dauerhaft erfassen. Bei Unterdeckung offen abbrechen, keine stillen Substitutionen.
- [x] Offline-Audit/Report/Dashboard aus Belegen bauen; Kostenbilanz inklusive Fehler/Reservierungen, Commands, Hashes, Grenzen, Messbereich und BBH-Protokoll liefern. Keine Erfolgsbehauptung „Einbruch gefunden“, falls nicht beobachtet.

## Ursprünglich geplante Lieferung und Ausführung

Empfohlen: Umsetzung durch den bestehenden Agenten in dieser Sitzung, Aufgaben nacheinander, mit abgeschlossenen Offline-Prüfungen vor bezahlten Calls. Der Nutzer hat zunächst diesen Plan angefordert; die Bestätigung der Modelländerung ist keine Aufforderung, den Planungsstopp zu überspringen. Nächster Schritt nach Planfreigabe ist Task 1, nicht der kostenpflichtige Smoke.

## Selbstprüfung

Abgedeckt: Nutzer-Modellkorrektur, Reasoning-off-Nachweis, Gesamtbudget, geheime Schlüsseldatei, skalierbare Entitäten, separat kontrollierte Ereignislast, frühes Screening, unabhängige Messung, BBH-Protokollgrenzen, Dashboard im Repo und Test-/Hashbelege. Praktische Abbruchbedingungen sind explizit: kein Reasoning-Nachweis, kein belastbarer Kostenbound, unzureichendes Stichprobenbudget oder kein beobachteter Einbruch. In diesem Planungsschritt wurden nur die vorhandenen Quellen und öffentliche GET-Endpunkte gelesen sowie diese Planungsdateien geschrieben.


## Ausführungsstand und genehmigte Präzisierungen

2026-09-29: Tasks 1–5 umgesetzt; 83 Offline-Tests bestanden, Wheel/Source gebaut, Wheel in sauberem venv installiert, N64/K128-CLI und Offline-Demo erfolgreich. Browser-Fixture einschließlich Filtern und Fehlerkonsole geprüft. Unabhängige Review fand drei wichtige Fehler; Regressionen reproduzierten diese vor der Korrektur.

Abweichungen vom ursprünglichen Implementierungsweg: eigener Kampagnenrunner nutzt vorhandenen Budget-/OpenRouter-Code, ohne ältere Run-Receipts umzubauen. Nutzer hat ausdrücklich den konservativen UTF8-Byte-plus-4096-Envelope-Kostenansatz freigegeben, nachdem exakte Tokenzählung nicht verfügbar war. Er ist kein providerzertifizierter Bound. Budgetprüfung erfolgt je Modellpaar; fixierte Populationen können mit sichtbarer Unterdeckung stoppen. BBH vorab auf 15 Originale je N und ohne optionale frische Ergänzung gesetzt; Hauptmessung mit zwei Gruppen je Seed/Aufgabe. Kein zusätzlicher Worktree und keine automatischen Commits.

Verbindlicher aktueller Betrieb: [FRONTIER_CAMPAIGN.md](../../FRONTIER_CAMPAIGN.md). Laufdaten bleiben lokal unter `runs/luna-sonnet-20260929-live/`; abgeschlossene öffentliche Ergebnisse werden im Dashboard dokumentiert.


## Abschluss

Alle vier Livephasen abgeschlossen: Gate 8, Smoke 144, BBH 90, Bestaetigung 192 Antworten. Audit PASS, Kosten 0.5169024 USD, keine offenen Reservierungen. Kein gueltiger Screening-Grenzbeleg; Sonnet wird stark durch Antwortformat/32-Token-Limit begrenzt. Ergebnisse: [Befundbericht](../../RESULTS_LUNA_SONNET_20260929.md), [Dashboard](../../../dashboard/luna-sonnet-20260929/index.html). Finale Offline-Regression: 86 passed. Reportingkorrekturen nach Messabschluss aenderten keine Anfragen, Antworten oder Trefferzahlen.
