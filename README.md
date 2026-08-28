# Erdős Problem 506 — minimum circles determined by planar points

[![status](https://img.shields.io/badge/status-public%20preprint-blue)](#status)
[![verification](https://img.shields.io/badge/verification-replayable-brightgreen)](#verification)
[![release](https://img.shields.io/badge/release-v1.0.2-blue)](https://github.com/DenisUkranian/erdos-506-circles/releases/tag/v1.0.2)

This repository accompanies the preprint **“The Minimum Number of Circles Determined by Planar Point Sets under the Elliott–Purdy–Smith Convention”** by **Denis Paliy** (Independent researcher, Kyiv, Ukraine).

## Result

For distinct planar points that are not all collinear and not all concyclic, counting only proper Euclidean circles containing at least three selected points, the computer-assisted verification establishes

- `f(8) = 17`;
- for every `n >= 9`, `f(n) = 1 + C(n-1,2) - floor((n-1)/2)`.

In particular, `f(12) = 51` and `f(13) = 61`.

## Current release

GitHub Release [`v1.0.2`](https://github.com/DenisUkranian/erdos-506-circles/releases/tag/v1.0.2) is public, is not a pre-release, and is the current Latest release. Tag `v1.0.2` resolves to commit `0fecffaecd3a53999aaef1b8a23a4665088af938`. The release contains:

- [`Erdos506.zip`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.2/Erdos506.zip) — canonical corrected proof and verification archive;
- [`Erdos506.zip.sha256`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.2/Erdos506.zip.sha256) — canonical archive checksum sidecar;
- [`erdos506_preprint.pdf`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.2/erdos506_preprint.pdf) — main preprint;
- [`erdos506_computational_supplement.pdf`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.2/erdos506_computational_supplement.pdf) — computational supplement;
- [`arxiv-source.zip`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.2/arxiv-source.zip) — manuscript source prepared for arXiv;
- [`supplement-source.zip`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.2/supplement-source.zip) — supplement source;
- [`Erdos506_AUDIT_v1.0.2.zip`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.2/Erdos506_AUDIT_v1.0.2.zip) and its `.sha256` sidecar — publication-gate logs;
- [`ASSET_SHA256SUMS.txt`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.2/ASSET_SHA256SUMS.txt) — checksums for the other eight uploaded assets.

The released checksum manifest is also committed as [`ASSET_SHA256SUMS.txt`](ASSET_SHA256SUMS.txt). Release `v1.0.0` remains available as a historical record, but `v1.0.2` should be used for downloading, verification, and citation.

The manuscript PDFs and source archives are byte-identical to those in `v1.0.0`; the corrected object in `v1.0.2` is the verification archive. Consequently, historical `v1.0.0` references inside the unchanged manuscript files refer to the first public release.

The complete editable sources are also committed:

- [LaTeX manuscript](paper/main.tex);
- [computational supplement](paper/supplement.tex);
- [bibliography metadata](paper/references.bib).

## Verification

The canonical proof object is `Erdos506.zip`, SHA-256:

```text
100316dcf37b1f424cf93df9e36ab539a3e97c3fdb05c87d641fd181bffd6298
```

Download it to `verification/Erdos506.zip`, then run:

```bash
bash verify_repository.sh
```

For the complete computational replay:

```bash
rm -rf /tmp/erdos506-full
mkdir -p /tmp/erdos506-full
unzip -q verification/Erdos506.zip -d /tmp/erdos506-full
cd /tmp/erdos506-full/Erdos506
python3 verify.py --full
```

Expected markers include:

```text
ERDOS506_QUICK_AUDIT=PASSED
ERDOS506_V102_AUDIT=PASSED
ERDOS506_FULL_REPLAY=PASSED
```

Before publication, the frozen archive passed deterministic builds, the quick and v1.0.2 structural audits, a complete clean replay, all 61 AA and 61 AB `n=10` branches, the complete `n=12` package, all active `n=13` packages for `B=80,81,82,83`, all 286 labelled `n=14` placements, and fail-closed mutation tests. After publication, each of the nine public GitHub API asset digests matched its frozen expected SHA-256; the exact frozen upload bytes also passed fresh quick and structural audits. A direct post-publication browser download was unavailable in the verification environment, so no independent consumer-side byte-download replay is claimed.

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md), [FINAL_RELEASE_AUDIT.md](FINAL_RELEASE_AUDIT.md), and [PUBLICATION_STATUS.md](PUBLICATION_STATUS.md).

## Repository contents

- `paper/` — complete manuscript and supplement sources;
- `verification/` — proof-bundle checksum and verification instructions;
- `CITATION.cff`, `codemeta.json`, `.zenodo.json` — archival metadata;
- `AI_USAGE_DISCLOSURE.md` — disclosure and human-responsibility statement;
- `LICENSE` — MIT license for software;
- `LICENSE-DOCUMENTATION.md` — CC BY 4.0 for manuscript and original documentation.

## Status

Public preprint / computer-assisted proof. Independent verification is explicitly invited. The repository does not claim journal peer review, formal proof-assistant verification, or adjudicated priority.
