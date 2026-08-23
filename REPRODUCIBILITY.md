# Reproducibility protocol

## Canonical object

The canonical proof bundle is the GitHub Release asset `Erdos506.zip` attached to release `v1.0.0`.

Expected SHA-256:

```text
528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3
```

Download the release asset and place it at:

```text
verification/Erdos506.zip
```

## Quick audit

```bash
(cd verification && sha256sum -c Erdos506.zip.sha256)
rm -rf /tmp/erdos506-quick
mkdir -p /tmp/erdos506-quick
unzip -q verification/Erdos506.zip -d /tmp/erdos506-quick
cd /tmp/erdos506-quick/Erdos506
python3 verify.py
```

Expected final marker:

```text
ERDOS506_QUICK_AUDIT=PASSED
```

## Full replay

```bash
cd /tmp/erdos506-quick/Erdos506
python3 verify.py --full
```

Expected final marker:

```text
ERDOS506_FULL_REPLAY=PASSED
```

The full replay compiles the C++ sources and reruns the finite proof packages. Runtime depends strongly on CPU speed. Run on a stable Linux host and retain stdout, `uname -a`, Python version and compiler version.

## GitHub Actions

Both workflows are manual (`workflow_dispatch`). They obtain `Erdos506.zip` from the `v1.0.0` release when it is not checked out locally.

## Verification layers

1. outer archive checksum and manifest;
2. nested package checksums and ZIP integrity;
3. package-local manifests;
4. exact retained-certificate audits;
5. source recompilation and full enumeration where supported;
6. theorem-value consistency checks.

## Independent audit request

A strong independent audit should reimplement at least one of:

- the `n=12` local allowable-sequence classification;
- the `n=13, B=80` 695-branch residual search;
- the `n=13, B=82, k=14` line-skeleton test;
- the `23T+9D` projective obstruction at `B=83`.
