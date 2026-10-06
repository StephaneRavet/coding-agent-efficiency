# Project Goals

## Objective

Find coding-agent configurations that minimize **total cost per successfully completed coding task** while maintaining a predeclared, verifiable quality threshold.

The unit of optimization is the complete task trajectory, including routing, model calls, cache effects, tools, retries, verification, and escalation. The project does not optimize token price or per-request price in isolation.

## Research questions

1. Which combinations of harness, router, model pool, and verifier reach the quality threshold at the lowest task-level cost?
2. When does sticky task- or phase-level routing outperform per-call routing after accounting for cache reuse and switching costs?
3. Which deterministic signals justify escalation, and how much do they reduce failed retries without over-escalating?
4. Which bounded decisions can Jev make reliably and cheaply enough to improve on deterministic policies?
5. How transferable are results across repositories, task types, harnesses, providers, and time?

## Core principles

- **Harness-independent:** adapters isolate harness-specific events from the evaluation contract.
- **Router-independent:** policies can be swapped while holding tasks, harness, verifier, and candidate models constant.
- **Task-level accounting:** include all attempts, routing calls, cached and uncached tokens, provider/tool charges, and relevant runtime costs.
- **Quality before savings:** compare cost only among systems meeting the same minimum quality bar; report solve rate with every cost result.
- **Evidence-based escalation:** prefer verifier failures, repeated errors, bounded retry counts, and explicit budget limits over prompt-only guesses.
- **Deterministic verification:** use task tests, build/lint checks, or a documented independent rubric; do not equate an agent's self-report with success.
- **Small, explainable choices:** maintain a few capability tiers and provider fallbacks; add options only when experiments justify them.
- **Cache awareness:** include cache hits, cache misses, and model-switch effects in routing and evaluation.
- **Bounded Jev use:** use Jev for structured classifications or choices with defined options and a deterministic fallback. Do not delegate open-ended implementation or verification to it.
- **Reproducibility:** record versions, configuration, task set, prices, cache assumptions, concurrency, seeds, and verifier outputs.

## Decision hierarchy

```text
Can deterministic evidence decide?
  yes -> apply the deterministic rule
  no  -> can this be expressed as a bounded classification or choice?
           yes -> ask Jev (or a comparable bounded decision service)
           no  -> use a generative model only where open-ended reasoning is needed
```

Examples of deterministic evidence include test exit status, build/lint results, retry count, repeated error signatures, changed-file scope, elapsed time, budget consumption, and whether required checks passed.

## Architecture hypotheses

- Separate task-level model routing from provider failover.
- Route at task start or a meaningful phase boundary; keep a model stable through a tool loop when switching would discard useful cache state.
- Permit escalation when new execution evidence changes the expected cost of continuing at the current tier.
- Compare task-level cascades and step-level policies as separate strategies.
- Record the reason, evidence, selected tier, cache context, and estimated incremental cost for every route and escalation.

## Acceptance contract for a claimed improvement

A routing change is an improvement only when a paired, reproducible evaluation shows:

1. the same task panel and verifier were used for the candidate and its baseline;
2. the candidate meets the predeclared quality threshold, with solve rate and uncertainty reported;
3. measured total cost per successful task is lower, after routing and retry costs;
4. latency, cache behavior, failures, and task-level outcomes are reported;
5. the result can be reproduced from versioned configuration and raw, privacy-safe measurements.

No improvement is claimed until these conditions have been measured.

## Non-goals

- Maximizing the number of supported models or providers.
- Selecting a single permanent harness or router before comparative evidence exists.
- Replacing tests with model confidence or self-review.
- Claiming universal savings from results on one benchmark or provider price snapshot.
- Publishing private task content, source code, credentials, or trace data without authorization.
