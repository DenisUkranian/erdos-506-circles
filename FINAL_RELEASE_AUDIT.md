# Final release audit — v1.0.2

GitHub Release [`v1.0.2`](https://github.com/DenisUkranian/erdos-506-circles/releases/tag/v1.0.2) was published on 28 August 2026 from the frozen, pre-verified asset set. It is public, is neither a draft nor a pre-release, and is the repository's Latest release. Tag `v1.0.2` resolves to commit `0fecffaecd3a53999aaef1b8a23a4665088af938`.

## Corrected verification archive

This patch release changes reproducibility and package hygiene, not the mathematical inputs or claimed values. It:

- fixes the `n=14` all-286 runner invocation;
- vendors and checksums `cadical-wasm@0.1.2` for offline `n=10` replay;
- vendors and checksums SymPy 1.14.0 and mpmath 1.3.0;
- restores executable modes required by nested proof runners;
- marks the stale `n=13` WIP snapshot explicitly historical and inactive;
- makes the full verifier execute the complete `n=10` and extended `n=14` paths.

Canonical object:

```text
100316dcf37b1f424cf93df9e36ab539a3e97c3fdb05c87d641fd181bffd6298  Erdos506.zip
```

## Pre-publication fail-closed gate

Attempt 1 of [workflow run 32986694903](https://github.com/DenisUkranian/erdos-506-circles/actions/runs/32986694903), at commit `0fecffaecd3a53999aaef1b8a23a4665088af938`, passed:

- deterministic preliminary, CAS-vendor, and final archive builds;
- preservation of executable bits for all shell runners;
- offline checks of the vendored SAT and symbolic-computation dependencies;
- ZIP and manifest integrity checks;
- `ERDOS506_QUICK_AUDIT=PASSED`;
- `ERDOS506_V102_AUDIT=PASSED`;
- `ERDOS506_FULL_REPLAY=PASSED`;
- all 61 AA and 61 AB branches for `n=10`;
- the complete `n=12` package;
- active `n=13` packages for `B=80,81,82,83`;
- the extended `n=14` replay, including all 286 labelled placements;
- negative fail-closed tests using intentionally damaged archives;
- preparation of the final asset set.

The run's GitHub Release API step then failed with HTTP 403 because the workflow token lacked the required workflow-file permission. The overall workflow is therefore correctly marked as failed, and its public-download step was skipped. This publication-API failure occurred after, and was separate from, all proof and asset checks. Release `v1.0.2` was subsequently published manually from those exact prepared assets.

## Public release verification

All nine uploaded assets are present. Each public GitHub API asset digest matches the asset's frozen pre-publication expected SHA-256. The released checksum manifest itself has SHA-256:

```text
e369239642db5cafb354b9a7f95cfa7b427e1ff92526510ab8cf0873751dae20  ASSET_SHA256SUMS.txt
```

The manifest intentionally lists the other eight uploaded assets; it cannot include its own checksum without changing itself.

The exact frozen upload bytes identified by those digests were freshly unpacked and passed the quick and v1.0.2 structural audits. A direct post-publication browser download was blocked by the execution environment, so this report does not claim an independent consumer-side byte-download replay.

## External focused delta cross-check

On 29 August 2026, Rafał Wrona published a [narrow delta cross-check](https://github.com/DenisUkranian/erdos-506-circles/issues/5#issuecomment-5461694383) against tag `v1.0.2`, commit `0fecffaecd3a53999aaef1b8a23a4665088af938`, and the canonical archive SHA-256 `100316dcf37b1f424cf93df9e36ab539a3e97c3fdb05c87d641fd181bffd6298`.

The report confirms, at its stated scope:

- the vendored `cadical-wasm@0.1.2` environment and all 61 AA plus 61 AB `n=10` branches completed offline;
- the unmodified `v1.0.2` `n=14` runner completed the 86 sigma-one regenerations, `B=96`, and all 286 labelled placements;
- the active `n=13` path consistently uses `B80..B83`, with the older WIP material historical and inactive;
- no statement-equivalence gap was identified in the count-preservation bridge under the explicit exact-triple-partition lemma.

The reviewer explicitly characterizes this as a replay and focused packaging/semantics cross-check, not a new independent audit of the entire proof. The full Euclidean-to-abstract encoding is not packaged as a single standalone Lean theorem.

## Manuscript-artifact boundary

The manuscript PDFs and source ZIPs in `v1.0.2` are byte-identical to their `v1.0.0` counterparts. Their embedded release text therefore still identifies the historical `v1.0.0` archive and checksum. The `v1.0.2` release notes, checksum manifest, and repository metadata identify the corrected canonical verification object. Updating the embedded manuscript text would require rebuilt manuscript assets in a future release.

The top-level README in the immutable `v1.0.2` tag snapshot likewise retains the historical `v1.0.0` release link and checksum because the repository metadata were synchronized after tag creation. The published tag is intentionally not retargeted. This is a tag-level metadata limitation, not a change to the verified archive or its checksum.

## Status boundary

This is a public computer-assisted preprint and reproducible exact verification package. It is not a proof-assistant formalization and has not undergone journal peer review. Independent mathematical review, literature and priority assessment, and clean-room reimplementation remain invited.
