# Coding Agent Efficiency

**Research and development on reducing cost per successfully completed coding task while preserving a verifiable quality threshold.**

This project studies coding-agent systems as complete, replaceable configurations: a harness, a routing policy, models, tools, and verification. The objective is not to minimize token price or the cost of an isolated model call. It is to spend less across the full task while meeting a declared quality bar.

## Research premise

The working hypothesis is that task-level economics improve when a system:

- can swap coding-agent harnesses and routers without changing the evaluation contract;
- chooses from a small set of capability tiers and keeps routing sticky through a task or phase when cache reuse makes that cheaper;
- accounts for prompt-cache state and the cost of switching models;
- uses Jev only for bounded, structured decisions that deterministic rules cannot settle;
- verifies outcomes with task tests and other observable checks;
- escalates after evidence of difficulty, such as repeated failures, rather than prompt appearance alone.

These are hypotheses to measure, not claimed results. No router, harness, or model is selected as the permanent implementation.

## Current status

This repository starts as an R&D brief and literature map. It contains no implementation or benchmark results yet. The next research step is to select a small, reproducible task panel and compare a fixed-model baseline with available routing baselines under the same harness and verifier.

## Documents

- [Project goals](docs/PROJECT_GOALS.md): objective, constraints, and acceptance contract.
- [Model routing](docs/MODEL_ROUTING.md): interchangeable routing design and decision policy.
- [Benchmark strategy](docs/BENCHMARK_STRATEGY.md): metrics, controls, baselines, and experiment sequence.
- [State of the art](docs/STATE_OF_THE_ART.md): source-backed snapshot dated 2026-10-06.

## Guiding metric

```text
cost_per_successful_task
  = total measured cost across all attempts and routing overhead
    / number of tasks passing the declared quality verifier
```

Always report the success rate and quality threshold beside this metric. A lower cost per success is meaningful only when the compared systems meet the same quality bar on the same tasks.

## Scope and decisions

- Harness, router, providers, and model pool remain replaceable.
- Start with a small model pool; justify each additional tier or model with measured gains.
- Keep router overhead, cache-aware input cost, retries, escalation, and failed attempts in the accounting.
- Treat published savings as results for their authors' setup, not as expected gains for this project.
- Keep credentials, private prompts, and raw user code out of public benchmark artifacts.

## License

This project is licensed under **GNU General Public License v3.0 only (GPL-3.0-only)**. See [LICENSE](LICENSE) for the complete terms.
