#!/usr/bin/env python3
"""One local FFmpeg adapter and original synthetic fixture; no capture or publishing."""
import argparse
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path
import shutil
import subprocess

DURATION = 12.0
NARRATION = 'Only after you press Apply does this test turn green. It does not run automatically.'
FONT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr[-3000:] or 'Command failed')
    return result.stdout, result.stderr


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)])[0])


def ffmpeg(args):
    return run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n', *map(str, args)])


def exact_keys(value, expected, context):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f'{context}: missing or unsupported fields')


def validate_manifest(manifest, root):
    """This adapter intentionally supports two 1x clips, not a generic timeline."""
    exact_keys(manifest, ('version', 'duration', 'plan', 'sources', 'clips'), 'manifest')
    if manifest['version'] != 'fixture-1' or manifest['duration'] != DURATION:
        raise ValueError('Unsupported version/duration')
    if not isinstance(manifest['sources'], list) or len(manifest['sources']) != 2:
        raise ValueError('Exactly two sources required')
    if not isinstance(manifest['clips'], list) or len(manifest['clips']) != 2:
        raise ValueError('Exactly two clips required')
    exact_keys(manifest['plan'], ('path', 'sha256'), 'plan identity')
    if not isinstance(manifest['plan']['path'], str):
        raise ValueError('Invalid plan path')
    plan_path = (root / manifest['plan']['path']).resolve()
    if not plan_path.is_relative_to(root.resolve()) or not plan_path.is_file() or sha(plan_path) != manifest['plan']['sha256']:
        raise ValueError('Missing, external, or changed plan')
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    if manifest['clips'] != project(plan):
        raise ValueError('Execution mapping differs from plan projection')
    resolved = {}
    for source in manifest['sources']:
        exact_keys(source, ('id', 'path', 'sha256', 'duration', 'modality'), 'source')
        sid = source['id']
        if not isinstance(sid, str) or not sid or sid in resolved:
            raise ValueError('Invalid/duplicate source ID')
        if type(source['duration']) not in (int, float) or not math.isfinite(source['duration']) or source['duration'] <= 0:
            raise ValueError('Invalid source duration')
        if not isinstance(source['path'], str):
            raise ValueError('Invalid source path')
        path = (root / source['path']).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file() or sha(path) != source['sha256']:
            raise ValueError('Missing, external, or changed source')
        info = probe(path)
        if abs(float(info['format']['duration']) - source['duration']) > 0.05:
            raise ValueError('Source duration declaration differs from media')
        stream_type = {'visual': 'video', 'audio': 'audio'}.get(source['modality'])
        if stream_type is None or not any(s['codec_type'] == stream_type for s in info['streams']):
            raise ValueError('Source modality differs from media')
        declaration = next((s for s in plan['sources'] if s['id'] == sid), None)
        if declaration is None or declaration['duration'] != source['duration'] or declaration['modality'] != source['modality']:
            raise ValueError('Resolved source differs from planning declaration')
        resolved[sid] = (source, path)
    roles = set()
    for clip in manifest['clips']:
        exact_keys(clip, ('source_id', 'start', 'end', 'output_start', 'output_end', 'role', 'playback'), 'clip')
        if clip['source_id'] not in resolved or clip['role'] in roles:
            raise ValueError('Missing source or duplicate role')
        roles.add(clip['role'])
        source, _ = resolved[clip['source_id']]
        for field in ('start', 'end', 'output_start', 'output_end'):
            if type(clip[field]) not in (float, int) or not math.isfinite(clip[field]):
                raise ValueError('Finite numeric timing required')
        if not 0 <= clip['start'] < clip['end'] <= source['duration']:
            raise ValueError('Source range outside media')
        if not 0 <= clip['output_start'] < clip['output_end'] <= DURATION:
            raise ValueError('Output range outside timeline')
        if clip['playback'] != 'play' or abs((clip['end'] - clip['start']) - (clip['output_end'] - clip['output_start'])) > 1e-6:
            raise ValueError('Only explicit 1x play mapping supported')
        if (clip['role'], source['modality']) not in (('visual', 'visual'), ('narration', 'audio')):
            raise ValueError('Unsupported role/modality')
        if clip['role'] == 'visual' and (clip['output_start'] != 0 or clip['output_end'] != DURATION):
            raise ValueError('Visual clip must cover the whole fixture')
    if roles != {'visual', 'narration'}:
        raise ValueError('Visual and narration required')
    return resolved


def project(plan):
    """Validate planning v2 then project scene-local evidence to absolute output time."""
    spec = importlib.util.spec_from_file_location('witcut_plan', Path(__file__).with_name('plan.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors, missing = module.validate(plan)
    if errors or missing:
        raise ValueError(f'Plan is not executable: {errors}; missing: {missing}')
    if len(plan['scenes']) != 1 or sum(s['duration'] for s in plan['scenes']) != DURATION:
        raise ValueError('Fixture adapter supports one twelve-second scene')
    if any(s['kind'] != 'synthetic-fixture' for s in plan['sources']):
        raise ValueError('Fixture adapter requires clearly labeled synthetic test sources')
    clips = []
    cursor = 0.0
    for scene in plan['scenes']:
        for ref in scene['evidence']:
            clips.append(dict(ref, output_start=cursor + ref['output_start'], output_end=cursor + ref['output_end']))
        cursor += scene['duration']
    return clips


def render(manifest, root, destination):
    resolved = validate_manifest(manifest, root)
    visual = next(c for c in manifest['clips'] if c['role'] == 'visual')
    audio = next(c for c in manifest['clips'] if c['role'] == 'narration')
    vf = f"[0:v]trim=start={visual['start']}:end={visual['end']},setpts=PTS-STARTPTS[v]"
    af = (f"[1:a]atrim=start={audio['start']}:end={audio['end']},asetpts=PTS-STARTPTS,"
          f"adelay={audio['output_start'] * 1000}:all=1,apad,atrim=duration={DURATION}[a]")
    ffmpeg(['-i', resolved[visual['source_id']][1], '-i', resolved[audio['source_id']][1],
            '-filter_complex', vf + ';' + af, '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
            '-r', '24', '-fps_mode', 'cfr', '-c:a', 'aac', '-b:a', '128k', '-t', DURATION, '-map_metadata', '-1',
            '-movflags', '+faststart', destination])


def text_filter(text, y, size=30, enable=None, x='40'):
    value = f"drawtext=fontfile={FONT}:text='{text}':x={x}:y={y}:fontsize={size}:fontcolor=white"
    return value + (f":enable='{enable}'" if enable else '')


def generate(out):
    for executable in ('ffmpeg', 'ffprobe'):
        if not shutil.which(executable):
            raise ValueError(f'Missing {executable}')
    if not FONT.is_file():
        raise ValueError(f'Missing fixture font {FONT}')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'narration.txt').write_text(NARRATION + '\n', encoding='utf-8')
    # Filter text is a fixed original literal, never interpolated from a supplied brief.
    ffmpeg(['-f', 'lavfi', '-i', f"flite=text='{NARRATION}':voice=slt", '-ar', '48000', '-c:a', 'pcm_s16le', out / 'narration.wav'])
    audio_duration = float(probe(out / 'narration.wav')['format']['duration'])
    if audio_duration > DURATION - 1:
        raise ValueError('Generated narration does not fit; do not truncate speech')
    filters = [
        text_filter('SYNTHETIC TEST - SIMULATED ACTION', 30, 28),
        text_filter('Only after pressing Apply does the result change.', 95, 25),
        'drawbox=x=350:y=210:w=240:h=100:color=0x334155:t=fill',
        text_filter('APPLY', 240, 32, x='410'),
        'drawbox=x=350:y=210:w=240:h=100:color=yellow:t=6:enable=between(t,6,6.5)',
        'drawbox=x=650:y=220:w=150:h=80:color=0x64748b:t=fill',
        'drawbox=x=650:y=220:w=150:h=80:color=0x16a34a:t=fill:enable=gte(t,6.5)',
        text_filter('WAITING', 335, 26, 'lt(t,6.5)', x='650'),
        text_filter('RESULT', 335, 26, 'gte(t,6.5)', x='650'),
        text_filter('>', 275, 40, x="'100+320*min(max((t-4)/2,0),1)'"),
        text_filter('Simulated pointer - not recorded user activity', 410, 23),
        text_filter('It does not run automatically.', 460, 25),
    ]
    # Escape expression commas at the filter option level.
    filters = [f.replace('enable=between(t,6,6.5)', "enable='between(t,6,6.5)'").replace('enable=gte(t,6.5)', "enable='gte(t,6.5)'") for f in filters]
    ffmpeg(['-f', 'lavfi', '-i', f'color=c=0x0f172a:s=960x540:r=24:d={DURATION}',
            '-vf', ','.join(filters), '-an', '-c:v', 'libx264', '-preset', 'veryfast',
            '-crf', '18', '-pix_fmt', 'yuv420p', '-map_metadata', '-1', out / 'visual.mp4'])
    sources = []
    for sid, name, modality in [('graphic', 'visual.mp4', 'visual'), ('speech', 'narration.wav', 'audio')]:
        path = out / name
        sources.append(dict(id=sid, path=name, sha256=sha(path), duration=float(probe(path)['format']['duration']), modality=modality))
    evidence = [
        dict(source_id='graphic', start=0.0, end=DURATION, output_start=0.0, output_end=DURATION, role='visual', playback='play'),
        dict(source_id='speech', start=0.0, end=audio_duration, output_start=1.0, output_end=1.0 + audio_duration, role='narration', playback='play'),
    ]
    plan = dict(version='2', profile='product-demo', brief=dict(
        revision='fixture-r1', latest_revision='fixture-r1', min_seconds=DURATION, max_seconds=DURATION,
        takeaway='In this synthetic test, only pressing Apply causes the green result; nothing runs automatically.', required_operations=['press-apply']),
        sources=[dict(id=s['id'], duration=s['duration'], modality=s['modality'], kind='synthetic-fixture',
                      verification='fixture', rights='fixture-only', provenance='Original locally generated synthetic test; no actual product or recorded user activity.') for s in sources],
        operations=[dict(id='press-apply', relationship='independent', predecessors=[], source_id='graphic',
                         start=6.0, end=6.5, observation='Simulated manual Apply press; not observed product behavior.', omission_reason='')],
        scenes=[dict(id='conditional-result', duration=DURATION, purpose='Preserve a conditional explanation with its simulated action and result.',
                     spoken=NARRATION, visual='Labeled synthetic UI; moving simulated pointer, press at six seconds, green result at 6.5 seconds.',
                     alignment='Conditional explanation begins before the simulated press; result follows the press; closing text rejects automation.',
                     claim_state='illustrative', operation_ids=['press-apply'], evidence=evidence, needs=[])])
    plan_path = out / 'plan-v2.json'
    plan_path.write_text(json.dumps(plan, indent=2) + '\n')
    manifest = dict(version='fixture-1', duration=DURATION, plan=dict(path=plan_path.name, sha256=sha(plan_path)), sources=sources, clips=project(plan))
    (out / 'execution.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (out / 'provenance.json').write_text(json.dumps({
        'kind': 'original synthetic test fixture', 'visual': 'Original programmatic graphic; simulated pointer, press at 6s, result at 6.5s; never real UI evidence.',
        'speech': 'Original text synthesized locally using FFmpeg libflite bundled slt voice; no uploaded or downloaded recording.',
        'runtime': run(['ffmpeg', '-version'])[0].splitlines()[0],
        'font': str(FONT), 'font_sha256': sha(FONT),
        'scope': 'Private task output only; no publication, no rights certification.',
    }, indent=2) + '\n')
    render(manifest, out, out / 'candidate.mp4')
    return inspect(out)


def inspect(out):
    candidate = out / 'candidate.mp4'
    info = probe(candidate)
    run(['ffmpeg', '-v', 'error', '-i', str(candidate), '-f', 'null', '-'])
    _, signal = run(['ffmpeg', '-hide_banner', '-i', str(candidate), '-vn', '-af', 'volumedetect', '-f', 'null', '-'])
    video = [s for s in info['streams'] if s['codec_type'] == 'video']
    audio = [s for s in info['streams'] if s['codec_type'] == 'audio']
    if len(video) != 1 or len(audio) != 1 or video[0].get('nb_frames') != '288' or video[0].get('avg_frame_rate') != '24/1':
        raise ValueError('Candidate frame count, rate, or streams differ from contract')
    if abs(float(info['format']['duration']) - DURATION) > 0.001 or abs(float(video[0]['duration']) - DURATION) > 0.001:
        raise ValueError('Candidate duration differs from contract')
    level = re.search(r'max_volume: ([-\w.]+) dB', signal)
    if not level or not math.isfinite(float(level.group(1))):
        raise ValueError('Candidate audio has no finite peak signal')
    qa = {'candidate_sha256': sha(candidate), 'bytes': candidate.stat().st_size,
          'duration': float(info['format']['duration']),
          'streams': [{k: s[k] for k in ('codec_type', 'codec_name', 'width', 'height', 'sample_rate', 'avg_frame_rate', 'nb_frames', 'duration') if k in s} for s in info['streams']],
          'full_decode': 'pass', 'audio_signal': 'finite nonzero peak; not listening', 'audio_signal_log': signal,
          'normal_speed_viewing': 'not tested', 'listening': 'not tested',
          'narrative_and_audience_goal': 'not tested; requires actual playback and listening',
          'owner_acceptance': 'pending'}
    (out / 'qa.json').write_text(json.dumps(qa, indent=2) + '\n')
    for label, second in [('start', 1), ('action', 6.25), ('result', 8)]:
        ffmpeg(['-ss', second, '-i', candidate, '-frames:v', '1', out / f'{label}.png'])
    return qa


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path, help='New directory; never overwrite')
    parser.add_argument('--execution', type=Path, help='Replay a saved execution.json and its hash-bound plan/sources')
    args = parser.parse_args()
    try:
        if args.execution:
            manifest = json.loads(args.execution.read_text(encoding='utf-8'))
            validate_manifest(manifest, args.execution.parent)
            args.out.mkdir(parents=True, exist_ok=False)
            render(manifest, args.execution.parent, args.out / 'candidate.mp4')
            qa = inspect(args.out)
            (args.out / 'replay.json').write_text(json.dumps({'execution': str(args.execution.resolve()), 'sha256': sha(args.execution)}, indent=2) + '\n')
        else:
            qa = generate(args.out)
        print(json.dumps({k: qa[k] for k in ('candidate_sha256', 'duration', 'full_decode', 'listening', 'normal_speed_viewing')}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
