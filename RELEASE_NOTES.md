# Erdős Problem 506 — proof and verification archive v1.0.0

This release accompanies the preprint **The Minimum Number of Circles Determined by Planar Point Sets under the Elliott–Purdy–Smith Convention** by Denis Paliy.

## Result

Under the stated nondegeneracy convention, the release verifies

- `f(8)=17`;
- `f(n)=1+C(n-1,2)-floor((n-1)/2)` for every `n>=9`;
- in particular, `f(12)=51` and `f(13)=61`.

## Assets

- `Erdos506.zip` — canonical self-contained proof and replay archive;
- `erdos506_preprint.pdf` — manuscript;
- `erdos506_computational_supplement.pdf` — verification manual and finite ledgers;
- `arxiv-source.zip` — arXiv-ready manuscript source;
- `supplement-source.zip` — supplement source.

## Canonical proof checksum

```text
528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3  Erdos506.zip
```

All release-asset checksums are recorded in `ASSET_SHA256SUMS.txt` on the tagged commit.

## Reproduction

Download `Erdos506.zip` to `verification/Erdos506.zip`, check the checksum and run:

```bash
bash verify_repository.sh
```

For the complete replay, extract the archive and run:

```bash
python3 verify.py --full
```

Expected final markers:

```text
ERDOS506_QUICK_AUDIT=PASSED
ERDOS506_FULL_REPLAY=PASSED
```

This is a preprint/computer-assisted proof release. Independent mathematical review and clean-room reimplementation are explicitly invited.
