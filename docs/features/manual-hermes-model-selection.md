# Feature — Hermes MVP benchmark runner

Last verified: 2026-10-06

Status: in-progress
Source of truth: yes

## Résumé

- Provide a direct manual Hermes launcher and a reproducible Hermes/OpenRouter benchmark focused on verified task cost.
- Preserve the project's conceptual agentic loop while measuring real harness runs.
- Keep routing, escalation, and DSH outside the initial benchmark.

## User flow

1. Install Hermes Agent and configure the desired provider/model once.
2. Run `./scripts/hermes-manual.sh` from any directory; it starts `hermes` at the repository root with the saved configuration.
3. Use `hermes model` separately only to change the saved default. Benchmark invocations override model/provider explicitly.
4. For benchmark runs, fill the freeze sheet, set the OpenRouter key limit, ensure Docker and the Hermes sandbox image are available, then run `python3 scripts/benchmark.py run-panel`.
5. Inspect per-run artifacts and score quality against the blinded task rubric; review aggregate results with `python3 scripts/benchmark.py report`.

## Règles métier

| Règle | Markdown | Code centralisé | Consommation |
| --- | --- | --- | --- |
| The manual launcher starts Hermes using the saved configuration; it does not change provider or model. Benchmark runs use only frozen model IDs. | This document | — | `scripts/hermes-manual.sh`, `scripts/benchmark.py` |

## Décisions

| Date | Décision | Raison | Impact |
| --- | --- | --- | --- |
| 2026-10-06 | Launch `hermes` directly for the manual smoke test; run `hermes model` only when deliberately changing the saved default. | Avoid reopening the selector on every launch. The benchmark passes frozen model IDs explicitly. | Manual runs use saved config; benchmark runs remain fixed-model. |
| 2026-10-06 | Do not install Hermes or collect/store an API key in this repository. | Global project instructions reserve dependency installation to the user; credentials belong to Hermes' setup. | Hermes must already be installed for the launcher to work. |

## Plan

- [x] P001 — Add a launcher that starts Hermes with saved provider/model configuration.
- [x] P002 — Document the manual smoke-test flow and benchmark separation.
- [x] P003 — Add a versioned six-task fixture panel with deterministic acceptance checks.
- [x] P004 — Add the fixed-model runner, isolation boundaries, resumable matrix, usage capture, blind scoring, and report.
- [x] P005 — Document setup, freeze requirements, reporting, and safety limits.
- [ ] P006 — Complete local Docker preflight, validate reference solutions in the frozen image, and run a harmless manual Hermes smoke task. Blocked on local Docker and a user-configured OpenRouter key spend limit.

## TODO

- [x] F001 — Install Hermes Agent and expose its CLI on `PATH` — status: complete at `90194c64` — files: `scripts/hermes-manual.sh`
- [ ] F002 — Complete a harmless manual Hermes/OpenRouter coding task — status: models fixed for the benchmark; manual smoke remains pending — files: `scripts/hermes-manual.sh`, `docs/MVP_PROTOCOL.md`
- [x] F003 — Implement benchmark runner and fixed demonstration task panel — status: implementation complete; end-to-end runtime validation awaits local Docker and spend cap — files: `scripts/benchmark.py`, `benchmark/`

## Journal impl

- status: partial
- code map: `scripts/hermes-manual.sh:1` launcher; `README.md` manual start instructions; `docs/MVP_PROTOCOL.md` smoke-test separation.
- checks: `bash -n scripts/hermes-manual.sh` passed; Hermes CLI absent from PATH at implementation time.
- blocage: the launcher could not be exercised because Hermes is not installed. Installation is reserved to the user by project instructions.
- status: Hermes Agent installed at pinned revision `90194c64ff99933ec3b9ecfd9295b06e6c11e038`; the launcher now starts `hermes` directly and preserves the saved provider/model.
- code map: `scripts/hermes-manual.sh:1` starts `hermes` at repository root; `hermes model` is a separate settings action.
- checks: `hermes --version` reported `v0.21.5+7733.g90194c6`; prior `hermes doctor` passed OpenRouter connectivity. No credential value was read or displayed.
- install scope: optional browser and computer-use tools skipped; setup and gateway stages skipped; no key was entered.
- status: in progress; expanded the feature contract to cover the fixed-panel MVP runner. Hermes terminal backend inspection shows local shell is not an acceptable isolation boundary; require its Docker backend for benchmark runs. Docker is unavailable on this host, so end-to-end model trajectories cannot be run here.
- code map: pending runner and task panel implementation.
- checks: Hermes `-z/--oneshot`, `--usage-file`, `--provider`, `--model`, `--in`, and `--run-budget` interfaces inspected locally; installed docs describe JSON usage fields. The benchmark target is Hermes/OpenRouter only; Codex is not part of the MVP.
- blockers: fixed model IDs and spend cap must be frozen before evaluation; OpenRouter fixed-model benchmark has no verified hard per-trajectory USD cap in the current setup. Do not start paid trajectories before freeze.
- status: runner and fixed six-task synthetic panel implemented. Candidate code is imported only by the acceptance verifier inside the frozen, networkless Docker image. The CLI forces Docker Desktop's `desktop-linux` context, strips remote Docker selection variables, and rejects unsafe fixture/workspace links, special files, oversized trees, and external hard links.
- code map: `scripts/benchmark.py` (freeze/preflight, isolation, runner, metrics, blind scores, report); `benchmark/tasks.json`; `benchmark/fixtures/`; `benchmark/verifiers.py`; `benchmark/reference_solutions.json`; `benchmark/freeze.json`; `README.md`; `docs/MVP_PROTOCOL.md`; `docs/BENCHMARK_STRATEGY.md`.
- checks: JSON/Python/shell static checks and panel hash are run at delivery. Docker preflight and reference-solution execution cannot pass on this host because Docker is unavailable; no paid model trajectory was launched.
- blockers: user must install/start local Docker Desktop, pull the Hermes sandbox image and freeze its image ID, configure a dedicated OpenRouter key with a $5.40 total limit, then set the UTC freeze time and key-limit confirmation. Manual model smoke remains outside measured results.

## Files actuels

| Zone | Files |
| --- | --- |
| CLI | `scripts/hermes-manual.sh` |
| Docs | `README.md`, `docs/MVP_PROTOCOL.md`, `docs/features/INDEX.md`, this document |
| Runner | `scripts/benchmark.py` |
| Panel | `benchmark/tasks.json`, `benchmark/fixtures/`, `benchmark/verifiers.py`, `benchmark/reference_solutions.json`, `benchmark/freeze.json` |
| Tests | Task acceptance verifiers in the fixed panel. |

## Files à créer/modifier

- `scripts/hermes-manual.sh`
- `README.md`
- `docs/MVP_PROTOCOL.md`
- `docs/features/INDEX.md`
- `docs/features/manual-hermes-model-selection.md`
- `scripts/benchmark.py`
- `benchmark/`

## Tests / QA

- [ ] Launcher exits with an actionable message if Hermes is unavailable.
- [ ] Each task verifier passes against a known reference solution and fails against its starter state in the frozen Docker image.
- [x] Runner refuses an incomplete freeze sheet and requires the frozen local Hermes image.
- [x] Runner records per-run JSONL, UUID-only rubric sheets, and an aggregate report without saving raw traces or credentials.
- [x] Each Hermes/OpenRouter run starts from a fresh task snapshot and uses the deterministic external verifier contract.
- [x] Quality ratings can be recorded against UUID-only rubric sheets without model labels.
- [x] Manual smoke-test runs remain separate from benchmark measurements.

## Keep updated when

- Hermes CLI command names or selector flow change.
- The launcher gains options, model defaults, or benchmark integration.
- The MVP begins recording manual runs as measured experiments.

## Vérification

- Date: 2026-10-06
- Résultat: implementation and static checks complete; reference fixtures, Docker execution, and manual model smoke still require the local runtime/key setup above.

## Historique

| Date | Commit | Type | Notes |
| --- | --- | --- | --- |

- status: scope pivot applied; runner launches Hermes/OpenRouter only and compares fixed OpenRouter configurations on verified task cost. Codex has been removed from the MVP freeze, CLI, result schema, and operational comparison.
- blocker: local Docker and a spend-capped OpenRouter key are still required before diagnostic model runs.
