# Coding Agent Efficiency

**Research and development on reducing cost per successfully completed coding task while preserving a verifiable quality threshold.**

This project evaluates whether open-source/open-weight models served through OpenRouter can reduce the cost of coding tasks versus OpenAI Codex while meeting the same declared quality bar. **Hermes is the operational harness for the MVP.** The agentic loop already defined in the project Markdown remains the conceptual target; this first experiment uses fixed models and does not yet implement model routing or escalation.

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

This repository starts as an R&D brief and literature map. It contains no implementation or benchmark results yet. The next step is to freeze a small, reproducible task panel and a fixed set of OpenRouter open-source/open-weight models, then compare Hermes runs with Codex using the same tasks and verifier. Record quality, success rate, total cost, cost per successful task, elapsed time, and token/cache telemetry when available. Dynamic routing, escalation, and DSH are later experiments, not MVP requirements.

## Documents

- [Project goals](docs/PROJECT_GOALS.md): objective, constraints, and acceptance contract.
- [Model routing](docs/MODEL_ROUTING.md): the preserved conceptual agentic loop and later routing experiments.
- [Benchmark strategy](docs/BENCHMARK_STRATEGY.md): Hermes MVP protocol, metrics, controls, and later experiment sequence.
- [State of the art](docs/STATE_OF_THE_ART.md): source-backed snapshot dated 2026-10-06.

## Guiding metric

```text
cost_per_successful_task
  = total measured cost across all attempts and routing overhead
    / number of tasks passing the declared quality verifier
```

Always report the success rate and quality threshold beside this metric. A lower cost per success is meaningful only when the compared systems meet the same quality bar on the same tasks.

## Scope and decisions

- MVP harness: Hermes; comparator: OpenAI Codex; inference target for open models: OpenRouter.
- Start with a small, fixed task panel and model set; justify additions with measured gains.
- The MVP does not add dynamic routing, escalation, or DSH. Preserve the existing loop conceptually for later implementation and evaluation.
- Measure quality, success rate, total cost, cost per successful task, elapsed time, and token/cache use when available.
- Keep retries, failed attempts, and any measurable tool/provider charges in total-cost accounting.
- Revisit DSH only if Hermes limits a concrete later experiment in modularity or routing.
- Treat published savings as results for their authors' setup, not as expected gains for this project.
- Keep credentials, private prompts, and raw user code out of public benchmark artifacts.

## License

This project is licensed under **GNU General Public License v3.0 only (GPL-3.0-only)**. See [LICENSE](LICENSE) for the complete terms.
