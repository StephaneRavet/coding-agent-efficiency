# Model Routing

## Goal

Select the least costly model configuration that can complete the current coding task while preserving the project's quality threshold. Routing is a policy under evaluation; it is not tied to one harness, provider, router, or model family.

## Replaceable boundaries

```text
task and repository
        |
        v
coding-agent harness <---- interchangeable adapter
        |
        +---- router policy <---- interchangeable policy adapter
        |       | deterministic rules
        |       | bounded Jev decisions (optional)
        |       | learned/agentic router (optional)
        |
        v
capability tier -> provider/model mapping -> execution
        |
        v
deterministic verifier -> evidence -> continue / finish / escalate
```

Keep semantic capability tiers separate from provider routing. A tier such as `fast`, `strong`, or `frontier` expresses required capability; provider/model selection and failover implement that tier.

## Routing lifecycle

### 1. Establish a task baseline

Capture task category, repository/workflow metadata permitted by the privacy policy, hard constraints, current budget, candidate tiers, and known verification commands. Reuse cached task and model facts where valid.

### 2. Make the cheapest reliable initial decision

1. Apply deterministic eligibility and safety rules.
2. If uncertainty remains and the output is bounded, optionally use Jev to choose among a fixed set of tiers, classify task difficulty, or recommend whether more context is needed.
3. Use a generative model for decisions that require open-ended reasoning.

Record the decision and its evidence. If a decision service is unavailable or uncertain, apply a documented deterministic fallback.

### 3. Keep routing sticky when cache economics support it

Default to one tier for the task or coherent phase. Do not switch for each model call. Before changing tiers, estimate the incremental value of the switch against:

- cache-hit and cache-miss pricing for the current and target models;
- context that must be resent or reconstructed;
- remaining expected work and task budget;
- expected quality or completion probability gain;
- latency and any router overhead.

Model switches are allowed when expected quality or completion savings justify their cache and transition cost. Record both the reason and observed cache usage. Cache behavior is provider- and harness-specific, so never assume that a switch always has the same cost.

### 4. Verify execution with observable evidence

Run the task's declared verifier. Preserve raw exit codes and structured results. An agent's statement that work is complete is not a verifier result.

### 5. Escalate from evidence

Escalation may use evidence such as:

- a required test, type check, build, or lint failure;
- repeated failure with the same normalized signature;
- bounded attempts exhausted without progress;
- a measured task-risk or budget threshold crossed;
- a missing capability or tool that the current tier cannot provide.

Do not escalate solely because the initial prompt appears difficult when the execution evidence does not support it. Escalate by the smallest capability step that is likely to change the outcome, subject to the remaining budget and policy constraints. Avoid retrying the same failing action without a changed hypothesis.

### 6. Stop and account

Stop when the verifier passes, when the budget/attempt policy is exhausted, or when a deterministic terminal condition is reached. Count every routing call, retry, model attempt, cache category, tool charge, and failed task in the run record.

## Sticky routing versus step-level routing

Evaluate these separately:

| Policy | Decision frequency | Main benefit | Main risk |
| --- | --- | --- | --- |
| Fixed model | Once for the full task | Simple, stable cache behavior | Pays for excess capability or misses hard tasks |
| Task-level router | Once per task | Low routing overhead; stable session | Cannot react to later evidence |
| Sticky cascade | Initial tier plus evidence-based upward escalation | Learns from verifier/execution results | Retries may add cost before escalation |
| Step-level router | Per meaningful step or phase | Matches changing subtask difficulty | Router overhead and cache fragmentation |

Do not compare policies using only classification accuracy. Compare completed task outcomes and complete task cost.

## Decision log contract

For each task and route, retain only privacy-safe fields needed for reproduction:

- task/run ID, harness and adapter version;
- policy, policy version, decision boundary, and reason;
- selected tier, model/provider identifier, and fallback path;
- task/phase boundary and whether the model changed;
- input/output/cache token counts when available, price snapshot, and measured cost;
- verifier result, failure signature category, retry/escalation count;
- elapsed time and budget state.

Never store raw private prompts, repository source, credentials, or unredacted traces in public results by default.
