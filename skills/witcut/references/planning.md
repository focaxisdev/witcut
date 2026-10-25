# Evidence-linked planning core (v1)

Use `../scripts/plan.py` and the [product-demo fixture](../examples/plans/product-demo.json) or [podcast-to-video fixture](../examples/plans/podcast-to-video.json). These are original synthetic, text-only fixtures, not captured media, private radio content, or rights-clearance examples.

The executable `SCHEMA` in `plan.py` is the strict format authority: all keys required, unknown keys rejected, numeric seconds finite. `version` is the string `1`. CLI (from repository root):

```sh
python3 skills/witcut/scripts/plan.py skills/witcut/examples/plans/product-demo.json --out /tmp/witcut-plan
```

The output directory must not exist. Exit 0 means structural/timeline/evidence-link checks passed, **not** that the story or footage is verified. Missing production materials may remain. Invalid input exits 1 and reports errors; no artifacts are emitted. Outputs are `script.md`, `shot-plan.json`, and `missing-materials.json`, all derived from one input. The shot plan includes accumulated timeline coordinates; it is an output artifact, not an editable input round-trip format.

## Plan and review

- Brief: identify the latest revision, actual duration bounds and required operations. Caller must check the latest brief externally; equal revision strings cannot establish freshness.
- Sources: declare `modality` (`audio`, `visual`, `audiovisual`, or `script`), actual duration and provenance; `real` means observed documentary/product source, never AI-generated or editorially fabricated imagery. Production graphics, AI images, reenactments, and other non-documentary assets use `editorial`, not `real` or `synthetic-fixture`; they cannot prove a `current` claim. Both production kinds use `verified`/`unverified` and `cleared`/`unknown`. Synthetic fixtures must use `fixture` and `fixture-only`. These fields record supplied assertions; this tool does not open media, verify a license, or certify an observation.
- Operations: every inventoried operation must appear in a scene or carry an explicit nonempty `omission_reason`; shown operations use an empty reason. Required operations cannot be omitted even with a reason. Review omissions for hidden manual prerequisites. Record observable/manual actions, source ranges, and `independent` or `sequential` relationships. Independent alternatives cannot list predecessors. Sequential dependencies must be acyclic and appear earlier in the plan; same-source predecessor ranges must precede their successors. Different-source continuity must be reviewed by a person/agent against actual evidence.
- Scenes: evidence references declare a `role` (`narration`, `visual`, or `both`) compatible with source modality. Audio/script evidence cannot prove a current visual state. Missing visual or narration evidence is listed separately. Write purpose, exact spoken text (empty for silence), visual direction, and an explicit audio/visual alignment rationale. Reference evidence ranges covering every claimed operation. Declare `current`, `intended`, or `illustrative`; current claims require verified real evidence, intended states enter the missing-material list. State missing assets in `needs` rather than inventing sources. Editorial visuals must be identified as such; they are not documentary evidence.
- Product-demo requires explicit required operations; podcast-to-video requires spoken text. Neither profile implies a particular length, aspect ratio, voice, existing episode, or rights grant.

Human review remains necessary: compare each spoken assertion with the actual visible state, inspect causal claims (including transitions between independent tools), confirm the alignment rationale, speaking/reading pace, privacy, and rights. Nonempty prose is not semantic proof. Use an unseen/adversarial plan as well as the shipped examples. Revise → validate → independently review → fix → rerun until blocking findings are resolved, or report the exact missing access/authority. Do not loop on optional polish.

## Not shipped

No transcription, automatic screenplay reasoning, semantic fact-checker, waveform/footage inspection, renderer, capture adapter, or delivery certification. Next: explicit timed narration and richer editorial-asset contracts; then source-inspecting adapters and a tiny deterministic renderer with exact-artifact QA. Keep production approval separate from planning validation.
