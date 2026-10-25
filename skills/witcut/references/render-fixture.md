# One executable synthetic pilot

Use this only to exercise the planning-to-output boundary. It is not product footage, a captured manual interaction, a Podcast adaptation, or production approval.

From the repository root, with Python 3.9+, FFmpeg supporting `libx264`, `aac`, `flite`, `drawtext`, `drawbox`, FFprobe, and `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`:

```sh
python3 skills/witcut/scripts/render_fixture.py --out /tmp/witcut-pilot
python3 skills/witcut/scripts/render_fixture.py --execution /tmp/witcut-pilot/execution.json --out /tmp/witcut-replay
```

Both output directories must be new. No network, desktop, paid service, uploaded private recording, or downloaded footage is used. All generated media stays in the requested directory, outside the repository. The script fails with the exact missing runtime dependency instead of replacing speech with silence.

## What the viewer should understand

“In this synthetic test, only pressing Apply causes the green result; nothing runs automatically.” The original spoken text retains both the condition and the rejection of automation. The graphic is labeled synthetic throughout: a simulated pointer moves at 4–6 seconds, a simulated press is highlighted at 6–6.5, and the result turns green at 6.5. This demonstrates an editorial fixture, not that a real product or user behaved this way. There is no claim of observed real UI behavior.

The narration is synthesized locally from original text with FFmpeg's bundled `flite` `slt` voice. `provenance.json` records that origin, runtime and font identity. Using an installed runtime is not a new licensing decision or certification of publication rights. Outputs remain private task artifacts.

## One mapping authority, one adapter

`plan-v2.json` is validated by the shared planning core. Its one illustrative scene contains a required simulated operation, a visual reference, and a narration reference. Evidence uses the same `start`, `end`, `output_start`, `output_end`, `role`, and `playback` fields as the planning core. Output coordinates in the plan are scene-local; the projection adds the scene cursor to produce absolute execution coordinates.

`execution.json` binds that exact plan and resolved media to SHA-256 identities. The adapter checks the plan hash, validates the plan, regenerates its projection, and rejects stale or different execution mappings. It checks actual media duration/modality against the declarations and source hashes before rendering. A changed plan requires revalidation and a new projection; silently editing only the execution times fails.

The adapter deliberately accepts only this bounded contract: one twelve-second scene, one continuous visual source, one audio narration clip, and explicit 1× playback. It refuses holds, references, speed changes, missing ranges and unsupported roles rather than guessing. The planning schema remains separate from codec settings and filesystem resolution. Adding this single adapter did not require the planner to become a renderer or a generic multitrack framework.

## Evidence and remaining review

Outputs include the exact `candidate.mp4`, full-decode and signal findings in `qa.json`, and three navigation PNGs. Technical checks require twelve seconds, 288 video frames at 24 fps, one video stream and one audio stream, full decoding, and a finite nonzero audio peak. The integration tests also re-render the same saved sources and manifest and compare candidate bytes in the current runtime. Runtime and encoder changes may change bytes; matching hashes in one runtime do not prove cross-version determinism.

The PNGs do not prove normal-speed viewing, and nonzero signal does not prove intelligibility. Generated QA records normal-speed viewing, listening and audience-goal acceptance as **not tested**. An actual reviewer must play and listen to that exact candidate, check the conditional meaning, action/result order, pace and speech clarity, and record time-based defects. If playback or listening is unavailable, report that concrete blocker; do not call the pilot accepted. Use the shared [collaboration loop](collaboration.md) and [candidate review](qa.md) for correction and stopping conditions.
