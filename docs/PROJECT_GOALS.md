# Project Goals

## Objective

Find coding-agent configurations that minimize **total cost per successfully completed coding task** while maintaining a predeclared, verifiable quality threshold.

The unit of optimization is the complete task trajectory, including model calls, cache effects, tools, retries, and verification. The project does not optimize token price or per-request price in isolation.

## MVP decision

- Operational harness: **Hermes**.
- Optimization: Hermes with fixed open-source/open-weight models through **OpenRouter**; Codex is outside the MVP.
- Agentic loop: preserve the loop concept already defined in the project Markdown as the conceptual target; do not redesign it as part of this harness pivot.
- First experiment: small, reproducible task panel; fixed model set; identical tasks, repository states, and verifier.
- Out of MVP: dynamic routing, model escalation, bounded Jev decisions, and DSH implementation/integration.
- Later R&D: consider DSH to test more modular strategies if Hermes becomes a demonstrated limitation.
- No benchmark result or harness superiority is assumed in advance.

## Research questions

1. Which Hermes/OpenRouter configuration minimizes verified task cost while meeting the quality floor?
2. How do quality, success rate, total cost, cost per successful task, elapsed time, and token/cache usage vary by OpenRouter model configuration?
3. If Hermes becomes limiting, which modular strategies would a later DSH experiment make possible?
4. In later phases, when does sticky task/phase routing or evidence-based escalation help after cache and switching costs?
5. How transferable are results across repositories, task types, harnesses, providers, and time?

## Evaluation principles

- **Fixed MVP configuration:** hold Hermes, each OpenRouter model, tasks, and verifier fixed within each baseline run.
- **Future replaceability:** keep the evaluation contract separable from harness-specific events so later harness or router comparisons remain possible.
- **Task-level accounting:** include all attempts, routing calls, cached and uncached tokens, provider/tool charges, and relevant runtime costs.
- **Quality before savings:** compare cost only among configurations meeting the same minimum quality bar; report solve rate with every cost result.
- **Deterministic verification:** use task tests, build/lint checks, or a documented independent rubric; do not equate an agent's self-report with success.
- **Small, explainable choices:** use a small fixed model set for the MVP; add models or tiers only when experiments justify them.
- **Reproducibility:** record versions, configuration, task set, prices, cache assumptions, concurrency, seeds, and verifier outputs.

## Later architecture principles

These principles retain the conceptual loop and guide post-MVP routing experiments; they do not add MVP scope.

- **Evidence-based escalation:** prefer verifier failures, repeated errors, bounded retry counts, and explicit budget limits over prompt-only guesses.
- **Cache awareness:** include cache hits, cache misses, and model-switch effects in routing and evaluation.
- **Bounded Jev use:** use Jev for structured classifications or choices with defined options and a deterministic fallback. Do not delegate open-ended implementation or verification to it.

## Later decision hierarchy

```text
Can deterministic evidence decide?
  yes -> apply the deterministic rule
  no  -> can this be expressed as a bounded classification or choice?
           yes -> ask Jev (or a comparable bounded decision service)
           no  -> use a generative model only where open-ended reasoning is needed
```

Examples of deterministic evidence include test exit status, build/lint results, retry count, repeated error signatures, changed-file scope, elapsed time, budget consumption, and whether required checks passed.

## Preserved agentic loop and later architecture hypotheses

The existing agentic loop described in the Markdown documents remains the conceptual design. This MVP changes the operational harness to Hermes; it does not change that loop's concepts. Dynamic selection, retries/escalation policy, and router decisions are deferred until fixed-model baselines exist.

- Separate task-level model routing from provider failover.
- Route at task start or a meaningful phase boundary; keep a model stable through a tool loop when switching would discard useful cache state.
- Permit escalation when new execution evidence changes the expected cost of continuing at the current tier.
- Compare task-level cascades and step-level policies as separate strategies.
- Record the reason, evidence, selected tier, cache context, and estimated incremental cost for every route and escalation.

## Acceptance contract for a claimed improvement

A claimed MVP advantage is supported only when a paired, reproducible evaluation shows:

1. the same task panel and verifier were used for the candidate and its baseline;
2. the candidate meets the predeclared quality threshold, with solve rate and uncertainty reported;
3. measured total cost per successful task is lower, after all attempts and measurable tool/provider costs;
4. latency, cache behavior, failures, and task-level outcomes are reported;
5. the result can be reproduced from versioned configuration and raw, privacy-safe measurements.

No improvement is claimed until these conditions have been measured.

## Non-goals

- Maximizing the number of supported models or providers.
- Adding another harness such as DSH before a concrete Hermes limitation is measured.
- Adding dynamic routing, escalation, or DSH to the initial MVP.
- Replacing tests with model confidence or self-review.
- Claiming universal savings from results on one benchmark or provider price snapshot.
- Publishing private task content, source code, credentials, or trace data without authorization.
