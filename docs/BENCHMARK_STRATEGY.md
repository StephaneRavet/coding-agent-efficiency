# Benchmark Strategy

## Purpose

Measure whether routing reduces the **total cost of successfully completing coding tasks** without lowering quality below a declared threshold. Use public benchmark suites for comparability and a separate, privacy-safe task panel representative of intended use.

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
- routing overhead, model/provider charges, cache-aware input/output charges, retries, and escalation;
- latency, completion time, tool reliability, and failure categories;
- confidence intervals or paired uncertainty estimates.

Treat a cost comparison as valid only when both systems pass the same quality gate on the same tasks. If the candidate misses the gate, report the result, but do not describe it as an efficiency improvement.

## Experimental controls

1. **Paired tasks:** run each baseline and candidate on identical task IDs and equivalent initial repository states.
2. **Same harness when testing routers:** swap only the router or policy. Report harness-comparison experiments separately.
3. **Same verifier:** use task-owned tests or a predeclared independent rubric. Keep hidden tests hidden from the agent where applicable.
4. **Repeat stochastic runs:** predeclare trial counts and seeds; distinguish one-attempt success from pass@k.
5. **Freeze conditions:** record model/provider versions, routing configuration, system prompts where allowed, tool versions, concurrency, retries, timeout, and price snapshot.
6. **Cache accounting:** capture provider-reported cache tokens and charges when available. Otherwise label the cache cost model and run sensitivity analysis for cold and warm sessions.
7. **Full-cost accounting:** include router/Jev decisions, failed attempts, retries, escalation, tools, and allocated inference infrastructure. Explain any excluded human or engineering cost.
8. **No silent task filtering:** publish exclusions, timeouts, invalid runs, and missing telemetry with denominators.
9. **Privacy:** use licensed/public tasks or approved synthetic/private tasks; publish only sanitized aggregates and artifacts.

## Baselines to compare

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

Keep an internal `router-under-test` row for each candidate policy: deterministic-only, bounded Jev, and evidence-based cascade. Compare one decision policy at a time before composing policies.

## Experiment sequence

### Phase 0 — Protocol

- Select task suite(s), licensing, task IDs, task categories, and quality bar.
- Define cache-cold/warm policy, retry cap, timeout, concurrency, budget, and price source.
- Write verifier contracts and pre-register exclusions and metrics.

### Phase 1 — Baselines

- Run fixed cheap and fixed strong models through one harness.
- Measure the success/cost/latency frontier and confirm that all cost inputs can be reconstructed.

### Phase 2 — Router swaps

- Add OpenRouter Auto and Pareto Code where available, then RouteLLM or ACRouter when the execution interface and terms permit.
- Hold harness, tasks, verifier, tools, and budget constant.

### Phase 3 — Task trajectory policies

- Compare fixed model, task-level choice, sticky cascade, and step/phase routing.
- Add cache-aware decisions and measure model-switch frequency, cache hits, and total cost.
- Add Jev only for bounded decisions and separately account for its calls, latency, and errors.

### Phase 4 — Robustness and transfer

- Repeat on held-out repositories/task categories and newer price/model snapshots.
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
