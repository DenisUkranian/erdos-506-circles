#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, stat, subprocess, sys, tarfile, tempfile, zipfile
from pathlib import Path

FIXED_DT = (2026, 8, 25, 0, 0, 0)
EXPECTED_OLD = '528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3'
EXPECTED_VENDOR_TGZ = 'e5fb041f3b1226d6a60c25de18583ce46ebcbe69f0eea1cc0f25855694973b20'

ap=argparse.ArgumentParser()
ap.add_argument('--source',required=True,type=Path)
ap.add_argument('--vendor-tgz',required=True,type=Path)
ap.add_argument('--build-dir',required=True,type=Path)
ap.add_argument('--output-dir',required=True,type=Path)
a=ap.parse_args()
SRC=a.source.resolve(); VENDOR_TGZ=a.vendor_tgz.resolve(); BUILD=a.build_dir.resolve(); OUT=a.output_dir.resolve()

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def write(path: Path, text: str, mode: int | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')
    if mode is not None: path.chmod(mode)

def deterministic_zip(src_dir: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as z:
        all_paths=[src_dir] + sorted(src_dir.rglob('*'), key=lambda p:p.relative_to(src_dir.parent).as_posix())
        seen=set()
        for p in all_paths:
            arc=p.relative_to(src_dir.parent).as_posix()
            if p.is_dir(): arc += '/'
            if arc in seen: raise RuntimeError(f'duplicate arcname {arc}')
            seen.add(arc)
            zi=zipfile.ZipInfo(arc, FIXED_DT)
            zi.create_system=3
            mode=p.stat().st_mode
            zi.external_attr=(mode & 0xFFFF)<<16
            if p.is_dir():
                zi.external_attr |= 0x10
                z.writestr(zi, b'')
            elif p.is_file():
                zi.compress_type=zipfile.ZIP_DEFLATED
                with p.open('rb') as f: z.writestr(zi, f.read(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            else:
                raise RuntimeError(f'unsupported filesystem object {p}')

def manifest_for(root: Path, out: Path, exclude_names: set[str]):
    rows=[]
    for p in sorted(root.rglob('*'), key=lambda x:x.relative_to(root).as_posix()):
        if not p.is_file(): continue
        rel=p.relative_to(root).as_posix()
        if rel in exclude_names: continue
        rows.append(f'{sha(p)}  ./{rel}\n')
    write(out, ''.join(rows))

def nested_manifest_for(root: Path, out: Path):
    rows=[]
    for p in sorted(root.rglob('*'), key=lambda x:x.relative_to(root).as_posix()):
        if not p.is_file() or p.resolve()==out.resolve(): continue
        rel=p.relative_to(root).as_posix()
        rows.append(f'{sha(p)}  ./{rel}\n')
    write(out, ''.join(rows))

def outer_manifest(root: Path, out: Path):
    rows=[]
    for p in sorted(root.rglob('*'), key=lambda x:x.relative_to(root).as_posix()):
        if not p.is_file() or p.resolve()==out.resolve(): continue
        rel=p.relative_to(root).as_posix()
        rows.append(f'{sha(p)}  {rel}\n')
    write(out, ''.join(rows))

def safe_extract_zip(src: Path, dest: Path):
    with zipfile.ZipFile(src) as z:
        names=z.namelist()
        if len(names)!=len(set(names)): raise RuntimeError('duplicate members')
        for info in z.infolist():
            pp=Path(info.filename)
            if pp.is_absolute() or '..' in pp.parts: raise RuntimeError(f'unsafe {info.filename}')
            mode=(info.external_attr>>16)&0xFFFF
            if stat.S_ISLNK(mode): raise RuntimeError(f'symlink {info.filename}')
        bad=z.testzip()
        if bad: raise RuntimeError(f'bad zip member {bad}')
        z.extractall(dest)
        for info in z.infolist():
            target=dest/Path(info.filename)
            mode=(info.external_attr>>16)&0xFFFF
            if mode and target.exists():
                try: target.chmod(mode & 0o7777)
                except OSError: pass

if sha(SRC)!=EXPECTED_OLD: raise SystemExit('source archive hash mismatch')
if sha(VENDOR_TGZ)!=EXPECTED_VENDOR_TGZ: raise SystemExit('vendor tar hash mismatch')
shutil.rmtree(BUILD, ignore_errors=True)
shutil.rmtree(OUT, ignore_errors=True)
BUILD.mkdir(parents=True)
OUT.mkdir(parents=True)
safe_extract_zip(SRC, BUILD)
R=BUILD/'Erdos506'
base_tmp=BUILD/'_base'
base_tmp.mkdir()
safe_extract_zip(R/'packages/base.zip', base_tmp)
roots=[p for p in base_tmp.iterdir() if p.is_dir()]
if len(roots)!=1: raise SystemExit(f'bad base roots {roots}')
B=roots[0]
N10=B/'n=10/01_COMPLETE_WORKING_PACKAGE'
N14=B/'n=14/01_COMPLETE_WORKING_PACKAGE'

prov=B/'99_PROVENANCE/V102_PREDECESSOR_LEDGERS'
prov.mkdir(parents=True, exist_ok=True)
shutil.copy2(B/'MANIFEST_V57.sha256', prov/'MANIFEST_V57_PRE_V102.sha256')
shutil.copy2(B/'SHA256SUMS.txt', prov/'SHA256SUMS_PRE_V102.txt')

with tarfile.open(VENDOR_TGZ, 'r:gz') as tf:
    for m in tf.getmembers():
        pp=Path(m.name)
        if pp.is_absolute() or '..' in pp.parts: raise SystemExit(f'unsafe vendor member {m.name}')
    tf.extractall(N10)

runner14=N14/'run_extended_final_n14.sh'
txt=runner14.read_text(encoding='utf-8')
old='python3 inherited_v36/new_move/crosscheck_erdos506_n14_102700_all_286.py\n'
new='python3 inherited_v36/new_move/crosscheck_erdos506_n14_102700_all_286.py /tmp/e506_102700_all 60\n'
if txt.count(old)!=1: raise SystemExit('expected one old n14 invocation')
write(runner14, txt.replace(old,new), 0o755)

runner10=N10/'run_independent_proof.sh'
write(runner10, '''#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
"$HERE/run_dependency_free_core.sh"
CAD="$HERE/sat_env/node_modules/cadical-wasm/dist/index.js"
VENDOR_MANIFEST="$HERE/SAT_VENDOR_MANIFEST.sha256"
if [[ ! -f "$CAD" || ! -f "$VENDOR_MANIFEST" ]]; then
  echo 'Vendored SAT replay dependency missing or incomplete: cadical-wasm@0.1.2' >&2
  exit 3
fi
(
  cd "$HERE"
  sha256sum -c SAT_VENDOR_MANIFEST.sha256 >/dev/null
)
node -e "import(process.argv[1]).then(()=>console.log('cadical-wasm@0.1.2 import: PASSED'))" "$CAD"
python3 "$HERE/verify_erdos506_n10_max5_circle_AA_exact.py"
python3 "$HERE/verify_erdos506_n10_max5_circle_AB_exact.py"
echo 'Erdos #506 n=10 full replay: PASSED; f(10)=33'
''', 0o755)

write(N10/'SAT_BACKEND_REPLAY.md', '''# Offline SAT replay for the n=10 max-5-circle AA/AB sweeps

Release v1.0.2 vendors the pinned backend `cadical-wasm@0.1.2` directly in
`sat_env/`. No network access or package installation is required after the
archive is downloaded.

Before either SAT sweep runs, `run_independent_proof.sh` checks every vendored
file against `SAT_VENDOR_MANIFEST.sha256` and smoke-tests the ES-module import.
Then the exact branch drivers regenerate their DIMACS instances and require all
61 AA and all 61 AB branches to return UNSAT.

```bash
bash run_independent_proof.sh
```

The vendored package is MIT-licensed; its upstream LICENSE and metadata are
retained unchanged.
''')
write(N10/'README_STATUS.md', '''# n=10 — complete offline replay, f(10)=33

`run_dependency_free_core.sh` checks the standard-library exact components;
`run_independent_proof.sh` also checks the vendored `cadical-wasm@0.1.2` bytes
and reruns all 61 AA and 61 AB non-complementary max-5-circle SAT branches.

Expected final marker:

```text
Erdos #506 n=10 full replay: PASSED; f(10)=33
```
''')
write(N10/'INDEPENDENCE_STATUS.md', '''# n=10 independence and replay status — corrected release v1.0.2

The working exact result is f(10)=33. All direct branches, max-size-4/6
branches, complementary 5+5 branch, and clean-room maximum-5-line terminal are
local. The historical AA/AB sweeps use the pinned third-party backend
`cadical-wasm@0.1.2`, now vendored and checksummed, so complete replay is
offline and self-contained.
''')
write(N10/'INDEPENDENCE_GAP.md', '''# Resolved replay boundary in corrected release v1.0.2

The former max-5-line persistence gap was already closed. The remaining
packaging boundary—an external SAT installation for the AA/AB sweeps—is also
resolved by vendoring and checksumming `cadical-wasm@0.1.2`.
''')
write(N10/'README.md', '''# n=10 — complete exact package, f(10)=33

```bash
bash run_dependency_free_core.sh
bash run_independent_proof.sh
```

The second command performs the complete offline replay, including all 61+61
SAT branches. The pinned runtime is checked against
`SAT_VENDOR_MANIFEST.sha256` before use.
''')
write(N10/'V102_CORRECTION.md', '''# v1.0.2 correction

This release vendors the exact `cadical-wasm@0.1.2` runtime used in the fresh
61-AA/61-AB replay. Mathematical reductions and DIMACS generators are unchanged.
''')
write(N14/'V102_RUNNER_FIX.md', '''# v1.0.2 runner correction

The predecessor extended runner invoked the all-286 Python cross-check without
its required arguments. The corrected command is:

```bash
python3 inherited_v36/new_move/crosscheck_erdos506_n14_102700_all_286.py \
  /tmp/e506_102700_all 60
```

A clean rerun passed the fast audit, all 86 sigma=1 regenerations, slow B=96
classifications, all 286 placements, and the final extended marker.
''')

nested_manifest_for(N14, N14/'MANIFEST.sha256')
subprocess.run(['python3', str(B/'build_file_indexes.py')], cwd=B, check=True)

write(B/'V102_CORRECTION.md', '''# Corrected replay snapshot for release v1.0.2

This is the v57 recovery payload with two reproducibility-only corrections:
(1) the n=14 all-286 call receives its required arguments; (2) the pinned n=10
SAT backend is vendored and checked. No theorem statement, finite profile,
certificate, or search input changed. The active manifest filename is retained
for compatibility and regenerated over the corrected tree; the predecessor is
preserved under `99_PROVENANCE/V102_PREDECESSOR_LEDGERS/`.
''')
write(B/'README_V102.md', '''# Start here — corrected release v1.0.2

Verify `MANIFEST_V57.sha256`, run the recovery audit, and use the outer
`verify.py --full` or `verify_fresh_critical.py` for complete fresh replay.
''')

manifest_for(B, B/'SHA256SUMS.txt', {'SHA256SUMS.txt','MANIFEST_V57.sha256'})
manifest_for(B, B/'MANIFEST_V57.sha256', {'MANIFEST_V57.sha256'})
subprocess.run(['sha256sum','-c','MANIFEST_V57.sha256'],cwd=B,check=True,stdout=subprocess.DEVNULL)

base1=BUILD/'base1.zip'; base2=BUILD/'base2.zip'
deterministic_zip(B, base1); deterministic_zip(B, base2)
if sha(base1)!=sha(base2): raise SystemExit('base deterministic build mismatch')
shutil.copy2(base1, R/'packages/base.zip')

verify_py = (R/'verify.py').read_text(encoding='utf-8')
verify_py = verify_py.replace("sh(['bash','run_dependency_free_core.sh'],cwd=b/'n=10/01_COMPLETE_WORKING_PACKAGE')", "sh(['bash','run_independent_proof.sh'],cwd=b/'n=10/01_COMPLETE_WORKING_PACKAGE')")
verify_py = verify_py.replace("sh(['bash','run_fast_final_n14.sh'],cwd=b/'n=14/01_COMPLETE_WORKING_PACKAGE')", "sh(['bash','run_extended_final_n14.sh'],cwd=b/'n=14/01_COMPLETE_WORKING_PACKAGE')")
if "run_independent_proof.sh'],cwd=b/'n=10" not in verify_py or "run_extended_final_n14.sh" not in verify_py:
    raise SystemExit('verify.py patch failed')
write(R/'verify.py', verify_py, 0o755)

write(R/'VERSION.txt', 'v1.0.2\n')
write(R/'CHANGELOG_V102.md', '''# v1.0.2 — reproducibility correction

- fixed the n=14 all-286 runner invocation;
- vendored and checksummed `cadical-wasm@0.1.2` for offline n=10 replay;
- made `verify.py --full` run complete n=10 and extended n=14 runners;
- added corrected-release and targeted fresh-critical verifiers;
- regenerated all affected manifests.

No mathematical input or claimed value changed.
''')
write(R/'THIRD_PARTY_NOTICES.md', '''# Third-party notice

The n=10 complete replay includes `cadical-wasm@0.1.2` under the MIT License.
Its upstream LICENSE and metadata are included unchanged in `packages/base.zip`.
''')
write(R/'README.md', '''# Erdős Problem 506 — corrected verification archive v1.0.2

```bash
python3 verify.py
python3 verify_v102.py
python3 verify.py --full
python3 verify_fresh_critical.py
```

The last two commands can take several hours. No network access is required
after download. v1.0.2 changes replay packaging only: the n=14 invocation is
corrected and the pinned n=10 SAT backend is vendored and checksummed.
Mathematical inputs and claims are unchanged.
''')
write(R/'STATUS.md', '''# Status — v1.0.2

Working exact computer-assisted result under the Elliott–Purdy–Smith convention:
f(8)=17 and f(n)=1+C(n-1,2)-floor((n-1)/2) for all n>=9, including
f(12)=51, f(13)=61, and f(14)=73. The computational frontier represented by
this archive is closed; independent human mathematical review is still invited.
''')
write(R/'REQUIREMENTS.md', '''# Requirements

Quick: Python 3.10+, `sha256sum`, ZIP tools.
Complete replay: Bash, GNU C++ with C++17/C++20, Node.js 18+, Unix-like system.
No network access or package installation is required after download.
''')
write(R/'FULL_REPLAY_AUDIT.md', '''# Full replay semantics — v1.0.2

`python3 verify.py --full` checks all manifests and runs every active proof
package, including the complete 61+61 n=10 SAT sweeps and n=14 extended runner.
Some packages verify exact certificates or retained exhaustive outputs rather
than repeating exploratory searches; timeouts are never accepted as NO proofs.
''')

write(R/'verify_v102.py', r'''#!/usr/bin/env python3
from __future__ import annotations
import json, re, stat, subprocess, tempfile, zipfile
from pathlib import Path
R=Path(__file__).resolve().parent

def safe_zip(p):
 with zipfile.ZipFile(p) as z:
  ns=z.namelist(); assert len(ns)==len(set(ns)),p
  assert z.testzip() is None,p
  for i in z.infolist():
   q=Path(i.filename); assert not q.is_absolute() and '..' not in q.parts,(p,i.filename)
   mode=(i.external_attr>>16)&0xffff; assert not stat.S_ISLNK(mode),(p,i.filename)

def root_of(d):
 xs=[p for p in d.iterdir() if p.is_dir()]; assert len(xs)==1,xs; return xs[0]

assert (R/'VERSION.txt').read_text().strip()=='v1.0.2'
for p in [R/'packages/base.zip',R/'packages/n12.zip',*sorted((R/'packages/n13').glob('*.zip'))]: safe_zip(p)
with tempfile.TemporaryDirectory(prefix='erdos506_v102_') as td:
 td=Path(td); d=td/'base'; d.mkdir()
 with zipfile.ZipFile(R/'packages/base.zip') as z:z.extractall(d)
 b=root_of(d); n10=b/'n=10/01_COMPLETE_WORKING_PACKAGE'; n14=b/'n=14/01_COMPLETE_WORKING_PACKAGE'
 subprocess.run(['sha256sum','-c','SAT_VENDOR_MANIFEST.sha256'],cwd=n10,check=True,stdout=subprocess.DEVNULL)
 pkg=json.loads((n10/'sat_env/node_modules/cadical-wasm/package.json').read_text())
 assert pkg['name']=='cadical-wasm' and pkg['version']=='0.1.2'
 r10=(n10/'run_independent_proof.sh').read_text(); assert 'sha256sum -c SAT_VENDOR_MANIFEST.sha256' in r10
 r14=(n14/'run_extended_final_n14.sh').read_text()
 assert 'crosscheck_erdos506_n14_102700_all_286.py /tmp/e506_102700_all 60' in r14
 for p in b.rglob('*.sh'): subprocess.run(['bash','-n',str(p)],check=True)
 for p in [n10/'run_independent_proof.sh',n10/'run_dependency_free_core.sh',n14/'run_extended_final_n14.sh']:
  t=p.read_text(errors='replace')
  assert not re.search(r'(^|[;&|]\s*)(curl|wget|npm\s+install|pip\s+install)',t,re.M),p
print('ERDOS506_V102_AUDIT=PASSED')
''', 0o755)

write(R/'verify_fresh_critical.py', r'''#!/usr/bin/env python3
from __future__ import annotations
import re, subprocess, tempfile, zipfile
from pathlib import Path
R=Path(__file__).resolve().parent

def root_of(d):
 xs=[p for p in d.iterdir() if p.is_dir()]; assert len(xs)==1,xs; return xs[0]

def run(cmd,cwd,marker):
 print('+',' '.join(map(str,cmd)),flush=True)
 p=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 print(p.stdout,end='')
 if p.returncode: raise SystemExit(p.returncode)
 assert marker in p.stdout,marker
 assert not re.search(r'\b(?:timeouts?|timed)\s*[=:]\s*[1-9][0-9]*',p.stdout,re.I)

with tempfile.TemporaryDirectory(prefix='erdos506_fresh_') as td:
 td=Path(td); d=td/'base'; d.mkdir()
 with zipfile.ZipFile(R/'packages/base.zip') as z:z.extractall(d)
 b=root_of(d)
 run(['bash','run_independent_proof.sh'],b/'n=9/01_COMPLETE_WORKING_PACKAGE','n=9 independent proof audit: PASSED')
 run(['bash','run_independent_proof.sh'],b/'n=10/01_COMPLETE_WORKING_PACKAGE','n=10 full replay: PASSED; f(10)=33')
 run(['bash','run_extended_final_n14.sh'],b/'n=14/01_COMPLETE_WORKING_PACKAGE','EXTENDED FINAL N14 AUDIT: PASSED')
print('ERDOS506_FRESH_CRITICAL_REPLAY=PASSED')
''', 0o755)

pkg_rows=[]
for rel in ['packages/base.zip','packages/n12.zip','packages/n13/B80.zip','packages/n13/B81.zip','packages/n13/B82.zip','packages/n13/B83.zip']:
    pkg_rows.append(f'{sha(R/rel)}  {rel}\n')
write(R/'PACKAGE_HASHES.sha256',''.join(pkg_rows))
outer_manifest(R,R/'MANIFEST.sha256')
subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=R,check=True,stdout=subprocess.DEVNULL)

out1=OUT/'Erdos506.zip'; out2=OUT/'Erdos506.second.zip'
deterministic_zip(R,out1); deterministic_zip(R,out2)
if sha(out1)!=sha(out2): raise SystemExit('outer deterministic build mismatch')
out2.unlink()
write(OUT/'Erdos506.zip.sha256',f'{sha(out1)}  Erdos506.zip\n')
print('SOURCE_SHA256',EXPECTED_OLD)
print('V102_SHA256',sha(out1))
print('SIZE',out1.stat().st_size)
print('BUILD=PASSED')
