# Erdős Problem 506 — minimum circles determined by planar points

[![status](https://img.shields.io/badge/status-public%20preprint-blue)](#status)
[![verification](https://img.shields.io/badge/verification-replayable-brightgreen)](#verification)
[![release](https://img.shields.io/badge/release-v1.0.0-blue)](https://github.com/DenisUkranian/erdos-506-circles/releases/tag/v1.0.0)

This repository accompanies the preprint **“The Minimum Number of Circles Determined by Planar Point Sets under the Elliott–Purdy–Smith Convention”** by **Denis Paliy** (Independent researcher, Kyiv, Ukraine).

## Result

For distinct planar points that are not all collinear and not all concyclic, counting only proper Euclidean circles containing at least three selected points, the computer-assisted verification establishes

- `f(8) = 17`;
- for every `n >= 9`, `f(n) = 1 + C(n-1,2) - floor((n-1)/2)`.

In particular, `f(12) = 51` and `f(13) = 61`.

## Published release

GitHub Release [`v1.0.0`](https://github.com/DenisUkranian/erdos-506-circles/releases/tag/v1.0.0) is published and contains:

- [`Erdos506.zip`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.0/Erdos506.zip) — canonical proof and verification archive;
- [`erdos506_preprint.pdf`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.0/erdos506_preprint.pdf) — main preprint;
- [`erdos506_computational_supplement.pdf`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.0/erdos506_computational_supplement.pdf) — computational supplement;
- [`arxiv-source.zip`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.0/arxiv-source.zip) — manuscript source prepared for arXiv;
- [`supplement-source.zip`](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.0/supplement-source.zip) — supplement source.

The exact release hashes are recorded in [`ASSET_SHA256SUMS.txt`](ASSET_SHA256SUMS.txt).

The complete editable sources are also committed:

- [LaTeX manuscript](paper/main.tex);
- [computational supplement](paper/supplement.tex);
- [bibliography metadata](paper/references.bib).

## Verification

The canonical proof object is `Erdos506.zip`, SHA-256:

```text
528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3
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

Expected markers:

```text
ERDOS506_QUICK_AUDIT=PASSED
ERDOS506_FULL_REPLAY=PASSED
```

The publication workflow hash-verified all five release assets and obtained `ERDOS506_QUICK_AUDIT=PASSED` before publishing `v1.0.0`. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md), [FINAL_RELEASE_AUDIT.md](FINAL_RELEASE_AUDIT.md), and [PUBLICATION_STATUS.md](PUBLICATION_STATUS.md).

## Repository contents

- `paper/` — complete manuscript and supplement sources;
- `verification/` — proof-bundle checksum, retained audit and instructions;
- `CITATION.cff`, `codemeta.json`, `.zenodo.json` — archival metadata;
- `AI_USAGE_DISCLOSURE.md` — disclosure and human-responsibility statement;
- `LICENSE` — MIT license for software;
- `LICENSE-DOCUMENTATION.md` — CC BY 4.0 for manuscript and original documentation.

## Status

Public preprint / computer-assisted proof. Independent verification is explicitly invited. The repository does not claim journal peer review until a journal version is accepted.
