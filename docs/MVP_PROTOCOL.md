# MVP Benchmark Protocol

## Objective

Optimize cost per successfully completed coding task using Hermes with a small, fixed set of open-source/open-weight models through OpenRouter. Measure task quality and end-to-end task economics. The initial baseline uses fixed models; no dynamic routing, escalation, or DSH.

## Manual smoke test

Use [`scripts/hermes-manual.sh`](../scripts/hermes-manual.sh) to start Hermes from the repository root with its saved configuration. Run `hermes model` separately only when changing that default. Manual runs are exploratory: exclude their task, tokens, cost, and duration from benchmark results. The automated runner overrides provider/model with the freeze sheet. See the [feature record](features/manual-hermes-model-selection.md).

## Experimental unit

One run is Hermes completing one task from a clean, versioned repository state through its declared verifier.

- Systems: Hermes with each frozen OpenRouter model configuration.
- Panel: 6 tasks, 2 per category: bug fix, bounded feature, maintenance/refactor.
- Current panel: six versioned synthetic fixtures in `benchmark/fixtures/`; they validate runner mechanics and provide a narrow initial coding-quality sample, not a representative estimate of general coding quality.
- Repetitions: up to 3 independent runs per task/model; start with one diagnostic run per model; report each run and aggregate.
- Attempts: one agent trajectory per run. Do not restart or repair a failed run; internal tool/model turns within the harness are part of that trajectory and must be recorded when observable.
- Controls: same task text, initial state, available context, verifier, timeout, and resource limits for every model configuration.
- Order: randomize run order within each task; record the seed. Use a fresh worktree or reset snapshot for every run.
- Execution: `python3 scripts/benchmark.py run-panel` shuffles the full matrix with the frozen seed, then runs sequentially from fresh fixture copies. The runner forces Docker Desktop's local `desktop-linux` context and strips remote Docker selectors. Hermes tools run networkless with only the task workspace mounted; candidate acceptance code runs in a separate read-only, networkless container from the frozen local image. Every Hermes run uses a fresh external temporary task folder.
- Diagnostics: `run` and `run-panel --limit N` are marked diagnostic and excluded from the aggregate report. Do not use those records as full-panel results.

## Task eligibility and acceptance

Select tasks that:

- have a deterministic acceptance test or an explicit, prewritten rubric;
- complete within the declared time and spend limits on a human dry run;
- have a redistributable/public source or explicit permission for benchmark use;
- represent one of the three declared categories without depending on external credentials or mutable services.

For each task, record an immutable task ID, source/repository and commit, category, exact prompt, initial state, allowed tools, acceptance criteria, verifier command/version, expected result, and any exclusions. Keep hidden tests and rubric details unavailable to the agents where feasible.

A run succeeds only if all required deterministic checks pass. If a task also requires a rubric, score it blind to model identity using the rubric fixed before runs. Report deterministic pass rate and rubric score separately; do not convert an unverified agent self-report into success.

## Freeze sheet (complete before the full evaluation)

| Field | Frozen value |
| --- | --- |
| Protocol revision and freeze timestamp (UTC) | TBD |
| Task IDs, fixture revision, prompts, verifiers, rubric | `benchmark/tasks.json`, `benchmark/fixtures/`, `benchmark/verifiers.py` |
| Task panel SHA-256 | `python3 scripts/benchmark.py panel-hash`; copy into freeze before run |
| Hermes release/commit and configuration hash | `v0.21.5+7733.g90194c6`; per-run freeze hash |
| Hermes Docker image | `nousresearch/hermes-sandbox:desktop`; freeze local image ID |
| OpenRouter model IDs, provider policy, and request settings | `deepseek/deepseek-v3.2` and `qwen/qwen3-coder-30b-a3b-instruct`; default Balanced endpoint policy; reasoning low |
| Hermes model configurations | Frozen OpenRouter IDs and Hermes reasoning setting |
| System/developer prompts and tool versions, where inspectable | Record current Hermes release and Docker image ID |
| Price snapshot URL/date and currency | `benchmark/freeze.json`; USD snapshot 2026-10-06, refresh before evaluation |
| Per-run timeout | 60 minutes |
| Per-run spend cap | $0.15 target; recorded and checked against reported Hermes usage, not enforced per run |
| Total OpenRouter budget | $5.40; set the dedicated API key limit to $5.40, with no reset, before execution |
| Max agent trajectories per task/model | 1 per repetition; a single diagnostic run is allowed before the freeze and excluded from full-panel results |
| Repetitions | 3 |
| Cache policy | Record actual provider telemetry; do not force or assume cache hits |
| Run order seed | TBD |
| Concurrency | Sequential; no overlapping runs |
| Human intervention | None after a run starts; record any interrupted run as invalid with reason |

Begin with a single diagnostic task/model run after setup; freeze the full repeated panel before collecting optimization results. Do not begin a full evaluation until every `TBD` field above has a recorded value or an explicit `unavailable` marker. Confirm the OpenRouter key limit before running: Hermes' usage report does not enforce a dollar ceiling during generation. The dedicated key limit bounds aggregate OpenRouter spend; the $0.15 per-run target is checked after each run. `benchmark/freeze.json` is the runner's machine-readable freeze sheet. Its unset UTC freeze time, panel hash, image ID, and key-limit confirmation intentionally block trajectories.

## Measurements

Record per run, where available:

- task/system/model/provider IDs, repetition, order, start/end times, and elapsed wall time;
- deterministic verifier outcome and rubric score, if used;
- total OpenRouter/API charge and currency;
- input, output, reasoning, cached-input tokens and cache charges as distinct fields; use `unavailable` when telemetry is not exposed;
- a blind quality score from 1–5 against the fixed task rubric; deterministic verifier success remains a separate measure;
- tool/model call counts, retries within the trajectory, timeouts, errors, and human interventions;
- exact configuration/version references and privacy-reviewed artifacts needed to reproduce the run.

Primary summaries:

- quality threshold and task success rate;
- total measured cost across all runs, including failed runs;
- cost per successful task = total measured cost / successful task count;
- elapsed-time distribution;
- token and cache usage when exposed.

If a model configuration has zero successful tasks, report cost per success as undefined. Compare configurations only when they meet the same predeclared quality threshold.

## Run procedure

1. Complete the freeze sheet; run `validate-panel` so each starter fails and reference solution passes in the frozen local Docker image; then run `preflight`.
2. Confirm each frozen model uses the same Hermes tools and task materials.
3. Execute each frozen run from a clean task snapshot in the seeded order. Do not alter prompts, settings, models, tools, or limits mid-panel.
4. Run the verifier without editing the agent output. Store exit status and structured results.
5. Mark interrupted or invalid runs with reason; do not silently replace them. A protocol change requires a new revision and a complete rerun of the affected paired panel.
6. Publish sanitized per-run data and aggregate results with missing telemetry and exclusions visible.

## Result record

| Task | OpenRouter model | Trial | Verifier | Rubric | Cost | Elapsed | Input/output/cache tokens | Cache charge | Calls/retries | Invalid reason |
| --- | --- | ---: | --- | ---: | ---: | ---: | --- | ---: | --- | --- |

Use one machine-readable row per run in addition to this human-readable summary. The runner writes `runs/results.jsonl`, blind rubric sheets to `runs/blind/`, and task workspaces to `runs/workspaces/`; all are gitignored. It does not persist raw model output or process logs. Hermes costs come from `--usage-file`; unavailable telemetry stays null. Store credentials, private prompts, and non-public source code outside published artifacts.
