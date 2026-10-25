# QA: conclusions stop where evidence stops

Read for encoded drafts, playback problems, or review-only requests.

## Identify the candidate first

Record the candidate filename/version and, where practical, byte count and SHA-256. Tie every review to it. A prior version's passing report does not validate a new export. Inspect the file that will actually be delivered, not a similarly named intermediate or a stale preview.

If viewing a cached or remotely hosted preview, verify which asset/revision it serves before attributing an old defect to the current file. Do not dismiss an owner's report as cache without evidence.

## Separate three decisions

| Track | Evidence | Status vocabulary |
| --- | --- | --- |
| Technical | Metadata, full decode, source/output timing, boundary checks | pass / hold / not tested |
| Narrative and art | Normal-speed viewing, timestamped composition and comprehension findings | pass / hold / optional polish / not tested |
| Owner acceptance | Actual response concerning this candidate | pending / approved / frozen |

Check duration, dimensions, codec/pixel format as relevant to delivery, frame count/timing, corruption, truncation, first/last frames, and transitions. A contact sheet helps navigation but cannot prove normal-speed motion or all-frame integrity. Use systematic trajectory checks for automated crops when feasible.

Do not call a technically clean but misleading film ready. An independent review is useful for a consequential creative decision; supply the actual cut and brief, not a desired verdict. If no independent or visual inspection occurred, state that limitation. Avoid unsupported numerical perfection scores.

## Audio: six separate layers

1. **Structure:** stream exists and decodes.
2. **Signal:** nonzero intended audio exists through appropriate portions, rather than an empty track.
3. **Edit:** intended duration, alignment, transitions, clipping, and ending.
4. **Listening:** the actual file was audibly monitored; speech/music fit and comfort were assessed.
5. **Playback device:** application output route, system device, external DAC or other endpoint behaves correctly.
6. **Rights:** exact source and applicable usage terms are recorded.

Do not infer the source codec from a decoded PCM stage in an error dialog. When possible, compare the exact file in a known working playback path before changing encodes. A device-specific failure may require choosing the intended output device rather than re-rendering. Conversely, a fixed device cannot prove the next export contains valid audio.

Never claim listening from a waveform, successful decode, or signal metric. Report those as signal checks. An automated platform copyright check is not a substitute for rights provenance. Do not bundle a music file merely because its use in one video is permitted.

## Review report

Use a compact record:

```text
Candidate: filename + version (+ hash when available)
Scope: review only / authorized revision / delivery check
Checked: observations and methods actually performed
Findings: time range — defect — viewer impact — smallest correction
Technical: pass / hold / not tested
Narrative/art: pass / hold / optional polish / not tested
Owner: pending / approved / frozen
Untested or blocked: concrete limitation
Next action: bounded step, or stop with no change
```

## Repair and stop

Use the [shared loop contract](collaboration.md) for bounded local fixes, escalation, and stopping. Mark obsolete QA as belonging to its old candidate; do not silently reuse it.

Review-only means no source edits, re-exports, or metadata changes. For a frozen cut, report optional polish separately and leave the file unchanged. Do not reopen the entire production pipeline because a nonblocking improvement is conceivable.

The review loop must report any required check that could not run. Owner acceptance remains distinct from reviewer confidence.
