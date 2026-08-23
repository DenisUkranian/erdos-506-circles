# Erdős Problem 506 — minimum circles determined by planar points

[![status](https://img.shields.io/badge/status-preprint-blue)](#status)
[![verification](https://img.shields.io/badge/verification-replayable-brightgreen)](#verification)

This repository accompanies the preprint **“The Minimum Number of Circles Determined by Planar Point Sets under the Elliott–Purdy–Smith Convention”** by **Denis Paliy** (Independent researcher, Kyiv, Ukraine).

## Result

For distinct planar points that are not all collinear and not all concyclic, counting only proper Euclidean circles containing at least three selected points, the computer-assisted verification establishes

- `f(8) = 17`;
- for every `n >= 9`, `f(n) = 1 + C(n-1,2) - floor((n-1)/2)`.

In particular, `f(12) = 51` and `f(13) = 61`.

## Paper

- [Preprint PDF](https://github.com/DenisUkranian/erdos-506-circles/raw/assets/paper/erdos506_preprint.pdf)
- [Computational supplement PDF](https://github.com/DenisUkranian/erdos-506-circles/raw/assets/paper/erdos506_computational_supplement.pdf)
- [Complete LaTeX manuscript](paper/main.tex)
- [Complete LaTeX supplement](paper/supplement.tex)
- [arXiv source archive](https://github.com/DenisUkranian/erdos-506-circles/raw/assets/paper/arxiv-source.zip)

## Verification

The canonical proof object is `Erdos506.zip`, expected SHA-256:

```text
528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3
```

It will be attached to GitHub Release `v1.0.0`. After downloading it to `verification/Erdos506.zip`, run:

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

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the full protocol.

## Repository contents

- `paper/` — complete manuscript and supplement sources;
- branch `assets` — compiled PDFs and ready-to-upload source archives;
- `verification/` — archive checksum, retained audit and instructions;
- `CITATION.cff`, `codemeta.json`, `.zenodo.json` — archival metadata;
- `AI_USAGE_DISCLOSURE.md` — disclosure and human-responsibility statement;
- `LICENSE` — MIT license for software;
- `LICENSE-DOCUMENTATION.md` — CC BY 4.0 for manuscript and original documentation.

## Status

Preprint / computer-assisted proof. Independent verification is explicitly invited. The repository does not claim journal peer review until a journal version is accepted.
