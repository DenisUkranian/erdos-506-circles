# Final release audit

GitHub Release `v1.0.0` was published on 24 August 2026 only after a fail-closed workflow verified every release asset and replayed the canonical quick proof audit.

## Publication files

- manuscript clean compile: passed, 8 pages;
- computational supplement clean compile: passed, 5 pages;
- deterministic arXiv source ZIP: passed;
- deterministic supplement source ZIP: passed;
- all five release assets matched `ASSET_SHA256SUMS.txt`.

## Canonical verification object

```text
528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3  Erdos506.zip
```

Checks performed from a clean extraction include:

```text
TOP_MANIFEST=PASSED
PACKAGE=base ZIP=OK
PACKAGE=n12 ZIP=OK
PACKAGE=B80 ZIP=OK
PACKAGE=B81 ZIP=OK
PACKAGE=B82 ZIP=OK
PACKAGE=B83 ZIP=OK
MANIFEST=base PASSED
MANIFEST=n12 PASSED
MANIFEST=B80 PASSED
MANIFEST=B81 PASSED
MANIFEST=B82 PASSED
MANIFEST=B83 PASSED
RETAINED_FINAL_AUDITS=PASSED
ERDOS506_VALUE_ARITHMETIC=PASSED
ERDOS506_QUICK_AUDIT=PASSED
```

The retained full clean replay ends with:

```text
ERDOS506_FULL_REPLAY=PASSED
```

The release finalization workflow downloaded the public release assets, checked their SHA-256 values, unpacked `Erdos506.zip`, required `ERDOS506_QUICK_AUDIT=PASSED`, and only then published `v1.0.0`.

## Status boundary

This is a public computer-assisted preprint and reproducible exact verification package. It is not a proof-assistant formalization and has not yet undergone journal peer review. Independent mathematical review and clean-room reimplementation remain invited.
