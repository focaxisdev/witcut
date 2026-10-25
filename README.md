# Witcut

**Cut with intent. Keep the truth.**

An agent skill for making thoughtful product-demo videos from real UI—not just adding motion to screen recordings.

[GitHub](https://github.com/focaxisdev/witcut) · [繁體中文](README.zh-TW.md) · [The skill](skills/witcut/SKILL.md) · [Lessons from production](skills/witcut/examples/production-lessons.md)

## What works today

Witcut is an **instruction-driven production workflow**. It helps an agent plan shots, capture authentic interactions, make motivated editing decisions, review the actual deliverable, and hand off recoverable work using tools available in its environment.

It is **not yet an automatic video editor**, rendering engine, hosted service, or browser-control integration. Loading this skill does not provide those tools or grant access to a computer. The included Python tools validate repository structure and evidence-linked planning data; they do not edit or certify videos.

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

Python 3.9 or newer, standard library only:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

These checks validate the package's frontmatter, local Markdown file links, required structure, and planning-schema invariants (including adversarial inputs and CLI output protection). They cannot establish artistic quality, privacy completeness, licensing, or agent behavior. [Scenario checks](tests/scenarios.md) provide realistic behavioral evaluation tasks and evidence requirements.

## Roadmap—not shipped capabilities

Shipped planning milestone: [shared planning core](skills/witcut/references/planning.md) for product-demo and podcast-to-video profiles, deriving an audiovisual script, machine-readable shot plan, and missing-material list. Synthetic examples are not real media evidence.

1. Timed narration and richer editorial-asset contracts, followed by source-inspecting adapters.
2. Deterministic timeline and render adapters, with small reproducible fixtures.
3. Automated technical checks tied to the exact output artifact.
4. Agent-assisted rough cuts with reviewable decisions and explicit approval boundaries.
5. Broader editing automation, evaluated against real footage and human acceptance.

Automation should preserve the viewer's understanding and the product's truth—not merely produce a playable file.

## Contributing

A useful change demonstrates a real production failure, explains the reusable decision it changes, and includes a bounded scenario or test. Prefer narrow fixes over accumulating rigid rules. Do not submit private account data, recordings, credentials, unlicensed assets, or machine-specific paths.

## Licensing

A license has not been selected. No open-source license grant is declared in this repository yet. Third-party footage, music, fonts, and brand assets are not bundled; any future inclusion requires its own provenance and appropriate rights.
