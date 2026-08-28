# Erdős Problem 506 — corrected self-contained proof archive v1.0.2

This patch release corrects reproducibility and package hygiene only; mathematical inputs and claimed values are unchanged.

## Corrections

- fixed the `n=14` all-286 verifier invocation;
- vendored and checksummed `cadical-wasm@0.1.2` for offline `n=10` replay;
- vendored and checksummed SymPy 1.14.0 and mpmath 1.3.0;
- restored executable modes required by nested proof runners;
- explicitly marked the stale `n=13` WIP snapshot as historical and inactive;
- made the full verifier execute the complete `n=10` and extended `n=14` paths.

## Assets

- `Erdos506.zip` and `Erdos506.zip.sha256` — canonical corrected proof archive and checksum;
- `erdos506_preprint.pdf` — manuscript;
- `erdos506_computational_supplement.pdf` — verification manual and finite ledgers;
- `arxiv-source.zip` and `supplement-source.zip` — manuscript sources;
- `Erdos506_AUDIT_v1.0.2.zip` and its checksum — publication-gate logs;
- `ASSET_SHA256SUMS.txt` — checksums for the other eight uploaded assets.

## Canonical proof checksum

```text
100316dcf37b1f424cf93df9e36ab539a3e97c3fdb05c87d641fd181bffd6298  Erdos506.zip
```

## Verification

The frozen archive passed deterministic builds, quick and v1.0.2 structural audits, complete clean replay, all 61 AA and 61 AB `n=10` branches, `n=12`, all active `n=13` packages for `B=80,81,82,83`, all 286 `n=14` placements, and fail-closed mutation tests.

Expected markers include:

```text
ERDOS506_QUICK_AUDIT=PASSED
ERDOS506_V102_AUDIT=PASSED
ERDOS506_FULL_REPLAY=PASSED
```

The manuscript PDFs and source ZIPs are byte-identical to their `v1.0.0` counterparts and retain historical first-release text internally. The corrected canonical verification object and checksum are defined by this `v1.0.2` release.

Rafał Wrona's scoped external cross-check of `v1.0.0` is preserved in issue #5. Independent human mathematical and formal review remains invited. No claim of journal peer review or adjudicated priority is made.
