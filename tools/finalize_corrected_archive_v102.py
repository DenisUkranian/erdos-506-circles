#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import shutil
import stat
import subprocess
import zipfile
from pathlib import Path

FIXED_DT = (2026, 8, 26, 0, 0, 0)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def write(path: Path, text: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')
    if mode is not None:
        path.chmod(mode)


def safe_extract_zip(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as zf:
        names = zf.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError(f'duplicate members in {source}')
        for info in zf.infolist():
            rel = Path(info.filename)
            if rel.is_absolute() or '..' in rel.parts:
                raise RuntimeError(f'unsafe member {info.filename!r} in {source}')
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise RuntimeError(f'symlink member {info.filename!r} in {source}')
        bad = zf.testzip()
        if bad:
            raise RuntimeError(f'CRC failure in {source}: {bad}')
        zf.extractall(destination)


def normalize_modes(root: Path) -> tuple[int, int]:
    executable = 0
    regular = 0
    root.chmod(0o755)
    for path in sorted(root.rglob('*')):
        if path.is_dir():
            path.chmod(0o755)
        elif path.is_file():
            head = path.read_bytes()[:2]
            if head == b'#!':
                path.chmod(0o755)
                executable += 1
            else:
                path.chmod(0o644)
                regular += 1
        else:
            raise RuntimeError(f'unsupported filesystem object: {path}')
    return executable, regular


def deterministic_zip(source_dir: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    all_paths = [source_dir] + sorted(
        source_dir.rglob('*'), key=lambda p: p.relative_to(source_dir.parent).as_posix()
    )
    seen: set[str] = set()
    with zipfile.ZipFile(
        destination,
        'w',
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        allowZip64=True,
    ) as zf:
        for path in all_paths:
            arcname = path.relative_to(source_dir.parent).as_posix()
            if path.is_dir():
                arcname += '/'
            if arcname in seen:
                raise RuntimeError(f'duplicate archive name: {arcname}')
            seen.add(arcname)
            info = zipfile.ZipInfo(arcname, FIXED_DT)
            info.create_system = 3
            mode = path.stat().st_mode & 0xFFFF
            info.external_attr = mode << 16
            if path.is_dir():
                info.external_attr |= 0x10
                zf.writestr(info, b'')
            elif path.is_file():
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(
                    info,
                    path.read_bytes(),
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
            else:
                raise RuntimeError(f'unsupported filesystem object: {path}')


def manifest_for(root: Path, output: Path, exclude: set[str]) -> None:
    rows: list[str] = []
    for path in sorted(root.rglob('*'), key=lambda p: p.relative_to(root).as_posix()):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in exclude:
            continue
        rows.append(f'{sha256(path)}  ./{rel}\n')
    write(output, ''.join(rows))


def outer_manifest(root: Path, output: Path) -> None:
    rows: list[str] = []
    for path in sorted(root.rglob('*'), key=lambda p: p.relative_to(root).as_posix()):
        if not path.is_file() or path.resolve() == output.resolve():
            continue
        rel = path.relative_to(root).as_posix()
        rows.append(f'{sha256(path)}  {rel}\n')
    write(output, ''.join(rows))


def single_directory(root: Path) -> Path:
    dirs = [p for p in root.iterdir() if p.is_dir()]
    if len(dirs) != 1:
        raise RuntimeError(f'expected one directory in {root}, got {dirs}')
    return dirs[0]


def prepend_notice(path: Path, notice: str) -> None:
    old = path.read_text(encoding='utf-8')
    marker = '<!-- V102_HISTORICAL_WIP_NOTICE -->'
    if marker not in old:
        write(path, notice + '\n\n---\n\n' + old)


parser = argparse.ArgumentParser()
parser.add_argument('--source', required=True, type=Path)
parser.add_argument('--work-dir', required=True, type=Path)
parser.add_argument('--output-dir', required=True, type=Path)
args = parser.parse_args()
source = args.source.resolve()
work = args.work_dir.resolve()
out = args.output_dir.resolve()

shutil.rmtree(work, ignore_errors=True)
shutil.rmtree(out, ignore_errors=True)
outer_dir = work / 'outer'
base_dir = work / 'base'
outer_dir.mkdir(parents=True)
base_dir.mkdir(parents=True)
out.mkdir(parents=True)

safe_extract_zip(source, outer_dir)
root = outer_dir / 'Erdos506'
if not root.is_dir():
    raise SystemExit('missing Erdos506 root')
safe_extract_zip(root / 'packages/base.zip', base_dir)
base = single_directory(base_dir)

# Remove interpreter caches accidentally created while probing the vendored CAS.
for cache in list(base.rglob('__pycache__')):
    shutil.rmtree(cache)
for pyc in list(base.rglob('*.pyc')):
    pyc.unlink()

# Repair executable modes lost by Python wheel/archive extraction. Every active
# directly-invoked source script in the predecessor package has a shebang.
outer_exec, outer_regular = normalize_modes(root)
base_exec, base_regular = normalize_modes(base)

notice = """<!-- V102_HISTORICAL_WIP_NOTICE -->
# Historical n=13 WIP provenance — inactive

This material is retained only as a provenance snapshot of the earlier v57
recovery checkpoint. It is **not** the active n=13 proof frontier and must not
be read as the current mathematical status. The corrected release verifies
n=13 through the separate outer packages `packages/n13/B80.zip`, `B81.zip`,
`B82.zip`, and `B83.zip`; the proven reduction gives `80 <= B <= 83`, so
B84–B86 are not required. The active outer `verify.py --full` does not dispatch
this historical directory.
"""
n13 = base / 'n=13'
write(n13 / 'HISTORICAL_WIP_NOTICE.md', notice + '\n')
for rel in [
    'README_FIRST.md',
    'PATH_TO_CURRENT_FRONTIER.md',
    '01_CURRENT_FRONTIER_PACKAGE/README.md',
    '01_CURRENT_FRONTIER_PACKAGE/CURRENT_STATUS.md',
    '01_CURRENT_FRONTIER_PACKAGE/CURRENT_STATUS_LATEST.md',
]:
    prepend_notice(n13 / rel, notice)

run_frontier = n13 / 'run_current_frontier.sh'
run_text = run_frontier.read_text(encoding='utf-8')
if 'HISTORICAL WIP AUDIT ONLY' not in run_text:
    run_text = run_text.replace(
        'set -euo pipefail\n',
        "set -euo pipefail\n\necho 'HISTORICAL WIP AUDIT ONLY: active n=13 proof is in outer B80-B83 packages.' >&2\n",
        1,
    ).replace(
        'echo "n=13 CURRENT FRONTIER AUDIT PASSED: B>=80; B=79 COMPLETE; 4 B=80 profiles terminal; 10 unresolved"',
        'echo "n=13 HISTORICAL WIP AUDIT PASSED: this is provenance only; active proof is outer B80-B83"',
    )
    write(run_frontier, run_text, 0o755)

root_notice = """# Historical recovery material retained in `base.zip`

The base recovery package contains an earlier n=13 WIP snapshot for provenance
and audit-history purposes. It is explicitly inactive. The final n=13 proof is
carried by the separate B80–B83 packages dispatched by `verify.py --full`.
No B84–B86 proof package is needed because the active reduction proves
`80 <= B <= 83`.
"""
write(root / 'HISTORICAL_WIP_NOTICE.md', root_notice)

readme = root / 'README.md'
readme_text = readme.read_text(encoding='utf-8')
if 'HISTORICAL_WIP_NOTICE.md' not in readme_text:
    readme_text += (
        '\n## Historical provenance note\n\n'
        'See `HISTORICAL_WIP_NOTICE.md`. The n=13 WIP directory inside the base '
        'recovery package is retained only for provenance and is not dispatched '
        'by the active verifier.\n'
    )
write(readme, readme_text)

# Prevent the complete replay from mutating the extracted proof tree with .pyc
# files; the recovery layout audit intentionally rejects such generated files.
verify_path = root / 'verify.py'
verify_text = verify_path.read_text(encoding='utf-8')
if "os.environ['PYTHONDONTWRITEBYTECODE']='1'" not in verify_text:
    verify_text = verify_text.replace(
        "  os.environ['PYTHONNOUSERSITE']='1'\n",
        "  os.environ['PYTHONNOUSERSITE']='1'\n  os.environ['PYTHONDONTWRITEBYTECODE']='1'\n",
        1,
    )
verify_text = verify_text.replace(
    "sh([sys.executable,'-S','-c',",
    "sh([sys.executable,'-B','-S','-c',",
    1,
)
write(verify_path, verify_text, 0o755)

v102_path = root / 'verify_v102.py'
v102_text = v102_path.read_text(encoding='utf-8')
if "env['PYTHONDONTWRITEBYTECODE']='1'" not in v102_text:
    v102_text = v102_text.replace(
        " env=os.environ.copy(); env['PYTHONPATH']=str(vendor); env['PYTHONNOUSERSITE']='1'\n",
        " env=os.environ.copy(); env['PYTHONPATH']=str(vendor); env['PYTHONNOUSERSITE']='1'; env['PYTHONDONTWRITEBYTECODE']='1'\n",
        1,
    )
v102_text = v102_text.replace(
    "[sys.executable,'-S','-c',",
    "[sys.executable,'-B','-S','-c',",
    1,
)
write(v102_path, v102_text, 0o755)

# Refresh human/machine file indexes and the embedded historical n=13
# manifest after adding the provenance notices.
subprocess.run(
    ['python3', str(base / 'build_file_indexes.py')],
    cwd=base,
    check=True,
    env={**__import__('os').environ, 'PYTHONDONTWRITEBYTECODE': '1'},
)
manifest_for(
    n13 / '01_CURRENT_FRONTIER_PACKAGE',
    n13 / '01_CURRENT_FRONTIER_PACKAGE/MANIFEST.sha256',
    {'MANIFEST.sha256'},
)

# Re-normalize after writing new files and scripts.
outer_exec, outer_regular = normalize_modes(root)
base_exec, base_regular = normalize_modes(base)

manifest_for(base, base / 'SHA256SUMS.txt', {'SHA256SUMS.txt', 'MANIFEST_V57.sha256'})
manifest_for(base, base / 'MANIFEST_V57.sha256', {'MANIFEST_V57.sha256'})
subprocess.run(
    ['sha256sum', '-c', 'MANIFEST_V57.sha256'],
    cwd=base,
    check=True,
    stdout=subprocess.DEVNULL,
)

base_one = work / 'base-one.zip'
base_two = work / 'base-two.zip'
deterministic_zip(base, base_one)
deterministic_zip(base, base_two)
if sha256(base_one) != sha256(base_two):
    raise SystemExit('base deterministic rebuild mismatch')
shutil.copy2(base_one, root / 'packages/base.zip')

package_rows: list[str] = []
for rel in [
    'packages/base.zip',
    'packages/n12.zip',
    'packages/n13/B80.zip',
    'packages/n13/B81.zip',
    'packages/n13/B82.zip',
    'packages/n13/B83.zip',
]:
    package_rows.append(f'{sha256(root / rel)}  {rel}\n')
write(root / 'PACKAGE_HASHES.sha256', ''.join(package_rows))
outer_manifest(root, root / 'MANIFEST.sha256')
subprocess.run(
    ['sha256sum', '-c', 'MANIFEST.sha256'],
    cwd=root,
    check=True,
    stdout=subprocess.DEVNULL,
)

final_one = out / 'Erdos506.zip'
final_two = out / 'Erdos506.second.zip'
deterministic_zip(root, final_one)
deterministic_zip(root, final_two)
if sha256(final_one) != sha256(final_two):
    raise SystemExit('outer deterministic rebuild mismatch')
final_two.unlink()
write(out / 'Erdos506.zip.sha256', f'{sha256(final_one)}  Erdos506.zip\n')

# Ensure the formerly failing direct script is executable in the rebuilt base ZIP.
with zipfile.ZipFile(base_one) as zf:
    members = zf.namelist()
    base_member = next(
        n for n in members
        if n.endswith('/n=12/01_CURRENT_FRONTIER_PACKAGE/run_n12_post_v54_structural.sh')
    )
    mode = (zf.getinfo(base_member).external_attr >> 16) & 0o777
    if not (mode & 0o111):
        raise SystemExit(f'executable mode not preserved for {base_member}: {oct(mode)}')

print(f'SOURCE_SHA256={sha256(source)}')
print(f'FINAL_SHA256={sha256(final_one)}')
print(f'FINAL_SIZE={final_one.stat().st_size}')
print(f'EXECUTABLE_FILES_OUTER={outer_exec}')
print(f'EXECUTABLE_FILES_BASE={base_exec}')
print('HISTORICAL_N13_WIP_MARKED_INACTIVE=PASSED')
print('EXECUTABLE_MODE_REPAIR=PASSED')
print('FINALIZE_CORRECTED_ARCHIVE_V102=PASSED')
