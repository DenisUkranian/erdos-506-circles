#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

OLD_SHA = '528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3'
FIXED = (2026, 8, 24, 0, 0, 0)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def safe_rel(name: str) -> PurePosixPath:
    name = name.replace('\\', '/')
    while name.startswith('./'):
        name = name[2:]
    p = PurePosixPath(name)
    if not name or name == '.' or p.is_absolute() or '..' in p.parts or '\x00' in name:
        raise RuntimeError(f'unsafe path: {name!r}')
    return p


def extract_zip(path: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as z:
        seen = set()
        for info in z.infolist():
            raw = info.filename.rstrip('/')
            if not raw:
                continue
            rel = safe_rel(raw)
            if rel.as_posix() in seen:
                raise RuntimeError(f'duplicate member: {rel}')
            seen.add(rel.as_posix())
            mode = (info.external_attr >> 16) & 0xffff
            if stat.S_ISLNK(mode):
                raise RuntimeError(f'symlink member: {rel}')
            target = dest / rel.as_posix()
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, target.open('wb') as out:
                    shutil.copyfileobj(src, out)
                perms = mode & 0o777
                if perms:
                    target.chmod(perms)
        bad = z.testzip()
        if bad:
            raise RuntimeError(f'bad ZIP CRC: {bad}')


def extract_vendor_tar(path: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, 'r:gz') as tf:
        for member in tf.getmembers():
            rel = safe_rel(member.name)
            if member.issym() or member.islnk() or member.isdev():
                raise RuntimeError(f'unsafe tar member: {member.name}')
            target = dest / rel.as_posix()
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                src = tf.extractfile(member)
                if src is None:
                    raise RuntimeError(f'cannot extract {member.name}')
                with src, target.open('wb') as out:
                    shutil.copyfileobj(src, out)
                target.chmod(member.mode & 0o777)


def copy_overlay(src: Path, dst: Path) -> None:
    for p in sorted(src.rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)


def manifest(root: Path, filename: str, dot_prefix: bool = False) -> None:
    target = root / filename
    rows = []
    for p in sorted(root.rglob('*'), key=lambda q: q.relative_to(root).as_posix()):
        if p.is_file() and p != target:
            rel = p.relative_to(root).as_posix()
            if dot_prefix:
                rel = './' + rel
            rows.append(f'{sha256(p)}  {rel}')
    target.write_text('\n'.join(rows) + '\n', encoding='utf-8')


def add_path(z: zipfile.ZipFile, path: Path, arc: str) -> None:
    st = path.lstat()
    if stat.S_ISLNK(st.st_mode):
        raise RuntimeError(f'symlink refused: {path}')
    if path.is_dir():
        if arc and not arc.endswith('/'):
            arc += '/'
        if arc:
            zi = zipfile.ZipInfo(arc, FIXED)
            zi.create_system = 3
            zi.external_attr = ((stat.S_IFDIR | 0o755) << 16) | 0x10
            zi.compress_type = zipfile.ZIP_STORED
            z.writestr(zi, b'')
        return
    zi = zipfile.ZipInfo(arc, FIXED)
    zi.create_system = 3
    zi.external_attr = ((stat.S_IFREG | (st.st_mode & 0o777)) << 16)
    zi.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(zi, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def make_zip(source: Path, output: Path, include_root: bool = True) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + '.tmp')
    if tmp.exists():
        tmp.unlink()
    base = source.parent if include_root else source
    paths = ([source] + sorted(source.rglob('*'), key=lambda p: p.relative_to(base).as_posix())
             if include_root else sorted(source.rglob('*'), key=lambda p: p.relative_to(base).as_posix()))
    with zipfile.ZipFile(tmp, 'w', allowZip64=True) as z:
        for p in paths:
            add_path(z, p, p.relative_to(base).as_posix())
    os.replace(tmp, output)


def normalize_vendor(n10: Path) -> None:
    env = n10 / 'sat_env'
    package = json.loads((env / 'package.json').read_text())
    package['dependencies']['cadical-wasm'] = '0.1.2'
    (env / 'package.json').write_text(json.dumps(package, indent=2) + '\n')
    lock = json.loads((env / 'package-lock.json').read_text())
    lock['packages']['']['dependencies']['cadical-wasm'] = '0.1.2'
    (env / 'package-lock.json').write_text(json.dumps(lock, indent=2) + '\n')
    rows = []
    for p in sorted(env.rglob('*'), key=lambda q: q.relative_to(n10).as_posix()):
        if p.is_file():
            rows.append(f'{sha256(p)}  {p.relative_to(n10).as_posix()}')
    (n10 / 'SAT_VENDOR_MANIFEST.sha256').write_text('\n'.join(rows) + '\n')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--overlay', type=Path, required=True)
    ap.add_argument('--vendor-tar', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()

    if sha256(args.source) != OLD_SHA:
        raise RuntimeError('source archive SHA-256 mismatch')

    with tempfile.TemporaryDirectory(prefix='erdos506_rebuild_v102_') as td:
        work = Path(td)
        extract_zip(args.source, work / 'outer')
        outer = work / 'outer' / 'Erdos506'
        if not outer.is_dir():
            raise RuntimeError('expected Erdos506 root')

        extract_zip(outer / 'packages/base.zip', work / 'base')
        roots = [p for p in (work / 'base').iterdir() if p.is_dir()]
        if len(roots) != 1:
            raise RuntimeError('expected one base root')
        base = roots[0]

        copy_overlay(args.overlay / 'base', base)
        n10 = base / 'n=10/01_COMPLETE_WORKING_PACKAGE'
        shutil.rmtree(n10 / 'sat_env', ignore_errors=True)
        extract_vendor_tar(args.vendor_tar, n10)
        normalize_vendor(n10)

        n14 = base / 'n=14/01_COMPLETE_WORKING_PACKAGE'
        manifest(n14, 'MANIFEST.sha256', dot_prefix=True)
        manifest(base, 'MANIFEST_V57.sha256')
        make_zip(base, outer / 'packages/base.zip')

        extract_zip(outer / 'packages/n13/B82.zip', work / 'b82')
        b82roots = [p for p in (work / 'b82').iterdir() if p.is_dir()]
        if len(b82roots) != 1:
            raise RuntimeError('expected one B82 root')
        b82 = b82roots[0]
        manifest(b82, 'MANIFEST.sha256')
        make_zip(b82, outer / 'packages/n13/B82.zip')

        copy_overlay(args.overlay / 'outer', outer)

        package_files = [
            'packages/base.zip', 'packages/n12.zip',
            'packages/n13/B80.zip', 'packages/n13/B81.zip',
            'packages/n13/B82.zip', 'packages/n13/B83.zip',
        ]
        (outer / 'PACKAGE_HASHES.sha256').write_text(
            ''.join(f'{sha256(outer / rel)}  {rel}\n' for rel in package_files),
            encoding='utf-8',
        )
        manifest(outer, 'MANIFEST.sha256')
        make_zip(outer, args.output)

    print(f'OUTPUT={args.output}')
    print(f'SHA256={sha256(args.output)}')


if __name__ == '__main__':
    main()
