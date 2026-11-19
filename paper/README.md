# Paper files

Complete editable sources:

- `main.tex` with the manuscript sections in `main-sections/`;
- `supplement.tex`, the computational supplement and verification manual;
- `references.bib`, machine-readable bibliography metadata.

The following compiled files are distributed with GitHub Release [`v1.0.2`](https://github.com/DenisUkranian/erdos-506-circles/releases/tag/v1.0.2):

- `erdos506_preprint.pdf`;
- `erdos506_computational_supplement.pdf`;
- `arxiv-source.zip`;
- `supplement-source.zip`.

These four manuscript assets are byte-identical to their `v1.0.0` counterparts and therefore retain historical `v1.0.0` release text and checksum references internally. The corrected canonical verification object is `Erdos506.zip` from `v1.0.2`, SHA-256 `100316dcf37b1f424cf93df9e36ab539a3e97c3fdb05c87d641fd181bffd6298`.

Current release-asset checksums are recorded in `../ASSET_SHA256SUMS.txt`. Any update to the embedded manuscript release text requires rebuilding and publishing new manuscript assets in a future release.

## Reproducing the manuscript source archives

The published `arxiv-source.zip` was built from the manuscript text at [commit `ea1ba88`](https://github.com/DenisUkranian/erdos-506-circles/tree/ea1ba88c60387c3c61df681e9ebb7ef91be563e6). The editable manuscript on `main` includes one subsequent [clarification in the proof of the generalized-circle lemma](https://github.com/DenisUkranian/erdos-506-circles/commit/41a9e72dd3d9515ea7763abb84ed87e56ae4b1e6) that a line and a circle meet in at most two points. The supplement source is identical in both versions.

From the repository root, these commands reconstruct both released ZIPs and compare them with the published checksums.

```bash
set -eu
build_dir=$(mktemp -d)
git archive ea1ba88c60387c3c61df681e9ebb7ef91be563e6 paper | tar -x -C "$build_dir"
paper_dir="$build_dir/paper"
python3 tools/make_deterministic_zip.py --base "$paper_dir" --output "$build_dir/arxiv-source.zip" \
  "$paper_dir/main.tex" "$paper_dir/main-sections" "$paper_dir/references.bib"
python3 tools/make_deterministic_zip.py --base "$paper_dir" --output "$build_dir/supplement-source.zip" \
  "$paper_dir/supplement.tex"
awk '$2 == "arxiv-source.zip" || $2 == "supplement-source.zip"' ASSET_SHA256SUMS.txt > "$build_dir/source-sha256sums.txt"
(cd "$build_dir" && sha256sum -c source-sha256sums.txt)
```
