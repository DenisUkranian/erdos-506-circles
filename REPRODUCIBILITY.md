# Reproducibility protocol

## Canonical object

The canonical proof bundle is the GitHub Release asset `Erdos506.zip` attached to release `v1.0.0`.

Expected SHA-256:

```text
528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3
```

Download it to `verification/Erdos506.zip`.

## Quick audit

```bash
bash verify_repository.sh
```

Expected final marker:

```text
ERDOS506_REPOSITORY_QUICK=PASSED
```

The underlying package also prints:

```text
ERDOS506_QUICK_AUDIT=PASSED
```

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

The full replay compiles C++ sources and reruns the finite proof packages. Runtime depends strongly on CPU speed. Use a stable Linux host and retain stdout, `uname -a`, Python version and compiler version.

## Verification layers

1. release asset checksum;
2. outer archive checksum and manifest;
3. nested package checksums and ZIP integrity;
4. package-local manifests;
5. exact retained-certificate audits;
6. source recompilation and full enumeration where supported;
7. theorem-value consistency checks.

## Independent audit request

A strong independent audit should reimplement at least one of:

- the `n=12` local allowable-sequence classification;
- the `n=13, B=80` 695-branch residual search;
- the `n=13, B=82, k=14` line-skeleton test;
- the `23T+9D` projective obstruction at `B=83`.
