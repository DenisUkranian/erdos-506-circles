#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

FIXED_DT = (2026, 8, 25, 0, 0, 0)
EXPECTED_PRELIMINARY = "d7c5b7146d4ae3c58c54e0dcb584477120907b694a40486191496e2014511b72"
EXPECTED_SYMPY_WHEEL = "e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5"
EXPECTED_MPMATH_WHEEL = "a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write(path: Path, text: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    if mode is not None:
        path.chmod(mode)


def safe_extract_zip(source: Path, destination: Path) -> None:
    """Extract a ZIP after validating paths and restore recorded Unix modes.

    Python's ZipFile.extractall() does not reliably restore executable bits.
    The proof package has shell runners that invoke sibling scripts directly,
    so losing those bits makes an otherwise valid replay fail with rc=126.
    """
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as zf:
        names = zf.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError(f"duplicate members in {source}")
        for info in zf.infolist():
            rel = Path(info.filename)
            if rel.is_absolute() or ".." in rel.parts:
                raise RuntimeError(f"unsafe member {info.filename!r} in {source}")
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise RuntimeError(f"symlink member {info.filename!r} in {source}")
        bad = zf.testzip()
        if bad:
            raise RuntimeError(f"CRC failure in {source}: {bad}")
        zf.extractall(destination)
        for info in zf.infolist():
            target = destination / Path(info.filename)
            mode = (info.external_attr >> 16) & 0xFFFF
            if mode and target.exists():
                target.chmod(mode & 0o7777)


def normalize_tree(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            path.chmod(0o755)
        elif path.is_file():
            path.chmod(0o644)
        else:
            raise RuntimeError(f"unsupported filesystem object: {path}")


def deterministic_zip(source_dir: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    all_paths = [source_dir] + sorted(
        source_dir.rglob("*"), key=lambda p: p.relative_to(source_dir.parent).as_posix()
    )
    seen: set[str] = set()
    with zipfile.ZipFile(
        destination,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        allowZip64=True,
    ) as zf:
        for path in all_paths:
            arcname = path.relative_to(source_dir.parent).as_posix()
            if path.is_dir():
                arcname += "/"
            if arcname in seen:
                raise RuntimeError(f"duplicate archive name: {arcname}")
            seen.add(arcname)
            info = zipfile.ZipInfo(arcname, FIXED_DT)
            info.create_system = 3
            mode = path.stat().st_mode & 0xFFFF
            info.external_attr = mode << 16
            if path.is_dir():
                info.external_attr |= 0x10
                zf.writestr(info, b"")
            elif path.is_file():
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(
                    info,
                    path.read_bytes(),
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
            else:
                raise RuntimeError(f"unsupported filesystem object: {path}")


def manifest_for(root: Path, output: Path, exclude: set[str]) -> None:
    rows: list[str] = []
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in exclude:
            continue
        rows.append(f"{sha256(path)}  ./{rel}\n")
    write(output, "".join(rows))


def outer_manifest(root: Path, output: Path) -> None:
    rows: list[str] = []
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if not path.is_file() or path.resolve() == output.resolve():
            continue
        rel = path.relative_to(root).as_posix()
        rows.append(f"{sha256(path)}  {rel}\n")
    write(output, "".join(rows))


def single_directory(root: Path) -> Path:
    dirs = [p for p in root.iterdir() if p.is_dir()]
    if len(dirs) != 1:
        raise RuntimeError(f"expected one directory in {root}, got {dirs}")
    return dirs[0]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one {label}; found {count}")
    return text.replace(old, new, 1)


def require_executable(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"required replay script is missing: {path}")
    if not os.access(path, os.X_OK):
        raise RuntimeError(f"required replay script lost its executable mode: {path}")


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, type=Path)
parser.add_argument("--sympy-wheel", required=True, type=Path)
parser.add_argument("--mpmath-wheel", required=True, type=Path)
parser.add_argument("--work-dir", required=True, type=Path)
parser.add_argument("--output-dir", required=True, type=Path)
args = parser.parse_args()

source = args.source.resolve()
sympy_wheel = args.sympy_wheel.resolve()
mpmath_wheel = args.mpmath_wheel.resolve()
work = args.work_dir.resolve()
out = args.output_dir.resolve()

if sha256(source) != EXPECTED_PRELIMINARY:
    raise SystemExit("preliminary archive hash mismatch")
if sha256(sympy_wheel) != EXPECTED_SYMPY_WHEEL:
    raise SystemExit("SymPy wheel hash mismatch")
if sha256(mpmath_wheel) != EXPECTED_MPMATH_WHEEL:
    raise SystemExit("mpmath wheel hash mismatch")

shutil.rmtree(work, ignore_errors=True)
shutil.rmtree(out, ignore_errors=True)
outer_dir = work / "outer"
base_dir = work / "base"
outer_dir.mkdir(parents=True)
base_dir.mkdir(parents=True)
out.mkdir(parents=True)

safe_extract_zip(source, outer_dir)
root = outer_dir / "Erdos506"
if not root.is_dir():
    raise SystemExit("missing Erdos506 root")
safe_extract_zip(root / "packages/base.zip", base_dir)
base = single_directory(base_dir)

# Guard the exact mode loss that caused publication run #6 to fail.
require_executable(
    base / "95_POST_V56_RECOVERY_CHECKPOINT/run_n12_post_v54_structural.sh"
)
require_executable(base / "n=10/01_COMPLETE_WORKING_PACKAGE/run_independent_proof.sh")
require_executable(base / "n=14/01_COMPLETE_WORKING_PACKAGE/run_extended_final_n14.sh")

vendor = base / "third_party/python"
if vendor.exists():
    raise SystemExit("third_party/python already exists")
safe_extract_zip(sympy_wheel, vendor)
safe_extract_zip(mpmath_wheel, vendor)
for cache in list(vendor.rglob("__pycache__")):
    shutil.rmtree(cache)
for pyc in list(vendor.rglob("*.pyc")):
    pyc.unlink()
normalize_tree(vendor)

env = os.environ.copy()
env["PYTHONPATH"] = str(vendor)
env["PYTHONNOUSERSITE"] = "1"
probe = subprocess.run(
    [
        sys.executable,
        "-S",
        "-c",
        "import sympy,mpmath;"
        "assert sympy.__version__=='1.14.0',sympy.__version__;"
        "assert mpmath.__version__=='1.3.0',mpmath.__version__;"
        "print('VENDORED_SYMPY_MPMATH_IMPORT=PASSED')",
    ],
    env=env,
    check=True,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
print(probe.stdout, end="")

vendor_rows: list[str] = []
for path in sorted(vendor.rglob("*"), key=lambda p: p.relative_to(vendor).as_posix()):
    if path.is_file():
        vendor_rows.append(f"{sha256(path)}  ./{path.relative_to(vendor).as_posix()}\n")
write(vendor / "MANIFEST.sha256", "".join(vendor_rows))

write(
    base / "THIRD_PARTY_PYTHON.md",
    """# Vendored exact symbolic runtime

The complete replay vendors SymPy 1.14.0 and mpmath 1.3.0 under
`third_party/python/`. Their upstream wheel contents, metadata, and license
files are preserved. `third_party/python/MANIFEST.sha256` authenticates every
vendored file. The outer verifier prepends this directory to `PYTHONPATH`
before the n=11 and n=14 symbolic terminals run. No network or package
installation is required after downloading the archive.
""",
)

write(
    base / "N13_HISTORICAL_WIP_NOTICE.md",
    """# Historical n=13 WIP material

Some predecessor recovery directories retained inside the base package contain
historical status text from before B=80,81,82,83 were closed. They are retained
only as provenance and are not dispatched by the active verifier. The active
n=13 proof objects are the separate packages `B80.zip`, `B81.zip`, `B82.zip`,
and `B83.zip`; B=84,85,86 are excluded by the proved bound B<=83 and are not
open proof branches.
""",
)

write(
    root / "REQUIREMENTS.md",
    """# Requirements

Quick audit: Python 3.10+, `sha256sum`, and ZIP tools.

Complete replay: Bash, GNU C++ with C++17/C++20, Node.js 18+, and a
Unix-like system. SymPy 1.14.0, mpmath 1.3.0, and cadical-wasm 0.1.2 are
vendored and checksummed inside the archive. No network access or package
installation is required after download.
""",
)
write(
    root / "PYTHON_CAS_VENDOR.md",
    """# Offline Python symbolic dependency

Release v1.0.2 vendors SymPy 1.14.0 and mpmath 1.3.0 in the base proof
package. The complete verifier checks the vendor manifest and imports both
packages with system site packages disabled before executing symbolic
terminals.
""",
)

third_party = root / "THIRD_PARTY_NOTICES.md"
existing = third_party.read_text(encoding="utf-8") if third_party.exists() else "# Third-party notices\n"
if "SymPy 1.14.0" not in existing:
    existing += (
        "\n## Python symbolic runtime\n\n"
        "SymPy 1.14.0 and mpmath 1.3.0 are redistributed under their BSD-style\n"
        "licenses. Their wheel metadata and license files are retained under\n"
        "`packages/base.zip` in `third_party/python/`.\n"
    )
write(third_party, existing)

verify_path = root / "verify.py"
verify_text = verify_path.read_text(encoding="utf-8")
needle = "  b=roots['base']\n"
insertion = (
    "  b=roots['base']\n"
    "  python_vendor=b/'third_party/python'\n"
    "  if not python_vendor.is_dir(): raise SystemExit('missing vendored Python CAS runtime')\n"
    "  prior_pythonpath=os.environ.get('PYTHONPATH','')\n"
    "  os.environ['PYTHONPATH']=str(python_vendor)+(os.pathsep+prior_pythonpath if prior_pythonpath else '')\n"
    "  os.environ['PYTHONNOUSERSITE']='1'\n"
    "  sh([sys.executable,'-S','-c',\"import sympy,mpmath; assert sympy.__version__=='1.14.0'; assert mpmath.__version__=='1.3.0'; print('PYTHON_CAS_VENDOR=PASSED')\"])\n"
)
verify_text = replace_once(verify_text, needle, insertion, "base-root assignment")
write(verify_path, verify_text, 0o755)

v102_path = root / "verify_v102.py"
v102_text = v102_path.read_text(encoding="utf-8")
v102_text = replace_once(
    v102_text,
    "import json, re, stat, subprocess, tempfile, zipfile\n",
    "import json, os, re, stat, subprocess, sys, tempfile, zipfile\n",
    "verify_v102 import line",
)
v102_needle = " b=root_of(d); n10=b/'n=10/01_COMPLETE_WORKING_PACKAGE'; n14=b/'n=14/01_COMPLETE_WORKING_PACKAGE'\n"
v102_insertion = (
    " b=root_of(d); n10=b/'n=10/01_COMPLETE_WORKING_PACKAGE'; n14=b/'n=14/01_COMPLETE_WORKING_PACKAGE'\n"
    " vendor=b/'third_party/python'; assert vendor.is_dir(),vendor\n"
    " subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=vendor,check=True,stdout=subprocess.DEVNULL)\n"
    " env=os.environ.copy(); env['PYTHONPATH']=str(vendor); env['PYTHONNOUSERSITE']='1'\n"
    " subprocess.run([sys.executable,'-S','-c',\"import sympy,mpmath; assert sympy.__version__=='1.14.0'; assert mpmath.__version__=='1.3.0'\"],env=env,check=True)\n"
)
v102_text = replace_once(v102_text, v102_needle, v102_insertion, "verify_v102 base setup")
write(v102_path, v102_text, 0o755)

correction = root / "CHANGELOG_V102.md"
correction_text = correction.read_text(encoding="utf-8")
if "vendored SymPy" not in correction_text:
    correction_text = correction_text.replace(
        "- added corrected-release and targeted fresh-critical verifiers;\n",
        "- added corrected-release and targeted fresh-critical verifiers;\n"
        "- vendored SymPy 1.14.0 and mpmath 1.3.0 for the n=11/n=14 symbolic terminals;\n",
    )
write(correction, correction_text)

manifest_for(base, base / "SHA256SUMS.txt", {"SHA256SUMS.txt", "MANIFEST_V57.sha256"})
manifest_for(base, base / "MANIFEST_V57.sha256", {"MANIFEST_V57.sha256"})
subprocess.run(
    ["sha256sum", "-c", "MANIFEST_V57.sha256"],
    cwd=base,
    check=True,
    stdout=subprocess.DEVNULL,
)
base_zip_1 = work / "base-one.zip"
base_zip_2 = work / "base-two.zip"
deterministic_zip(base, base_zip_1)
deterministic_zip(base, base_zip_2)
if sha256(base_zip_1) != sha256(base_zip_2):
    raise SystemExit("base package deterministic rebuild mismatch")
shutil.copy2(base_zip_1, root / "packages/base.zip")

# Re-open the rebuilt base package and fail before publication if any essential
# runner lost its Unix executable bit in the ZIP metadata.
mode_probe_dir = work / "mode-probe"
safe_extract_zip(root / "packages/base.zip", mode_probe_dir)
mode_probe_base = single_directory(mode_probe_dir)
require_executable(
    mode_probe_base / "95_POST_V56_RECOVERY_CHECKPOINT/run_n12_post_v54_structural.sh"
)
require_executable(
    mode_probe_base / "n=10/01_COMPLETE_WORKING_PACKAGE/run_independent_proof.sh"
)
require_executable(
    mode_probe_base / "n=14/01_COMPLETE_WORKING_PACKAGE/run_extended_final_n14.sh"
)
print("REPLAY_EXECUTABLE_MODES=PASSED")

package_rows: list[str] = []
for rel in [
    "packages/base.zip",
    "packages/n12.zip",
    "packages/n13/B80.zip",
    "packages/n13/B81.zip",
    "packages/n13/B82.zip",
    "packages/n13/B83.zip",
]:
    package_rows.append(f"{sha256(root / rel)}  {rel}\n")
write(root / "PACKAGE_HASHES.sha256", "".join(package_rows))
outer_manifest(root, root / "MANIFEST.sha256")
subprocess.run(
    ["sha256sum", "-c", "MANIFEST.sha256"],
    cwd=root,
    check=True,
    stdout=subprocess.DEVNULL,
)

final_one = out / "Erdos506.zip"
final_two = out / "Erdos506.second.zip"
deterministic_zip(root, final_one)
deterministic_zip(root, final_two)
if sha256(final_one) != sha256(final_two):
    raise SystemExit("outer archive deterministic rebuild mismatch")
final_two.unlink()
write(out / "Erdos506.zip.sha256", f"{sha256(final_one)}  Erdos506.zip\n")
print(f"PRELIMINARY_SHA256={EXPECTED_PRELIMINARY}")
print(f"FINAL_SHA256={sha256(final_one)}")
print(f"FINAL_SIZE={final_one.stat().st_size}")
print("VENDORED_PYTHON_CAS_BUILD=PASSED")
