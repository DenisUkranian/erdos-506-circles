#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

OLD_SHA = "528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3"
VENDOR_SHA = "e5fb041f3b1226d6a60c25de18583ce46ebcbe69f0eea1cc0f25855694973b20"
STAMP = (2026, 8, 24, 0, 0, 0)
ROW = re.compile(r"^([0-9a-fA-F]{64})\s+([*]?)(.+?)\s*$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_zip(path: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        seen: set[str] = set()
        for info in zf.infolist():
            p = PurePosixPath(info.filename)
            mode = (info.external_attr >> 16) & 0xFFFF
            if p.is_absolute() or ".." in p.parts or "\\" in info.filename:
                raise RuntimeError(f"unsafe ZIP path: {info.filename}")
            if info.filename in seen:
                raise RuntimeError(f"duplicate ZIP member: {info.filename}")
            if stat.S_ISLNK(mode):
                raise RuntimeError(f"symlink ZIP member: {info.filename}")
            seen.add(info.filename)
        bad = zf.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failure: {bad}")


def extract_zip(path: Path, destination: Path) -> None:
    safe_zip(path)
    with zipfile.ZipFile(path) as zf:
        zf.extractall(destination)


def safe_tar_extract(path: Path, destination: Path) -> None:
    with tarfile.open(path, "r:gz") as tf:
        for member in tf.getmembers():
            p = PurePosixPath(member.name)
            if p.is_absolute() or ".." in p.parts:
                raise RuntimeError(f"unsafe TAR path: {member.name}")
            if member.issym() or member.islnk() or member.isdev():
                raise RuntimeError(f"unsupported TAR member: {member.name}")
        tf.extractall(destination, filter="data")


def parse_manifest(path: Path):
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        match = ROW.match(line)
        if match:
            rows.append((match.group(1).lower(), match.group(2), match.group(3)))
    return rows


def resolve(path: Path, rel: str, root: Path) -> Path | None:
    norm = rel.replace("\\", "/")
    for base in (path.parent, root, root.parent):
        candidate = base.joinpath(*PurePosixPath(norm).parts)
        if candidate.is_file():
            return candidate
    return None


def manifest_base(path: Path, rows, root: Path) -> Path:
    candidates = (path.parent, root, root.parent)
    sample = rows[:100]
    return max(
        candidates,
        key=lambda base: sum(
            base.joinpath(*PurePosixPath(rel.replace("\\", "/")).parts).exists()
            for _, _, rel in sample
        ),
    )


def refresh_manifest(path: Path, root: Path, add_new: bool = False) -> None:
    rows = parse_manifest(path)
    if not rows:
        return
    base = manifest_base(path, rows, root)
    output = []
    listed = set()
    for old, star, rel in rows:
        listed.add(rel.replace("\\", "/"))
        target = resolve(path, rel, root)
        if target is None:
            raise RuntimeError(f"unresolved manifest path: {path}: {rel}")
        digest = old if target.resolve() == path.resolve() else sha256(target)
        output.append((digest, star, rel))
    if add_new:
        for target in sorted(
            (p for p in root.rglob("*") if p.is_file()),
            key=lambda p: p.as_posix(),
        ):
            if target.resolve() == path.resolve():
                continue
            try:
                rel = target.relative_to(base).as_posix()
            except ValueError:
                continue
            if rel not in listed:
                output.append((sha256(target), "", rel))
                listed.add(rel)
    path.write_text("\n".join(f"{h}  {star}{rel}" for h, star, rel in output) + "\n")


def refresh_all(root: Path) -> None:
    manifests = [
        p
        for p in root.rglob("*")
        if p.is_file()
        and (
            p.name.lower().endswith(".sha256")
            or p.name.lower() in {"checksums.sha256", "sha256sums", "sha256sums.txt"}
        )
        and parse_manifest(p)
    ]
    manifests.sort(key=lambda p: len(p.parts), reverse=True)
    for _ in range(5):
        before = {p: sha256(p) for p in manifests}
        for p in manifests:
            refresh_manifest(
                p,
                root,
                add_new=(p.parent.resolve() == root.resolve() and len(parse_manifest(p)) > 100),
            )
        if all(sha256(p) == before[p] for p in manifests):
            break


def deterministic_zip(src: Path, output: Path, archive_root: str) -> None:
    tmp = output.with_suffix(output.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        tmp,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        allowZip64=True,
    ) as zf:
        root_info = zipfile.ZipInfo(archive_root.rstrip("/") + "/", STAMP)
        root_info.create_system = 3
        root_info.external_attr = (0o40755 << 16) | 0x10
        zf.writestr(root_info, b"")
        for directory in sorted(
            (p for p in src.rglob("*") if p.is_dir()),
            key=lambda p: p.relative_to(src).as_posix(),
        ):
            arc = f"{archive_root}/{directory.relative_to(src).as_posix().rstrip('/')}/"
            info = zipfile.ZipInfo(arc, STAMP)
            info.create_system = 3
            info.external_attr = (0o40755 << 16) | 0x10
            zf.writestr(info, b"")
        for path in sorted(
            (p for p in src.rglob("*") if p.is_file()),
            key=lambda p: p.relative_to(src).as_posix(),
        ):
            arc = f"{archive_root}/{path.relative_to(src).as_posix()}"
            info = zipfile.ZipInfo(arc, STAMP)
            info.create_system = 3
            info.external_attr = (
                (0o100755 if os.access(path, os.X_OK) else 0o100644) << 16
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    os.replace(tmp, output)


def append_once(path: Path, heading: str, body: str) -> None:
    if not path.exists():
        return
    text = path.read_text(errors="replace")
    if heading in text:
        return
    path.write_text(text.rstrip() + "\n\n" + body.strip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--vendor-artifact", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if sha256(args.original) != OLD_SHA:
        raise RuntimeError("unexpected predecessor archive SHA-256")
    if args.work.exists():
        shutil.rmtree(args.work)
    args.work.mkdir(parents=True)

    outer_dir = args.work / "outer"
    extract_zip(args.original, outer_dir)
    outer = outer_dir / "Erdos506"
    if not outer.is_dir():
        raise RuntimeError("outer root Erdos506 missing")

    base_zip = outer / "packages" / "base.zip"
    base_dir = args.work / "base"
    extract_zip(base_zip, base_dir)
    roots = [p for p in base_dir.iterdir() if p.is_dir()]
    if len(roots) != 1:
        raise RuntimeError("base.zip must contain one root directory")
    master = roots[0]

    n14_runner = next(master.rglob("run_extended_final_n14.sh"))
    text = n14_runner.read_text()
    old_call = "python3 inherited_v36/new_move/crosscheck_erdos506_n14_102700_all_286.py"
    new_call = old_call + " /tmp/e506_102700_all 60"
    if new_call not in text:
        if old_call not in text:
            raise RuntimeError("n=14 all-286 call not found")
        n14_runner.write_text(text.replace(old_call, new_call, 1))
    n14_runner.chmod(n14_runner.stat().st_mode | 0o111)

    vendor_stage = args.work / "vendor"
    extract_zip(args.vendor_artifact, vendor_stage)
    tarballs = list(vendor_stage.rglob("cadical-wasm-0.1.2-vendor.tar.gz"))
    if len(tarballs) != 1 or sha256(tarballs[0]) != VENDOR_SHA:
        raise RuntimeError("vendored SAT tarball missing or has wrong SHA-256")
    n10_candidates = [p for p in master.rglob("01_COMPLETE_WORKING_PACKAGE") if p.parent.name == "n=10"]
    if len(n10_candidates) != 1:
        raise RuntimeError("n=10 package not uniquely located")
    n10 = n10_candidates[0]
    if (n10 / "sat_env").exists():
        shutil.rmtree(n10 / "sat_env")
    safe_tar_extract(tarballs[0], n10)
    index_js = n10 / "sat_env" / "node_modules" / "cadical-wasm" / "dist" / "index.js"
    wasm = n10 / "sat_env" / "node_modules" / "cadical-wasm" / "dist" / "cadical.wasm"
    if not index_js.is_file() or not wasm.is_file():
        raise RuntimeError("vendored SAT runtime is incomplete")
    vendor_files = sorted(
        (p for p in (n10 / "sat_env").rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(n10).as_posix(),
    )
    (n10 / "SAT_VENDOR_MANIFEST.sha256").write_text(
        "\n".join(f"{sha256(p)}  {p.relative_to(n10).as_posix()}" for p in vendor_files)
        + "\n"
    )
    (n10 / "VENDORED_SAT_BACKEND.md").write_text(
        f"""# Vendored SAT backend\n\nThe complete n=10 AA/AB replay uses the included `cadical-wasm@0.1.2` payload and therefore requires no network access after this archive is downloaded.\n\n- deterministic vendor tarball SHA-256: `{VENDOR_SHA}`\n- file-level checksum ledger: `SAT_VENDOR_MANIFEST.sha256`\n- lifecycle scripts were disabled during installation; `dist/index.js` and `dist/cadical.wasm` were smoke-tested before packaging.\n"""
    )

    correction = f"""# Corrections in v1.0.2\n\nThis revision changes no mathematical statement or finite input. It corrects two reproducibility defects found by fresh replay on 24 August 2026.\n\n1. The n=14 extended runner now passes the required binary and timeout arguments to the all-286 labelled-placement cross-check.\n2. The n=10 package now includes a checksummed offline copy of `cadical-wasm@0.1.2`, enabling the complete 61 AA plus 61 AB SAT replay without a package download.\n\nHistorical predecessor SHA-256: `{OLD_SHA}`.\n"""
    (master / "CORRECTIONS_v1.0.2.md").write_text(correction)
    refresh_all(master)

    corrected_base = args.work / "base.corrected.zip"
    deterministic_zip(master, corrected_base, master.name)
    safe_zip(corrected_base)
    shutil.copy2(corrected_base, base_zip)

    (outer / "CORRECTIONS_v1.0.2.md").write_text(correction)
    fresh = outer / "verify_fresh_critical.py"
    fresh.write_text(
        '''#!/usr/bin/env python3\nfrom __future__ import annotations\nimport argparse, pathlib, shutil, subprocess, tempfile, zipfile\np=argparse.ArgumentParser();p.add_argument("--keep",action="store_true");a=p.parse_args()\nroot=pathlib.Path(__file__).resolve().parent\nwork=pathlib.Path(tempfile.mkdtemp(prefix="erdos506-critical-"))\ntry:\n with zipfile.ZipFile(root/"packages/base.zip") as z:z.extractall(work)\n master=next(work.glob("Erdos506_MASTER_BY_N_*"))\n jobs=[\n  ("n9",master/"n=9/01_COMPLETE_WORKING_PACKAGE",["bash","run_independent_proof.sh"],"Erdos #506 n=9 independent proof audit: PASSED; f(9)=25"),\n  ("n10",master/"n=10/01_COMPLETE_WORKING_PACKAGE",["bash","run_independent_proof.sh"],"Erdos #506 n=10 full replay: PASSED; f(10)=33"),\n  ("n14",master/"n=14/01_COMPLETE_WORKING_PACKAGE",["bash","run_extended_final_n14.sh"],"=== EXTENDED FINAL N14 AUDIT: PASSED ==="),\n ]\n for name,cwd,cmd,marker in jobs:\n  print("=== fresh",name,"===",flush=True)\n  r=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)\n  (root/f"fresh_{name}.log").write_text(r.stdout);print(r.stdout,end="")\n  if r.returncode or marker not in r.stdout:raise SystemExit(f"{name} failed")\n print("ERDOS506_FRESH_CRITICAL_REPLAY=PASSED")\nfinally:\n if not a.keep:shutil.rmtree(work,ignore_errors=True)\n'''
    )
    fresh.chmod(0o755)

    verify_v102 = outer / "verify_v102.py"
    verify_v102.write_text(
        '''#!/usr/bin/env python3\nfrom __future__ import annotations\nimport hashlib,re,stat,subprocess,sys,tempfile,zipfile,shutil\nfrom pathlib import Path,PurePosixPath\nR=re.compile(r"^([0-9a-fA-F]{64})\\s+[*]?(.+?)\\s*$")\ndef sha(p):\n h=hashlib.sha256()\n with open(p,"rb") as f:\n  for b in iter(lambda:f.read(1<<20),b""):h.update(b)\n return h.hexdigest()\ndef safe(zp):\n with zipfile.ZipFile(zp) as z:\n  seen=set()\n  for i in z.infolist():\n   q=PurePosixPath(i.filename);m=(i.external_attr>>16)&0xffff\n   if q.is_absolute() or ".." in q.parts or "\\\\" in i.filename or i.filename in seen or stat.S_ISLNK(m):raise SystemExit("unsafe ZIP member: "+i.filename)\n   seen.add(i.filename)\n  if z.testzip():raise SystemExit("ZIP CRC failure")\nroot=Path(__file__).resolve().parent\nif subprocess.run([sys.executable,"verify.py"],cwd=root).returncode:raise SystemExit(1)\nfor z in root.rglob("*.zip"):safe(z)\nw=Path(tempfile.mkdtemp(prefix="e506-v102-"))\ntry:\n with zipfile.ZipFile(root/"packages/base.zip") as z:z.extractall(w)\n master=next(w.glob("Erdos506_MASTER_BY_N_*"))\n n14=master/"n=14/01_COMPLETE_WORKING_PACKAGE/run_extended_final_n14.sh"\n if "crosscheck_erdos506_n14_102700_all_286.py /tmp/e506_102700_all 60" not in n14.read_text():raise SystemExit("n14 runner correction missing")\n n10=master/"n=10/01_COMPLETE_WORKING_PACKAGE";vm=n10/"SAT_VENDOR_MANIFEST.sha256"\n for line in vm.read_text().splitlines():\n  m=R.match(line)\n  if not m:continue\n  q=n10.joinpath(*PurePosixPath(m.group(2).replace("\\\\","/")).parts)\n  if not q.is_file() or sha(q)!=m.group(1).lower():raise SystemExit("SAT vendor mismatch: "+m.group(2))\nfinally:shutil.rmtree(w,ignore_errors=True)\nprint("ERDOS506_V102_AUDIT=PASSED")\n'''
    )
    verify_v102.chmod(0o755)

    append_once(
        outer / "README.md",
        "## Corrections in v1.0.2",
        """## Corrections in v1.0.2\n\nThe n=14 extended-runner invocation is corrected and the pinned n=10 CaDiCaL-WASM backend is vendored. Run `python3 verify_v102.py` for structural verification and `python3 verify_fresh_critical.py` for fresh n=9, n=10, and n=14 regeneration.\n""",
    )
    append_once(
        outer / "REQUIREMENTS.md",
        "## Offline SAT backend",
        """## Offline SAT backend\n\nThe complete n=10 AA/AB sweep uses the checksummed `cadical-wasm@0.1.2` payload inside `packages/base.zip`. Node.js 18 or newer is required for that fresh replay; no package download is required.\n""",
    )
    append_once(
        outer / "FULL_REPLAY_AUDIT.md",
        "## Replay semantics clarification",
        """## Replay semantics clarification\n\n`verify.py --full` preserves the original master replay semantics, including retained exact outputs for several very long historical searches. `verify_fresh_critical.py` additionally forces fresh complete regeneration of n=9, all n=10 AA/AB SAT branches, and the corrected extended n=14 chain.\n""",
    )

    package_hashes = outer / "PACKAGE_HASHES.sha256"
    if package_hashes.exists():
        refresh_manifest(package_hashes, outer)
    refresh_all(outer)
    deterministic_zip(outer, args.output, "Erdos506")
    safe_zip(args.output)
    digest = sha256(args.output)
    args.output.with_suffix(args.output.suffix + ".sha256").write_text(
        f"{digest}  {args.output.name}\n"
    )
    print(digest)


if __name__ == "__main__":
    main()
