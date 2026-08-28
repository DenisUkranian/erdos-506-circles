# Reproducibility protocol

## Canonical object

The canonical proof bundle is the GitHub Release asset `Erdos506.zip` attached to release [`v1.0.2`](https://github.com/DenisUkranian/erdos-506-circles/releases/tag/v1.0.2).

Expected SHA-256:

```text
100316dcf37b1f424cf93df9e36ab539a3e97c3fdb05c87d641fd181bffd6298
```

Download it to `verification/Erdos506.zip`.

## Quick and structural audits

```bash
bash verify_repository.sh
```

Expected markers:

```text
ERDOS506_QUICK_AUDIT=PASSED
ERDOS506_V102_AUDIT=PASSED
ERDOS506_REPOSITORY_QUICK=PASSED
```

The archive vendors and checksums `cadical-wasm@0.1.2` for the offline `n=10` SAT replay and SymPy 1.14.0 plus mpmath 1.3.0 for symbolic terminals. Network access is not part of verification.

## Full replay

```bash
rm -rf /tmp/erdos506-full
mkdir -p /tmp/erdos506-full
unzip -q verification/Erdos506.zip -d /tmp/erdos506-full
cd /tmp/erdos506-full/Erdos506
python3 verify.py --full
```

Expected final marker:

```text
ERDOS506_FULL_REPLAY=PASSED
```

The full replay compiles C++ sources and runs every active proof package, including all 61 AA and 61 AB `n=10` branches and the extended `n=14` path with all 286 labelled placements. Some packages validate exact retained certificates rather than repeat exploratory searches; timeouts are never accepted as negative proofs. Runtime depends strongly on CPU speed. Use a stable Linux host and retain stdout, `uname -a`, Python version, and compiler version.

## Verification layers

1. release-asset checksum;
2. outer archive checksum and manifest;
3. nested package checksums and ZIP integrity;
4. package-local manifests;
5. exact retained-certificate audits;
6. source recompilation and full enumeration where supported;
7. theorem-value consistency checks;
8. v1.0.2 packaging and historical-WIP boundary checks.

## Publication verification boundary

The pre-publication frozen bytes passed the complete fail-closed gate. After publication, GitHub's public API digests for all nine uploaded assets matched their frozen expected SHA-256 values, and those exact frozen bytes passed fresh quick and structural audits. The execution environment blocked a direct post-publication browser download, so no independent consumer-side byte-download replay is claimed.

## Independent audit request

A strong independent audit could reimplement at least one of:

- the `n=10` AA or AB SAT encodings;
- the `n=12` local allowable-sequence classification;
- the `n=13, B=80` 695-branch residual search;
- the `n=13, B=82, k=14` line-skeleton test;
- the `23T+9D` projective obstruction at `B=83`;
- the `n=14` all-286 placement ledger.
