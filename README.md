# Erdős Problem 506 — minimum circles determined by planar points

[![status](https://img.shields.io/badge/status-preprint-blue)](#status)
[![verification](https://img.shields.io/badge/verification-replayable-brightgreen)](#verification)

This repository accompanies the preprint
**“The Minimum Number of Circles Determined by Planar Point Sets under the Elliott–Purdy–Smith Convention”** by **Denis Paliy** (Independent researcher, Kyiv, Ukraine).

## Result

For distinct planar points that are not all collinear and not all concyclic, counting only proper Euclidean circles containing at least three selected points, the computer-assisted verification establishes

- `f(8) = 17`;
- for every `n >= 9`,
  `f(n) = 1 + C(n-1,2) - floor((n-1)/2)`.

In particular, the formerly unresolved finite cases are

- `f(12) = 51`;
- `f(13) = 61`.

## Paper

- [Preprint PDF (release asset)](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.0/erdos506_preprint.pdf)
- [Computational supplement PDF (release asset)](https://github.com/DenisUkranian/erdos-506-circles/releases/download/v1.0.0/erdos506_computational_supplement.pdf)
- [LaTeX source](paper/main.tex)
- [LaTeX bibliography](paper/references.bib)

## Verification

The canonical verification object is the GitHub Release asset `Erdos506.zip` in release `v1.0.0`.

Expected SHA-256:

```text
528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3
```

After downloading the release asset, place it at `verification/Erdos506.zip` and run:

```bash
cd verification
sha256sum -c Erdos506.zip.sha256
unzip Erdos506.zip
cd Erdos506
python3 verify.py          # quick integrity and retained-certificate audit
python3 verify.py --full   # compile and rerun all proof packages
```

Requirements: Linux/Unix shell, Python 3.10+, GNU C++20, Bash, `sha256sum`, and ZIP tools. No network is required after downloading the release asset.

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the complete protocol.

## Repository contents

- `paper/` — manuscript, supplement, LaTeX and arXiv sources;
- `verification/` — proof-bundle checksum, retained public replay log and release instructions;
- `CITATION.cff`, `codemeta.json`, `.zenodo.json` — archival metadata;
- `AI_USAGE_DISCLOSURE.md` — disclosure and human-responsibility statement;
- `LICENSE` — MIT license for software;
- `LICENSE-DOCUMENTATION.md` — CC BY 4.0 for manuscript and original documentation.

## Citation

See [`CITATION.cff`](CITATION.cff). A permanent DOI and arXiv identifier will be added after the first archival deposits.

## Status

Preprint / computer-assisted proof. Independent verification is explicitly invited. This repository does not claim journal peer review until a journal version is accepted.
