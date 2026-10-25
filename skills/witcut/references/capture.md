# Capture: preserve the evidence

Read before recording or when UI readability and motion are in doubt.

## Six settings that are not interchangeable

| Setting | What it changes | What it does not prove |
| --- | --- | --- |
| Browser zoom | Layout and apparent control/text size | Capture quality or viewer legibility |
| CSS viewport | Available layout space | Physical capture dimensions |
| Device pixel ratio (DPR) | Pixel density relative to CSS units | Browser zoom or a larger UI proportion |
| Capture resolution | Recorded detail | Readable controls in the final frame |
| Editorial crop/scale | Attention and subject size | Native product camera/focal changes |
| Delivery resolution | Final raster size | Original-source resolution |

Downsampling a full 4K frame to 1080p preserves the UI's relative size. If controls occupy too little of the composition, increasing resolution alone does not solve it. Test real browser zoom or a justified crop and inspect layout changes; do not merely set DPR and call it browser zoom.

## Pilot checklist

Record a short representative action before a long take. Verify the actual delivered-size view:

- Relevant labels and controls are readable without pausing or magnifying the player.
- The desired mode, inputs, and result are present; temporary state from an earlier take is not leaking in.
- Browser chrome, pointer, notifications, account details, and unrelated data are handled appropriately.
- The native page remains spatially coherent; attribution remains visible when required.
- Capture timestamps and source identity are recorded.
- Animation and audio are checked through the intended output path as available.

Use an authorized test/demo environment where appropriate. Do not alter product behavior or production records without permission. Respect background-only operation and disconnection boundaries; if the capture environment is unavailable, prepare the plan and report the blocked capture instead.

## Timing and genuine animation

Keep untrimmed source recordings where authorized, with action timestamps and take identifiers. For image-sequence capture, retain capture timestamps and account for irregular intervals rather than assuming every image arrived on time.

Distinguish:

1. Source sampling cadence and missing/repeated frames.
2. Reconstruction/playback timing.
3. Encoded output fps and frame count.
4. Perceived smoothness during normal-speed viewing.

An output labeled 25 fps can contain repeated images from a much slower capture. Correct timestamps can preserve speed but cannot recover motion never sampled. Do not claim native fluid capture from metadata alone. If capture cadence is inadequate for the intended movement, change the capture approach or simplify the shot, not just its output fps.

Record actual orientation, zoom, focal-length, or other native adjustments when they demonstrate the feature. Editorial scale changes are not equivalent to those actions.

## Source record

For each selected take keep source filename/identifier, dimensions, timing basis, observed mode/state, essential action times, and known limitations. Separate rejected or wrong-state takes from selectable footage. For mixed-resolution sources, disclose upscaling rather than labeling all footage native to the master resolution.

Use authorized original brand assets and font provenance. Confirm font rendering; missing fonts can silently alter an SVG or lockup. Record tool versions and relative source references without bundling credentials, profiles, or private account data.
