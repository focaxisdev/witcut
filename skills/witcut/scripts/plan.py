#!/usr/bin/env python3
"""Evidence-linked planning only. Standard library, Python 3.9+. No media execution."""
import argparse
import json
import math
from pathlib import Path

# This strict, executable schema is the format authority. No unknown keys accepted.
SCHEMA = {
    'version': str, 'profile': str,
    'brief': {'revision': str, 'latest_revision': str, 'min_seconds': float, 'max_seconds': float,
              'takeaway': str, 'required_operations': [str]},
    'sources': [{'id': str, 'kind': str, 'duration': float, 'provenance': str,
                 'verification': str, 'rights': str, 'modality': str}],
    'operations': [{'id': str, 'relationship': str, 'predecessors': [str],
                    'source_id': str, 'start': float, 'end': float, 'observation': str, 'omission_reason': str}],
    'scenes': [{'id': str, 'duration': float, 'purpose': str, 'spoken': str,
                'visual': str, 'alignment': str, 'claim_state': str,
                'operation_ids': [str], 'evidence': [{'source_id': str, 'start': float, 'end': float, 'role': str}],
                'needs': [str]}],
}


def shape(value, schema, path='$'):
    errors = []
    if isinstance(schema, dict):
        if not isinstance(value, dict):
            return [f'{path}: expected object']
        for key in sorted(set(value) - set(schema)):
            errors.append(f'{path}.{key}: unknown field')
        for key, field in schema.items():
            if key not in value:
                errors.append(f'{path}.{key}: required field')
            else:
                errors.extend(shape(value[key], field, f'{path}.{key}'))
    elif isinstance(schema, list):
        if not isinstance(value, list):
            return [f'{path}: expected array']
        for i, item in enumerate(value):
            errors.extend(shape(item, schema[0], f'{path}[{i}]'))
    elif schema is float:
        try:
            finite = type(value) in (int, float) and math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            errors.append(f'{path}: expected finite number (not boolean)')
    elif not isinstance(value, schema):
        errors.append(f'{path}: expected {schema.__name__}')
    return errors


def validate(plan):
    errors = shape(plan, SCHEMA)
    missing = []
    if errors:
        return errors, missing
    def require(condition, message):
        if not condition:
            errors.append(message)
    def unique(items, label):
        ids = [x['id'] for x in items]
        require(all(x.strip() for x in ids), f'{label}: empty ID')
        require(len(set(ids)) == len(ids), f'{label}: duplicate IDs')
        return {x['id']: x for x in items}
    sources = unique(plan['sources'], 'sources')
    operations = unique(plan['operations'], 'operations')
    unique(plan['scenes'], 'scenes')
    require(plan['version'] == '1', 'unsupported version')
    require(plan['profile'] in ('product-demo', 'podcast-to-video'), 'unknown profile')
    brief = plan['brief']
    require(bool(brief['revision'].strip()) and brief['revision'] == brief['latest_revision'], 'brief: not latest revision')
    require(bool(brief['takeaway'].strip()), 'brief: takeaway required')
    require(0 <= brief['min_seconds'] <= brief['max_seconds'] and brief['max_seconds'] > 0, 'brief: invalid duration bounds')
    duration = sum(s['duration'] for s in plan['scenes'])
    require(bool(plan['scenes']), 'scenes: must not be empty')
    require(brief['min_seconds'] <= duration <= brief['max_seconds'], 'timeline: duration outside latest brief')
    for source in plan['sources']:
        sid = source['id']
        require(source['modality'] in ('audio', 'visual', 'audiovisual', 'script'), f'{sid}: unknown source modality')
        require(source['kind'] in ('real', 'editorial', 'synthetic-fixture'), f'{sid}: unknown source kind')
        require(source['verification'] in ('verified', 'unverified', 'fixture'), f'{sid}: unknown verification')
        require(source['rights'] in ('cleared', 'unknown', 'fixture-only'), f'{sid}: unknown rights')
        require(source['duration'] > 0 and bool(source['provenance'].strip()), f'{sid}: duration/provenance required')
        if source['kind'] == 'synthetic-fixture':
            require(source['verification'] == 'fixture' and source['rights'] == 'fixture-only', f'{sid}: fixture cannot claim real verification/rights')
        else:
            require(source['verification'] != 'fixture' and source['rights'] != 'fixture-only', f'{sid}: production source cannot use fixture status')
    def evidence(ref, context):
        source = sources.get(ref['source_id'])
        if not source:
            require(False, f'{context}: unknown source {ref["source_id"]}')
            missing.append({'context': context, 'need': f'source {ref["source_id"]}'})
            return None
        require(0 <= ref['start'] < ref['end'] <= source['duration'], f'{context}: invalid source range')
        for field, allowed in [('verification', ('verified', 'fixture')), ('rights', ('cleared', 'fixture-only'))]:
            if source[field] not in allowed:
                missing.append({'context': context, 'need': f'{source["id"]}: {field}'})
        return source
    for op in plan['operations']:
        oid = op['id']
        require(op['relationship'] in ('independent', 'sequential'), f'{oid}: unknown relationship')
        require(bool(op['observation'].strip()), f'{oid}: observation required')
        require(len(op['predecessors']) == len(set(op['predecessors'])), f'{oid}: duplicate predecessors')
        if op['relationship'] == 'independent':
            require(not op['predecessors'], f'{oid}: independent operation cannot have predecessors')
        else:
            require(bool(op['predecessors']), f'{oid}: sequential operation needs predecessors')
        for pred in op['predecessors']:
            require(pred in operations and pred != oid, f'{oid}: invalid predecessor {pred}')
            if pred in operations and operations[pred]['source_id'] == op['source_id']:
                require(operations[pred]['end'] <= op['start'], f'{oid}: predecessor occurs after operation')
        evidence(op, oid)
    # Graph validation independent of scene ordering.
    visiting, visited = set(), set()
    def visit(oid):
        if oid in visiting:
            require(False, f'{oid}: dependency cycle')
            return
        if oid in visited or oid not in operations:
            return
        visiting.add(oid)
        for pred in operations[oid]['predecessors']:
            visit(pred)
        visiting.remove(oid)
        visited.add(oid)
    for oid in operations:
        visit(oid)
    shown = set()
    for scene in plan['scenes']:
        sid = scene['id']
        require(scene['duration'] > 0, f'{sid}: duration must be positive')
        for field in ('purpose', 'visual', 'alignment'):
            require(bool(scene[field].strip()), f'{sid}: {field} required')
        require(scene['claim_state'] in ('current', 'intended', 'illustrative'), f'{sid}: unknown claim state')
        refs = [evidence(ref, sid) for ref in scene['evidence']]
        visuals = []
        for ref, source in zip(scene['evidence'], refs):
            require(ref['role'] in ('narration', 'visual', 'both'), f'{sid}: unknown evidence role')
            if source:
                if ref['role'] in ('visual', 'both'):
                    require(source['modality'] in ('visual', 'audiovisual'), f'{sid}: visual evidence needs visual source')
                    visuals.append(source)
                if ref['role'] in ('narration', 'both'):
                    require(source['modality'] in ('audio', 'audiovisual', 'script'), f'{sid}: narration evidence needs audio/script source')
        if not visuals:
            missing.append({'context': sid, 'need': 'visual evidence or explicit editorial asset'})
        if scene['spoken'].strip() and not any(r['role'] in ('narration', 'both') for r in scene['evidence']):
            missing.append({'context': sid, 'need': 'narration source/recording'})
        if scene['claim_state'] == 'current':
            require(bool(visuals) and all(s['kind'] == 'real' and s['verification'] == 'verified' for s in visuals), f'{sid}: current claim needs verified real evidence for visuals')
        if not scene['evidence']:
            missing.append({'context': sid, 'need': 'visual/audio supporting evidence'})
        if scene['claim_state'] == 'intended':
            missing.append({'context': sid, 'need': 'capture/verify intended state before presenting as current'})
        for need in scene['needs']:
            require(bool(need.strip()), f'{sid}: empty material need')
            missing.append({'context': sid, 'need': need})
        for oid in scene['operation_ids']:
            require(oid in operations, f'{sid}: unknown operation {oid}')
            if oid not in operations:
                continue
            op = operations[oid]
            require(set(op['predecessors']) <= shown, f'{sid}: sequential predecessor not shown earlier')
            require(any(r['source_id'] == op['source_id'] and r['start'] <= op['start'] and r['end'] >= op['end'] for r in scene['evidence']), f'{sid}: operation {oid} not covered by scene evidence')
            shown.add(oid)
    for oid, op in operations.items():
        require(oid in shown or bool(op['omission_reason'].strip()), f'{oid}: omitted operation requires explicit rationale')
        require(oid not in shown or not op['omission_reason'].strip(), f'{oid}: shown operation cannot carry omission rationale')
    require(set(brief['required_operations']) <= set(operations), 'brief: required operation undefined')
    require(set(brief['required_operations']) <= shown, 'timeline: required operation omitted')
    if plan['profile'] == 'product-demo':
        require(bool(brief['required_operations']), 'product-demo: required operations must be explicit')
    if plan['profile'] == 'podcast-to-video':
        require(any(s['spoken'].strip() for s in plan['scenes']), 'podcast-to-video: spoken script required')
    return errors, missing


def artifacts(plan):
    errors, missing = validate(plan)
    if errors:
        raise ValueError('\n'.join(errors))
    lines = [f'# Audiovisual script — {plan["profile"]}', '',
             f'Brief: {plan["brief"]["revision"]} · {plan["brief"]["takeaway"]}', '',
             '**Planning only. Evidence/rights statuses are supplied assertions, not independently certified.**', '']
    cursor = 0
    shots = []
    for scene in plan['scenes']:
        shot = dict(scene, timeline_start=cursor, timeline_end=cursor + scene['duration'])
        shots.append(shot)
        lines.extend([f'## {scene["id"]} · {cursor:g}–{cursor + scene["duration"]:g}s · {scene["claim_state"]}',
                      f'Purpose: {scene["purpose"]}', f'Audio: {scene["spoken"] or "[silent]"}',
                      f'Visual: {scene["visual"]}', f'Alignment: {scene["alignment"]}',
                      'Evidence: ' + (', '.join(f'{r["source_id"]} {r["start"]:g}–{r["end"]:g}s ({r["role"]})' for r in scene['evidence']) or '[missing]'), ''])
        lines.append('Operations: ' + (', '.join(scene['operation_ids']) or '[none]'))
        cursor += scene['duration']
    lines.extend(['', '## Operation inventory'])
    for op in plan['operations']:
        lines.append(f'- {op["id"]}: {op["observation"]} | {op["relationship"]}; predecessors: {", ".join(op["predecessors"]) or "none"}; omission: {op["omission_reason"] or "included"}')
    lines.extend(['', '## Source declarations (not independently certified)'])
    for source in plan['sources']:
        lines.append(f'- {source["id"]}: {source["kind"]}/{source["modality"]}; {source["verification"]}; rights: {source["rights"]}. {source["provenance"]}')
    lines.extend(['', '## Missing materials'])
    lines.extend(f'- {item["context"]}: {item["need"]}' for item in missing)
    return '\n'.join(lines), dict(plan, scenes=shots, planning_only=True), {'items': missing, 'production_ready': False, 'note': 'Planning checks do not certify media, rights, semantic alignment, or production readiness.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--out', type=Path, help='New output directory (will not overwrite existing work)')
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding='utf-8'))
        errors, missing = validate(plan)
        if errors:
            print(json.dumps({'errors': errors, 'missing_materials': missing}, indent=2, ensure_ascii=False))
            return 1
        if args.out:
            script, shots, materials = artifacts(plan)
            args.out.mkdir(parents=True, exist_ok=False)
            (args.out / 'script.md').write_text(script, encoding='utf-8')
            for name, data in [('shot-plan.json', shots), ('missing-materials.json', materials)]:
                (args.out / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f'PASS: planning invariants; {len(missing)} missing-material item(s). Not production certification.')
        return 0
    except (OSError, ValueError, RecursionError) as exc:
        print(f'ERROR: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
