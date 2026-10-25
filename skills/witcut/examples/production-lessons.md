# Lessons from a real-UI demo

These anonymized cases describe production failure patterns, not bundled footage or independently reproducible benchmark results. Numerical settings are examples, not defaults.

| Observed problem | Decision that changed the result | Transferable lesson |
| --- | --- | --- |
| Three independent modes were narrated as a sequence | Rebuilt the story around alternatives and verified each input/result relationship | Validate semantics before writing the script |
| UI still appeared small after increasing output resolution | Tested actual browser zoom and UI proportion at delivery size | Pixels and apparent size are different variables |
| A circular control was awkwardly cropped during a zoom, although endpoints looked acceptable | Reviewed intermediate compositions and used a same-state result insert where a continuous move failed | Review the path, not just its ends |
| Decorative zoom distracted from an otherwise clear operation | Removed the move | No movement is better than unmotivated movement |
| A short opening did not communicate an aerial feel | Added real camera motion and settling time | More genuine action, not static padding |
| A selected location was presented without showing the remaining orientation and focal adjustment | Captured those actual UI actions and held the final view | Do not turn manual work into implied automation |
| An encoded frame rate looked adequate while source captures were sparse | Distinguished source timestamps/cadence from output fps | Metadata is not motion evidence |
| A player failed downstream of decoding | The intended external output device resolved local playback | Device routing and file integrity require separate diagnosis |
| A later export had an audio stream but lacked intended signal | Rebuilt audio for that exact export and checked it separately | Earlier audio success does not validate a new artifact |
| A technical pass coexisted with a composition defect | Kept technical and art decisions separate | Encoder success is not artistic readiness |
| An owner requested one final inspection, not another edit | Reported minor polish opportunities without changing the accepted file | Review-only and frozen are real boundaries |
| A design archive passed hash checks but omitted required media/runtime assumptions | Documented external dependencies and limited restoration claims | Integrity is not reproducibility |

In one brief, 150% browser zoom, internal 4K production, 1080p delivery, and a runtime beyond one minute were appropriate. A different product, layout, audience, or destination may need none of them. Reuse the reasoning, not the constants.
