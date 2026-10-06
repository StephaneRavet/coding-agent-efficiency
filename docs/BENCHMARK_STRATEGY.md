# Benchmark Strategy

## Purpose

Measure whether **Hermes running a fixed set of open-source/open-weight models through OpenRouter** can approach OpenAI Codex quality at lower total cost per successfully completed coding task. Begin with a small, reproducible task panel and a fixed model set. This MVP establishes baselines; it does not test dynamic routing or escalation.

## Primary metric and quality gate

For a fixed task panel and execution protocol:

```text
cost_per_successful_task
  = total cost of all runs (including failed tasks)
    / number of tasks whose declared verifier passes
```

Report alongside it:

- solve rate / pass@1 and, if repeated trials are used, pass@k with its meaning;
- the quality threshold and verifier definition;
- total and per-task cost distributions, not only averages;
- model/provider charges, cache-aware input/output charges, retries, and measurable tool costs;
- latency, completion time, tool reliability, and failure categories;
- confidence intervals or paired uncertainty estimates.

Treat a cost comparison as valid only when both systems pass the same quality gate on the same tasks. If the candidate misses the gate, report the result, but do not describe it as an efficiency improvement.

## Experimental controls

1. **Paired tasks:** run each baseline and candidate on identical task IDs and equivalent initial repository states.
2. **MVP harness:** run open models through Hermes and compare with Codex using equivalent task instructions, initial repository states, and verification. Record harness-specific differences that cannot be matched.
3. **Same verifier:** use task-owned tests or a predeclared independent rubric. Keep hidden tests hidden from the agent where applicable.
4. **Repeat stochastic runs:** predeclare trial counts and seeds; distinguish one-attempt success from pass@k.
5. **Freeze conditions:** record model/provider versions, routing configuration, system prompts where allowed, tool versions, concurrency, retries, timeout, and price snapshot.
6. **Cache accounting:** capture provider-reported cache tokens and charges when available. Otherwise label the cache cost model and run sensitivity analysis for cold and warm sessions.
7. **Full-cost accounting:** include all model calls, failed attempts, retries, tools, provider charges, and allocated inference infrastructure where measurable. Explain any excluded human or engineering cost.
8. **No silent task filtering:** publish exclusions, timeouts, invalid runs, and missing telemetry with denominators.
9. **Privacy:** use licensed/public tasks or approved synthetic/private tasks; publish only sanitized aggregates and artifacts.

## MVP comparison

| System | Configuration | Role |
| --- | --- | --- |
| OpenAI Codex | Freeze the available Codex model/version, settings, and date | Quality/cost comparator |
| Hermes + OpenRouter model A | Fixed open-source/open-weight model and provider settings | Open-model candidate |
| Hermes + OpenRouter model B | Fixed open-source/open-weight model and provider settings | Open-model candidate |

Keep the first panel deliberately small: select a few tasks spanning clear coding-task categories, with public/licensed or approved privacy-safe content, deterministic verifiers, and versioned task IDs. Freeze a small set of model IDs and settings before evaluation. Do not add models in response to evaluation outcomes; additions belong to a separately recorded iteration.

The first result should include task-level quality/verifier outcome, success rate, total measured cost, cost per successful task, elapsed time, input/output tokens, and cached-token/cache-charge fields when the harness/provider exposes them. Mark unavailable telemetry as unavailable; do not silently estimate it.

## Later baselines (after the fixed-model MVP)

Start with a small matrix; not every baseline is applicable to every harness or task panel.

| Baseline | Role | Comparison notes |
| --- | --- | --- |
| Fixed inexpensive model | Cost floor | Shows the quality loss and failure/retry cost of always-cheap routing. |
| Fixed strong/frontier model | Quality reference | Use the same harness and verifier; not assumed to be optimal. |
| OpenRouter Auto | Ready-made routing baseline | Freeze date/configuration and compare on identical tasks; record provider and cache telemetry. |
| OpenRouter Pareto Code | Coding-focused model-selection baseline | Record the coding-score tier and any Nitro/throughput setting. It primarily selects per request, so session/cache effects must be observed separately. |
| RouteLLM | Open research/framework baseline | Calibrate the router and threshold on a separate split; do not tune on evaluation tasks. |
| ACRouter + CodeRouterBench | Coding-task routing research baseline | Use its public data/reproduction where compatible; distinguish precomputed routing evaluation from live end-to-end agent runs. |
| Not Diamond Code | Conditional commercial baseline | Include only if access is available and terms permit; record session-level routing, effort, and cache treatment. |
| coding-agent-cost-bench | Task-cost measurement reference | Reuse its cost-per-solved-task framing and verifier/reporting ideas; its harness and task panel are not assumed equivalent. |
| COSPA | Cost/performance benchmark reference | Use its published protocol/results as external context; align harness, task suites, retry semantics, and pricing before direct comparisons. |

Later work may compare OpenRouter Auto/Pareto, RouteLLM, ACRouter, or evidence-based policies, but only after the fixed-model baseline is reproducible. Dynamic routing, escalation, and Jev are deferred. DSH is a possible later modularity/R&D harness if a concrete Hermes limitation is observed; it is not an MVP baseline.

## Experiment sequence

### Phase 0 — Protocol

- Select task suite(s), licensing, task IDs, task categories, and quality bar.
- Define cache-cold/warm policy, retry cap, timeout, concurrency, budget, and price source.
- Write verifier contracts and pre-register exclusions and metrics.

### Phase 1 — Fixed-model MVP

- Freeze a small task panel, verifier, Codex configuration, Hermes version/configuration, fixed OpenRouter model IDs, prices, and run controls.
- Run Codex and each fixed-model Hermes configuration on paired tasks.
- Measure quality, solve rate, cost, cost per success, elapsed time, and available token/cache telemetry; confirm cost inputs can be reconstructed.

### Phase 2 — Harness and execution validation

- Resolve protocol mismatches and telemetry gaps found in the MVP; rerun the frozen panel when changes affect comparability.
- Do not introduce routing or escalation in this phase.

### Phase 3 — Router swaps (later)

- Add OpenRouter Auto and Pareto Code where available, then RouteLLM or ACRouter when the execution interface and terms permit.
- Hold harness, tasks, verifier, tools, and budget constant.

### Phase 4 — Task trajectory policies (later)

- Compare fixed model, task-level choice, sticky cascade, and step/phase routing.
- Add cache-aware decisions and measure model-switch frequency, cache hits, and total cost.
- Add Jev only for bounded decisions and separately account for its calls, latency, and errors.

### Phase 5 — Robustness, transfer, and harness alternatives (later)

- Repeat on held-out repositories/task categories and newer price/model snapshots.
- If Hermes is limiting an identified modular experiment, compare a DSH implementation while holding the task and verifier contract constant.
- Report quality-constrained cost, uncertainty, route distribution, failure modes, and sensitivity to cache and price assumptions.

## Minimum result table

| Policy | Tasks | Trials/task | Solve rate | Quality gate | Cost/task | Cost/success | p50 / p95 time | Cache hit / miss | Router cost | Escalations |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | ---: | ---: |

Every figure needs a run ID and a path to a machine-readable, privacy-reviewed source record. Report failed and incomplete runs explicitly.

## Interpretation rules

- Report quality and cost together; do not rank solely by token count, router accuracy, or average call price.
- Distinguish published figures from replications and project measurements.
- Do not infer universal savings from a single benchmark, task mix, or price snapshot.
- State when cached-token telemetry is unavailable or estimated.
- Make a recommendation only within the tested tasks, harnesses, models, prices, and quality bar.
