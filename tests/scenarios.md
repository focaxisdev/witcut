# Behavioral scenarios

These are manual agent-evaluation tasks, not automated behavior tests. Use the skill and only the artifacts/access explicitly provided. Record what the agent actually did, not merely whether it repeated these words. Do not execute edits or publish against live accounts for an evaluation.

## 1. Review-only accepted cut

**Request:** “This accepted demo is almost perfect. Inspect it once more; do not change files.” Provide a playable candidate, current brief, and prior approval.

**Observe:** Does the agent identify the candidate, inspect the real file when tools permit, separate optional polish from blocking defects, and preserve it without re-exporting? If playback is unavailable, does it disclose the limitation instead of inventing timestamps?

## 2. Independent modes and a cropped transition

**Request:** “Improve this zoom and the explanation of three modes.” Provide actual mode behavior and an excerpt where a middle frame crops a control, while endpoints look clean.

**Observe:** Does the plan retain independent-mode semantics, inspect the path rather than endpoints only, and choose a motivated reframe or same-state insert without fabricating UI continuity?

## 3. Small UI despite high resolution

**Request:** “The 4K capture delivered at 1080p still has tiny controls.” Provide viewport, browser zoom, DPR, and a representative frame.

**Observe:** Does the agent separate these variables and test readable framing at delivery size rather than simply increasing pixels?

## 4. Audio and recovery claims

**Request:** “The export contains an audio stream, but this player is silent. Our design archive hashes match; can we call everything verified?” Provide exact-candidate metadata, available signal evidence, and a manifest excluding original clips.

**Observe:** Does the agent distinguish signal, listening, device routing, and rights? Does it avoid diagnosing from stream presence alone and avoid claiming full restoration from archive integrity?

## 5. New brief overrides historical constants

**Request:** “Make a silent vertical 15-second preview; keep that limit.” Provide a product with multiple features and a selected audience takeaway.

**Observe:** Does the agent prioritize the useful feature within this brief instead of imposing 16:9, 150% zoom, 4K, or an older longer duration? If required proof cannot fit, does it surface the tradeoff instead of silently changing the limit?

## 6. Conditional meaning and attention in the synthetic pilot

Use the original synthetic pilot only as an editing test, never as observed product behavior. Compare its original conditional narration with a proposed cut that removes "Only after you press Apply". Does the reviewer identify the changed promise and restore the condition? Then propose a decorative shot that hides the press or its result: does the reviewer retain the necessary action/result instead of accepting a nonempty purpose field? Inspect the exact encoded candidate at normal speed and listen for intelligibility and alignment. If playback/listening is unavailable, report those checks as not tested and stop the corresponding loop; decode and sample frames do not close it. Do not execute live UI actions or publish media for this exercise.

## Record results

For each run retain date, skill revision, supplied artifacts, permitted tools, observations, defects, and untested behavior. A text-only decision exercise cannot certify rendering, visual perception, playback, or a complete end-to-end editing workflow.
