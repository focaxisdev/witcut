#!/usr/bin/env python3
"""Validate Witcut's portable package, not its creative or runtime behavior."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

REQUIRED = (
    'README.md', 'README.zh-TW.md', 'skills/witcut/SKILL.md',
    'skills/witcut/references/art-direction.md',
    'skills/witcut/references/capture.md',
    'skills/witcut/references/qa.md',
    'skills/witcut/references/handoff.md',
    'skills/witcut/examples/production-lessons.md',
)
LINK = re.compile(r'\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"\n]*")?\)')


def validate(root):
    root = Path(root).resolve()
    errors = []
    for relative in REQUIRED:
        if not (root / relative).is_file():
            errors.append(f'Missing file: {relative}')
    entry = root / 'skills/witcut/SKILL.md'
    if entry.is_file():
        text = entry.read_text(encoding='utf-8')
        match = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.S)
        if not match:
            errors.append('SKILL.md: missing YAML frontmatter delimiters')
        else:
            # This package deliberately uses plain one-line YAML fields.
            fields = {}
            for line in match.group(1).splitlines():
                if not re.match(r'^[a-z][a-z-]*: .+$', line):
                    errors.append('SKILL.md: expected plain one-line frontmatter fields')
                    continue
                key, value = line.split(': ', 1)
                if key in fields:
                    errors.append(f'SKILL.md: duplicate field {key}')
                fields[key] = value
            if fields.get('name') != 'witcut':
                errors.append('SKILL.md: name must match skill folder witcut')
            if not fields.get('description', '').strip():
                errors.append('SKILL.md: description is required')
    for page in sorted(root.rglob('*.md')):
        for target in LINK.findall(page.read_text(encoding='utf-8')):
            url = urlsplit(target.strip('<>'))
            if url.scheme or url.netloc or not url.path:
                continue
            dest = (page.parent / unquote(url.path)).resolve()
            if not dest.is_relative_to(root):
                errors.append(f'{page.relative_to(root)}: link escapes package: {target}')
            elif not dest.is_file():
                errors.append(f'{page.relative_to(root)}: missing link target: {target}')
    return errors


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    errors = validate(root)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        raise SystemExit(1)
    print('PASS: required files, plain frontmatter, and local Markdown file links')
    print('Not checked: link anchors, external URLs, video quality, rights, privacy, or agent behavior')
