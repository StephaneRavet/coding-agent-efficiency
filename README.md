# Coding Agent Efficiency

**Research and development on reducing cost per successfully completed coding task while preserving a verifiable quality threshold.**

This project optimizes the cost of coding tasks that Hermes completes and an independent verifier validates, using open-source/open-weight models through OpenRouter. **Hermes is the operational harness.** The existing agentic loop remains the conceptual target; the first experiment compares fixed model configurations and does not yet implement dynamic routing or escalation.

## Research premise

The longer-term research hypothesis is that task-level economics improve when a system:

- can swap coding-agent harnesses and routers without changing the evaluation contract;
- chooses from a small set of capability tiers and keeps routing sticky through a task or phase when cache reuse makes that cheaper;
- accounts for prompt-cache state and the cost of switching models;
- uses Jev only for bounded, structured decisions that deterministic rules cannot settle;
- verifies outcomes with task tests and other observable checks;
- escalates after evidence of difficulty, such as repeated failures, rather than prompt appearance alone.

These are hypotheses to measure, not claimed results. Hermes is the selected MVP harness, not a permanent commitment. DSH remains a later R&D option for testing more modular strategies if Hermes becomes limiting.

## Current status

The repository now contains an executable benchmark runner and a fixed six-task synthetic panel. It has no benchmark results yet. Freeze a small set of OpenRouter model IDs, pricing snapshot, timeout, and budget before running Hermes trajectories. Record verifier success and blind rubric quality, total measured cost, cost per successful task, elapsed time, and token/cache telemetry when available. Dynamic routing, escalation, and DSH remain later experiments.

## Démarrer Hermes manuellement

With Hermes Agent installed and configured, run:

```bash
./scripts/hermes-manual.sh
```

The launcher starts `hermes` directly from this repository's root using the saved provider/model. Run `hermes model` separately only when you want to change that saved default. Manual smoke tests are exploratory and are not benchmark results. The automated benchmark passes fixed model IDs to each run. See [the feature record](docs/features/manual-hermes-model-selection.md).

## Lancer le benchmark MVP

The benchmark requires Python 3.10+, Hermes Agent, Docker Desktop using its `desktop-linux` local context, and the local image `nousresearch/hermes-sandbox:desktop`. Hermes tool execution is forced into Docker with network access disabled; the task directory is the only host directory mounted in the sandbox. The acceptance verifier also runs candidate code in a separate networkless, read-only container from that exact frozen local image. The runner strips remote Docker host/context settings before any Docker operation. The current repository host does not have Docker, so it cannot execute model trajectories here.

1. Start local Docker Desktop, pull `nousresearch/hermes-sandbox:desktop`, and record its exact ID with `docker --context desktop-linux image inspect --format '{{.Id}}' nousresearch/hermes-sandbox:desktop`. Put that ID, a fresh UTC timestamp, and the output of `python3 scripts/benchmark.py panel-hash` into [`benchmark/freeze.json`](benchmark/freeze.json); refresh the model price snapshot before the run.
2. The fixed models are `deepseek/deepseek-v3.2` and `qwen/qwen3-coder-30b-a3b-instruct`; Hermes reasoning is fixed to `low` for the baseline; change one setting at a time in later experiments. OpenRouter's default Balanced endpoint routing is retained, so the served provider may vary.
3. Create/use a dedicated OpenRouter key with a total $5.40 spend limit and no reset; include BYOK usage in that limit if applicable. Only then set `openrouter_key_limit_confirmed` to `true`. The runner cannot enforce the $0.15 target on each trajectory; the external key limit is the hard total ceiling. Do not run without it.
4. Run `python3 scripts/benchmark.py validate-panel`. It confirms starter states fail and reference solutions pass inside the frozen, local, networkless Docker verifier. Then run `python3 scripts/benchmark.py preflight`; it refuses an incomplete freeze, mismatched Hermes version/image, non-local Docker context, absent Docker engine, or missing sandbox image.
5. Run `python3 scripts/benchmark.py run-panel`. The seeded order is sequential and the complete panel has 36 trajectories (6 tasks × 2 OpenRouter models × 3 repetitions). Hermes and verifier code execute in networkless Docker containers. Each Hermes run gets a fresh isolated task folder.
6. Inspect `runs/blind/<run-id>.json` and `runs/workspaces/<run-id>/` without consulting `runs/results.jsonl`; record one overall quality score from 1–5 with `python3 scripts/benchmark.py score <run-id> <score>`. Then review `python3 scripts/benchmark.py report`.

The initial fixtures are small synthetic code tasks for validating benchmark mechanics, not a representative estimate of general coding quality. Missing provider telemetry remains unavailable. All generated runs and artifacts are ignored by Git.

## Documents

- [Project goals](docs/PROJECT_GOALS.md): objective, constraints, and acceptance contract.
- [Model routing](docs/MODEL_ROUTING.md): the preserved conceptual agentic loop and later routing experiments.
- [Benchmark strategy](docs/BENCHMARK_STRATEGY.md): Hermes MVP protocol, metrics, controls, and later experiment sequence.
- [MVP protocol](docs/MVP_PROTOCOL.md): task panel design, freeze sheet, run procedure, and result record.
- [Feature index](docs/features/INDEX.md): implementation status for the Hermes benchmark runner.
- [State of the art](docs/STATE_OF_THE_ART.md): source-backed snapshot dated 2026-10-06.

## Guiding metric

```text
cost_per_successful_task
  = total measured cost across all attempts and routing overhead
    / number of tasks passing the declared quality verifier
```

Always report the success rate and quality threshold beside this metric. A lower cost per success is meaningful only when configurations meet the same quality bar on the same tasks.

## Scope and decisions

- MVP: Hermes with OpenRouter models; optimize verified task completion cost.
- Start with a small, fixed task panel and model set; justify additions with measured gains.
- The MVP does not add dynamic routing, escalation, or DSH. Preserve the existing loop conceptually for later implementation and evaluation.
- Measure quality, success rate, total cost, cost per successful task, elapsed time, and token/cache use when available.
- Keep retries, failed attempts, and any measurable tool/provider charges in total-cost accounting.
- Revisit DSH only if Hermes limits a concrete later experiment in modularity or routing.
- Treat published savings as results for their authors' setup, not as expected gains for this project.
- Keep credentials, private prompts, and raw user code out of public benchmark artifacts.

## License

This project is licensed under **GNU General Public License v3.0 only (GPL-3.0-only)**. See [LICENSE](LICENSE) for the complete terms.
