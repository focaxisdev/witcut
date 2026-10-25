# Collaboration: bounded decisions, shared evidence

Read when choosing an execution strategy, delegating work, or coordinating revision loops. These are responsibilities, not required agent counts. One agent can hold several roles; a separate reviewer is useful when the consequence or ambiguity justifies it.

## Choose capability for the decision

First inspect which models, reasoning controls, tools, and delegation mechanisms the environment actually exposes. Record the selected configuration when it is available; otherwise state that it cannot be selected or observed. Do not name a vendor model as a requirement or claim that a prompt changed an unavailable setting.

Use the least costly available capability that can satisfy the acceptance check. Deterministic validation, asset inventory, and a known render command usually need execution tools more than deeper reasoning. Ambiguous source meaning, causal edits, conflicting constraints, and consequential viewer claims warrant stronger available reasoning and, where useful, an independent reviewer. Increase capability in response to a specific unresolved failure, not to compensate for missing media, permission, or playback. A larger model cannot establish an observation it never made.

Delegate bounded, separable work only when coordination costs are justified and delegation is authorized. Give each worker the brief revision, exact inputs, permitted actions, expected artifact, acceptance check, and blockers to report. Avoid concurrent writes to the same file or output directory. The coordinator resolves incompatible assumptions and remains responsible for the whole film.

## One loop contract at every layer

Before an expensive loop, identify its input/version, intended artifact, acceptance evidence, responsible role, and a finite attempt or time budget suited to the task. After a failure, name its viewer impact, make the smallest authorized correction, and rerun the affected check plus relevant integration checks. Keep failed candidates separate. Escalate when the fix changes the brief, requires unavailable evidence/authority, crosses another role's boundary, or repeats without new evidence. Repeating the same check without a change or new evidence is not progress.

Stop when the acceptance check is satisfied and no blocking defect remains, or when the budget or a real blocker prevents it. Report optional polish separately. Missing evidence is `not tested` or a blocker, never a pass. Read-only and frozen boundaries apply to every nested loop.

| Layer / responsible role | Input → artifact | Acceptance and local correction | Escalation and stop |
| --- | --- | --- | --- |
| Audience goal / coordinator | Current brief + integrated candidate → decision and tradeoffs | At normal speed, can the intended viewer understand the takeaway, necessary action, result, and qualifying conditions? Revise the smallest failing segment. | Escalate incompatible duration, truth, rights, or access constraints. Stop at the agreed goal or report the unresolved requirement; subtask passes cannot substitute for this decision. |
| Planning / planner | Brief + source observations → script, shot plan, missing materials | Check structural invariants and review source meaning, omissions, and voice/image alignment. Correct the affected scene or dependency. | Escalate unsupported claims or conflicting goals; stop with a usable plan or named missing inputs. |
| Sources / material owner | Required evidence + authorized inputs → identified assets, ranges, provenance and limitations | Inspect the required state and retain enough context to preserve meaning. Replace or recapture the deficient range. | Escalate absent access, unclear rights, or unverifiable source claims; stop before treating intended evidence as observed. |
| Execution / editor or adapter operator | Accepted plan + resolved assets + settings → new candidate and reproducible execution record | Validate range/time mapping, decode, and compare critical boundaries with the plan. Fix the local mapping or execution failure. | Escalate plan changes or unsupported adapter operations; stop with an identified candidate or exact failed command and outcome. |
| Review / reviewer | Exact candidate + brief + source context → timestamped findings with evidence and untested checks | Apply [QA](qa.md), including normal-speed viewing and actual listening where available. Return the smallest blocking correction to its owner; inspect the changed candidate. | Escalate semantic disagreement or unavailable observation. Stop after required checks and resolved blockers; keep owner acceptance separate. |

A review handoff names the candidate/hash, methods actually used, findings, and remaining uncertainty. An independent reviewer should inspect the evidence rather than inherit the producer's desired verdict. Source checks, code tests, and successful encoding support their own claims only; none alone establishes a comprehensible film.
