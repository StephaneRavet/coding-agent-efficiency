# MVP Benchmark Protocol

## Objective

Compare OpenAI Codex with Hermes running a small, fixed set of open-source/open-weight models through OpenRouter. Measure task quality and end-to-end task economics. This is a fixed-model comparison; no dynamic routing, escalation, or DSH.

## Manual smoke test

Use [`scripts/hermes-manual.sh`](../scripts/hermes-manual.sh) to open Hermes' provider/model selector and start a session from the repository root. Select OpenRouter and a model with tool-use support. This is an exploratory setup check only: exclude its task, tokens, cost, and duration from benchmark results. See the [feature record](features/manual-hermes-model-selection.md).

## Experimental unit

One run is one system completing one task from a clean, versioned repository state through its declared verifier.

- Systems: one frozen Codex configuration; Hermes with each frozen OpenRouter model configuration.
- Panel: 6 tasks, 2 per category: bug fix, bounded feature, maintenance/refactor.
- Repetitions: 3 independent runs per task and system; report each run and aggregate.
- Attempts: one agent trajectory per run. Do not restart or repair a failed run; internal tool/model turns within the harness are part of that trajectory and must be recorded when observable.
- Pairing: same task text, initial commit, available repository context, tool permissions, verifier, timeout, and resource constraints. Record unavoidable Codex/Hermes differences.
- Order: randomize run order within each task; record the seed. Use a fresh worktree or reset snapshot for every run.

## Task eligibility and acceptance

Select tasks that:

- have a deterministic acceptance test or an explicit, prewritten rubric;
- complete within the declared time and spend limits on a human dry run;
- have a redistributable/public source or explicit permission for benchmark use;
- represent one of the three declared categories without depending on external credentials or mutable services.

For each task, record an immutable task ID, source/repository and commit, category, exact prompt, initial state, allowed tools, acceptance criteria, verifier command/version, expected result, and any exclusions. Keep hidden tests and rubric details unavailable to the agents where feasible.

A run succeeds only if all required deterministic checks pass. If a task also requires a rubric, score it blind to system/model identity using the rubric fixed before runs. Report deterministic pass rate and rubric score separately; do not convert an unverified agent self-report into success.

## Freeze sheet (complete immediately before the first run)

| Field | Frozen value |
| --- | --- |
| Protocol revision and freeze timestamp (UTC) | TBD |
| Task IDs, source commits, prompts, verifiers, rubric | TBD |
| Hermes release/commit and configuration hash | TBD |
| OpenRouter model IDs, provider policy, and request settings | TBD |
| Codex product/model identifier and settings exposed to the user | TBD |
| System/developer prompts and tool versions, where inspectable | TBD |
| Price snapshot URL/date and currency | TBD |
| Per-run timeout | 60 minutes |
| Per-run spend cap | TBD before execution |
| Max agent trajectories per task/system | 1 per repetition; no manual reruns |
| Repetitions | 3 |
| Cache policy | Record actual provider telemetry; do not force or assume cache hits |
| Run order seed | TBD |
| Concurrency | Sequential; no overlapping runs |
| Human intervention | None after a run starts; record any interrupted run as invalid with reason |

Do not begin evaluation until every `TBD` field above has a recorded value or an explicit `unavailable` marker. If the spend cap cannot be set, stop before execution and choose one. The freeze sheet and task artifacts are versioned with the benchmark results.

## Measurements

Record per run, where available:

- task/system/model/provider IDs, repetition, order, start/end times, and elapsed wall time;
- deterministic verifier outcome and rubric score, if used;
- total provider/API charge and currency; separate subscription charges from marginal API spend and never invent an allocated Codex subscription cost;
- input, output, reasoning, cached-input tokens and cache charges as distinct fields; use `unavailable` when telemetry is not exposed;
- tool/model call counts, retries within the trajectory, timeouts, errors, and human interventions;
- exact configuration/version references and privacy-reviewed artifacts needed to reproduce the run.

Primary summaries:

- quality threshold and task success rate;
- total measured cost across all runs, including failed runs;
- cost per successful task = total measured cost / successful task count;
- elapsed-time distribution;
- token and cache usage when exposed.

If a system has zero successful tasks, report cost per success as undefined. Compare cost efficiency only when the same predeclared quality threshold is met. Report Codex subscription treatment separately from marginal OpenRouter charges so the comparison does not imply false precision.

## Run procedure

1. Complete the freeze sheet and verify the six task snapshots and verifier commands.
2. Confirm every system can access the same task materials and permitted tools; record differences.
3. Execute each frozen run from a clean task snapshot in the seeded order. Do not alter prompts, settings, models, tools, or limits mid-panel.
4. Run the verifier without editing the agent output. Store exit status and structured results.
5. Mark interrupted or invalid runs with reason; do not silently replace them. A protocol change requires a new revision and a complete rerun of the affected paired panel.
6. Publish sanitized per-run data and aggregate results with missing telemetry and exclusions visible.

## Result record

| Task | System/model | Trial | Verifier | Rubric | Cost | Elapsed | Input/output/cache tokens | Cache charge | Calls/retries | Invalid reason |
| --- | --- | ---: | --- | ---: | ---: | ---: | --- | ---: | --- | --- |

Use one machine-readable row per run in addition to this human-readable summary. Store credentials, private prompts, and non-public source code outside published artifacts.
