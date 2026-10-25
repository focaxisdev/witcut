# Witcut

**Cut with intent. Keep the truth.**

An agent skill for making thoughtful product-demo videos from real UI—not just adding motion to screen recordings.

[GitHub](https://github.com/focaxisdev/witcut) · [繁體中文](README.zh-TW.md) · [The skill](skills/witcut/SKILL.md) · [Lessons from production](skills/witcut/examples/production-lessons.md)

## What works today

This branch contains three distinct capabilities:

| Component | Available now | Boundary |
| --- | --- | --- |
| Agent skill | Guidance for planning, capture, editing decisions, candidate review and handoff | Uses the agent's existing authorized tools; grants no computer access |
| Python planner | Shared product-demo / podcast-to-video schema v2, source-to-output timing, validation and three derived planning files | Does not inspect media, judge meaning or certify production readiness |
| Optional FFmpeg fixture adapter | Generates and reproduces one original, explicitly synthetic test video with speech | Not real UI capture, a general editor or a Podcast adaptation; normal-speed viewing and listening remain unverified |

Autonomous story generation, media understanding and general editing are future work. The [collaboration strategy](skills/witcut/references/collaboration.md) covers available model/reasoning choices and bounded role handoffs; viewer understanding remains the final acceptance check.

## Five-minute quickstart: Python only

This quickstart targets `planning-loop-v1` in [Draft PR #1](https://github.com/focaxisdev/witcut/pull/1), not a claim that it is merged into `main`. Use Python 3.9+ and a POSIX shell; no pip packages, FFmpeg, account credentials or media files are needed after checkout.

```sh
git clone --branch planning-loop-v1 --single-branch https://github.com/focaxisdev/witcut.git
cd witcut
python3 scripts/validate.py
work_dir=$(mktemp -d)
python3 skills/witcut/scripts/plan.py skills/witcut/examples/plans/product-demo.json --out "$work_dir/product-demo"
python3 skills/witcut/scripts/plan.py skills/witcut/examples/plans/podcast-to-video.json --out "$work_dir/podcast-to-video"
python3 - "$work_dir" <<'PYTHON'
import json
from pathlib import Path
import sys
for profile in ('product-demo', 'podcast-to-video'):
    folder = Path(sys.argv[1]) / profile
    assert {p.name for p in folder.iterdir()} == {'script.md', 'shot-plan.json', 'missing-materials.json'}
    shots = json.loads((folder / 'shot-plan.json').read_text())
    missing = json.loads((folder / 'missing-materials.json').read_text())
    assert shots['planning_only'] is True
    assert missing['production_ready'] is False and len(missing['items']) == 4
    print(profile, 'planning_only=True; production_ready=False; missing=4', folder)
PYTHON
```

Inputs are the two original synthetic JSON plans, not real footage or private radio content. Each CLI call prints `PASS` with **4 missing-material items** and creates:

- `script.md`: human-readable audiovisual script.
- `shot-plan.json`: scene coordinates and evidence mappings; `planning_only: true`.
- `missing-materials.json`: outstanding recordings/visuals or source checks; `production_ready: false`.

Missing materials are expected, not a failed quickstart. `PASS` means planning invariants passed, not that a video exists or its meaning, rights or quality are verified. Output directories must be new; rerun the `mktemp` command for another attempt. See the [planning contract](skills/witcut/references/planning.md) for the format.

## Why it exists

A technically clean video can still tell the wrong story. A high-resolution capture can still have unreadable controls. A smooth zoom can still crop out the information that matters.

Witcut turns those production lessons into reusable decisions:

- **Truth before transitions:** independent modes stay independent; manual work is not presented as automation.
- **Purpose before motion:** decide what the viewer must notice, then compose the beginning, path, and end of the move.
- **Readability before pixel count:** distinguish browser zoom, viewport, pixel density, capture resolution, and delivery resolution.
- **Understanding before arbitrary duration:** hold meaningful actions and outcomes long enough to read them.
- **Evidence before confidence:** separate technical integrity, artistic judgment, listening, playback-device behavior, and owner acceptance.
- **Finish without endless polishing:** respect review-only requests and frozen cuts; preserve a precise delivery candidate.

## Use it

Copy the entire `skills/witcut` folder into the skill directory supported by your agent. Keep its references and examples together. For agents without skill discovery, give the agent `skills/witcut/SKILL.md` as the workflow entrypoint and allow it to read the linked files as needed.

No platform-specific installer is required. Tool access, capture permissions, media rights, and publishing authorization remain separate.

Example requests:

> Use Witcut to plan a real-UI demo of this product. Inspect how its modes actually relate before writing the story. Propose a short pilot before the full capture.

> Use Witcut to review this encoded draft. The circular control feels awkward during the zoom. Report timestamped findings; do not modify any files.

> Use Witcut to package this approved cut for handoff. Include only the authorized design sources, list excluded media dependencies, and report which restoration checks you actually performed.

Bring the current brief, product or footage access, intended audience, delivery destination, approved assets, and any frozen-version boundaries. Missing access should produce a specific blocker—not a fabricated inspection.

## The workflow

`Brief → real behavior → visual pilot → capture → edit → bounded review → freeze → handoff`

Read only the reference needed for the current stage:

| Reference | Decision it supports |
| --- | --- |
| [Art direction](skills/witcut/references/art-direction.md) | Story, motivated zoom, composition, timing |
| [Capture](skills/witcut/references/capture.md) | UI scale, real motion, timestamps, truthful sources |
| [QA](skills/witcut/references/qa.md) | Exact-candidate review, audio, stopping conditions |
| [Handoff](skills/witcut/references/handoff.md) | Frozen cuts, delivery identity, honest recovery |

The workflow does not prescribe 16:9, 4K, 150% zoom, silent audio, a one-minute limit, or a particular outro. Those are brief-specific choices.

## Development and validation

The pure Python CI job runs only the following explicit package/planner scope (Python 3.9+, standard library):

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -p 'test_validate.py' -v
python3 -m unittest discover -s tests -p 'test_plan.py' -v
```

Renderer integration is a separate optional check:

```sh
python3 -m unittest discover -s tests -p 'test_render_fixture.py' -v
```

It requires FFmpeg/libflite, FFprobe and the fixture font described in the [synthetic pilot](skills/witcut/references/render-fixture.md). Read the actual unittest summary: missing dependencies produce `skipped`, which is not renderer acceptance. The pure Python CI job does not run or certify the renderer. Neither technical integration tests nor sampled PNGs establish actual viewing, listening or audience acceptance.

These checks validate the package's frontmatter, local Markdown file links, required structure, and planning-schema invariants (including adversarial inputs and CLI output protection). They cannot establish artistic quality, privacy completeness, licensing, or agent behavior. [Scenario checks](tests/scenarios.md) provide realistic behavioral evaluation tasks and evidence requirements.

## Roadmap—not shipped capabilities

1. Validate the original synthetic pilot through actual viewing and listening, then extend only where a demonstrated failure requires it.
2. Extend the single fixture adapter only for a demonstrated production need; broad editing automation remains unshipped.
3. Production QA beyond the fixed fixture, tied to exact output artifacts.
4. Agent-assisted rough cuts with reviewable decisions and explicit approval boundaries.
5. Broader editing automation, evaluated against real footage and human acceptance.

Automation should preserve the viewer's understanding and the product's truth—not merely produce a playable file.

## Contributing

A useful change demonstrates a real production failure, explains the reusable decision it changes, and includes a bounded scenario or test. Prefer narrow fixes over accumulating rigid rules. Do not submit private account data, recordings, credentials, unlicensed assets, or machine-specific paths.

## Licensing

A license has not been selected. No open-source license grant is declared in this repository yet. Third-party footage, music, fonts, and brand assets are not bundled; any future inclusion requires its own provenance and appropriate rights.
