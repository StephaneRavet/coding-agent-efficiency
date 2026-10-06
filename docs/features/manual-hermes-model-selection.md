# Feature — Manual Hermes model selection

Last verified: 2026-10-06

Status: partial
Source of truth: yes

## Résumé

- Provide a repository launcher for a manual coding-agent smoke test.
- Open Hermes' interactive provider/model selector, then launch its chat from the repository root.
- Keep model selection fixed for the session; no routing, escalation, benchmark automation, or DSH.

## User flow

1. Install Hermes Agent and make `hermes` available on `PATH`.
2. Run `./scripts/hermes-manual.sh` from any directory.
3. In `hermes model`, choose OpenRouter, authenticate through Hermes, and choose an available model with tool use.
4. Hermes starts an interactive session with the repository root as its working directory.
5. Give it a small, reviewable coding task and inspect its changes manually.

## Règles métier

| Règle | Markdown | Code centralisé | Consommation |
| --- | --- | --- | --- |
| This launcher always starts Hermes with an interactively selected provider/model; it does not choose or switch models itself. | This document | — | `scripts/hermes-manual.sh` |

## Décisions

| Date | Décision | Raison | Impact |
| --- | --- | --- | --- |
| 2026-10-06 | Use Hermes' existing `hermes model` selector, then launch `hermes` from the repository root. | Reuse the supported provider/model picker and keep the MVP fixed-model. | No project dependency or local model catalog is needed. |
| 2026-10-06 | Do not install Hermes or collect/store an API key in this repository. | Global project instructions reserve dependency installation to the user; credentials belong to Hermes' setup. | Hermes must already be installed for the launcher to work. |

## Plan

- [x] P001 — Add a launcher that selects a provider/model and starts Hermes in the repository.
- [x] P002 — Document the manual smoke-test flow and benchmark separation.
- [ ] P003 — Run the flow after Hermes is installed and confirm a model can execute a harmless repository task.

## TODO

- [ ] F001 — Install Hermes Agent and choose an OpenRouter model with tool use — status: user action — files: `scripts/hermes-manual.sh`
- [ ] F002 — Perform a manual smoke test and record the observed Hermes/model versions — status: blocked on F001 — files: `docs/MVP_PROTOCOL.md`

## Journal impl Codex

- status: partial
- code map: `scripts/hermes-manual.sh:1` launcher; `README.md` manual start instructions; `docs/MVP_PROTOCOL.md` smoke-test separation.
- checks: `bash -n scripts/hermes-manual.sh` passed; Hermes CLI absent from PATH at implementation time.
- blocage: the launcher could not be exercised because Hermes is not installed. Installation is reserved to the user by project instructions.

## Files actuels

| Zone | Files |
| --- | --- |
| CLI | `scripts/hermes-manual.sh` |
| Docs | `README.md`, `docs/MVP_PROTOCOL.md`, `docs/features/INDEX.md`, this document |
| Tests | No test added; manual smoke test pending Hermes installation. |

## Files à créer/modifier

- `scripts/hermes-manual.sh`
- `README.md`
- `docs/MVP_PROTOCOL.md`
- `docs/features/INDEX.md`
- `docs/features/manual-hermes-model-selection.md`

## Tests / QA

- [ ] Launcher exits with an actionable message if Hermes is unavailable.
- [ ] Hermes selector opens and accepts OpenRouter credentials/model.
- [ ] Hermes starts in the repository root and can complete a harmless task using its tools.
- [ ] Manual smoke-test runs remain separate from benchmark measurements.

## Keep updated when

- Hermes CLI command names or selector flow change.
- The launcher gains options, model defaults, or benchmark integration.
- The MVP begins recording manual runs as measured experiments.

## Historique

| Date | Commit | Type | Notes |
| --- | --- | --- | --- |
