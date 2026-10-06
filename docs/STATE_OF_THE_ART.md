# State of the Art: Coding-Agent Cost and Model Routing

**Snapshot date: 2026-10-06**  
**Research status: source check completed on 2026-10-06; availability and prices can change.**

## Summary

The problem is active across commercial routers, open routing frameworks, agentic routing research, and coding-agent cost benchmarks. The distinctive project question is not whether one router beats every model in general. It is whether a replaceable harness/router configuration can lower **verified cost per completed coding task** on a fixed task mix without crossing a declared quality floor.

Published percentages are setup-specific. They are not expected gains for this project until reproduced with the same tasks, harness, verifier, cache treatment, and accounting.

## Available solutions and tools

| System | Status on 2026-10-06 | What it offers | Limits for this R&D |
| --- | --- | --- | --- |
| OpenRouter Auto | Public hosted router | Ready request-level model selection; OpenRouter's router benchmark reports quality, speed, and cost across benchmark suites. | General benchmark scores are not proof of coding-task session economics; provider, cache, and route behavior need logging. |
| OpenRouter Pareto Code | Public hosted code-focused router | Chooses from a tiered coding-model shortlist using a requested minimum coding score; a throughput variant is available. | The tier selection is useful as a baseline, but does not by itself establish task-level completion cost across a coding-agent trajectory. |
| RouteLLM | Public open-source framework | OpenAI-compatible serving/evaluation and trained request routers; the project reports up to 85% cost reduction while retaining 95% GPT-4 performance on its evaluation setup. | Primarily request-level routing; reported result is not a coding-agent end-to-end guarantee. |
| Not Diamond Code | Commercial product, gated early access | Documentation describes session-level routing over expected downstream work, model, reasoning effort, and cache state; advertises 20%+ lower inference cost. | Documentation says access is waitlist-gated. Access was not verified; claims are vendor-reported and require an eligible trial for independent comparison. |
| Jev-powered routers | Several public community projects | Examples route coding-agent turns among bounded model tiers; some keep sessions sticky to protect per-model prompt cache. | Independent implementations vary in protocol, policy, telemetry, and maturity. Treat each as a separate baseline, not a standard. |

Sources: [OpenRouter router benchmarks](https://openrouter.ai/benchmarks/routers), [OpenRouter benchmark announcement](https://openrouter.ai/blog/announcements/model-router-benchmarks/), [Pareto Code API page](https://openrouter.ai/openrouter/pareto-code/api), [RouteLLM repository](https://github.com/lm-sys/RouteLLM), [Not Diamond Code documentation](https://code.notdiamond.ai/docs/), [Jev router example](https://github.com/dirien/jev-router).

## Research and development

| Work | Contribution | Relevance and caveat |
| --- | --- | --- |
| **T2MO** (2026) | Data-driven task-to-model optimization for coding assistants; frames expected cost per completed task with retries/escalation and proposes staged rollout from static policies to verified cascades. | Strong alignment with this project's metric. It is a research methodology and its reported framework is not a ready interchangeable harness. |
| **ACRouter / Agent-as-a-Router** (2026) | Agentic routing with Orchestrator, Verifier, Memory, and Router; introduces CodeRouterBench and reports results across coding tasks/models. | The public repository includes data and reproducible scripts. Distinguish offline benchmark replay from a live harness end-to-end evaluation. |
| **AgentRouter** (2026) | Research on assigning model tiers to steps in multi-step workflows; its preprint reports 72% lower cost and 97.3% of frontier-only quality on its own setup. | Directly motivates step-level routing. Treat its headline as author-reported and verify whether per-step switching remains beneficial after real harness/cache costs. |

Sources: [T2MO paper](https://arxiv.org/abs/2608.08528), [ACRouter paper](https://arxiv.org/abs/2606.22902), [ACRouter implementation and CodeRouterBench](https://github.com/LanceZPF/agent-as-a-router), [AgentRouter paper](https://arxiv.org/abs/2609.22951).

## Benchmarks and measurement projects

| Resource | What it measures | How to use it here |
| --- | --- | --- |
| CodeRouterBench | A coding-task/model result matrix used to evaluate routing policies; the repository describes a 9,999-task, 8-model in-distribution dataset and additional OOD data. | Reuse its data/protocol when compatible; do not conflate matrix replay with execution of a full coding agent. |
| `coding-agent-cost-bench` | Repeated coding-agent runs with task-owned tests, cost, solve rate, and cost per solved task; its public README documents the evaluated setups and billing method. | A close measurement precedent. Reuse accounting and verifier ideas, while keeping task/harness differences explicit. |
| COSPA | Cost-performance evaluation of coding agents on a published 336-task panel, recording correctness, token use, elapsed time, and estimated API cost. | External comparison point. Direct comparisons require protocol, harness, task, and price alignment. |
| OpenRouter Model Router Benchmarks | Router/model comparisons across varied benchmarks with quality, speed, and cost dimensions. | Useful hosted-router baseline and methodology reference; not coding-task-specific in every suite. |

Sources: [CodeRouterBench repository](https://github.com/LanceZPF/agent-as-a-router), [`coding-agent-cost-bench`](https://github.com/agencyenterprise/coding-agent-cost-bench), [COSPA](https://github.com/shisa-ai/cospa), [OpenRouter router benchmarks](https://openrouter.ai/benchmarks/routers).

## Reusable ideas

1. **Optimize expected completion cost.** Count failed attempts and escalations; a lower-cost call is not a lower-cost task when it fails more often. [T2MO](https://arxiv.org/abs/2608.08528)
2. **Keep the comparison unit explicit.** A result belongs to a harness/model/router/task combination, not to a model name alone. [ACRouter](https://arxiv.org/abs/2606.22902) and [COSPA](https://github.com/shisa-ai/cospa)
3. **Use verified feedback.** Route or escalate from test outcomes, execution state, and previous attempts; keep verifier evidence separate from model self-assessment. [ACRouter](https://github.com/LanceZPF/agent-as-a-router)
4. **Measure trajectory-level policies.** Task-level stickiness and step-level adaptation are competing policies; assess both end-to-end, including decision overhead. [AgentRouter](https://arxiv.org/abs/2609.22951)
5. **Account for cache and switching.** Commercial and community documentation identifies cache state as relevant to long-horizon routing; verify the effect from provider telemetry instead of assuming a universal penalty. [Not Diamond Code](https://code.notdiamond.ai/docs/), [Jev router example](https://github.com/dirien/jev-router)
6. **Use a small, calibrated pool.** Request-level routers and Pareto-style tiers offer ready baselines, but route thresholds must be measured on the target task mix. [RouteLLM](https://github.com/lm-sys/RouteLLM), [Pareto Code](https://openrouter.ai/openrouter/pareto-code/api)
7. **Keep reproducible records.** Freeze task IDs, verifier, prices, versions, cache assumptions, concurrency, and retry semantics; make each reported cost reconstructible. [coding-agent-cost-bench](https://github.com/agencyenterprise/coding-agent-cost-bench), [COSPA](https://github.com/shisa-ai/cospa)

## Project position

This project will test an **interchangeable R&D harness** rather than commit to one provider stack. It will compare ready routers and research policies on paired coding tasks, with deterministic verification and full trajectory cost accounting. Sticky routing, cache awareness, bounded Jev decisions, and evidence-based escalation are hypotheses in the experimental design, not assumed wins.

Initial candidate baselines:

- fixed inexpensive model and fixed strong/frontier model;
- OpenRouter Auto and Pareto Code;
- RouteLLM;
- ACRouter using CodeRouterBench and, where practical, an end-to-end adapter;
- Not Diamond Code only if access is granted and its terms allow evaluation;
- task-cost references from `coding-agent-cost-bench` and COSPA.

## Sources and limits

- All links were checked on **2026-10-06** for this snapshot.
- Product documentation, repository README files, and preprints are primary sources, but product metrics remain vendor claims and paper metrics remain results for the authors' conditions.
- No independent replication was performed for this document.
- Prices, APIs, access status, source code, and benchmark releases may change after the snapshot date.
