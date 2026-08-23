# GitHub Release `v1.0.0` — final publication step

A private draft release has already been created automatically. Four source-derived assets have already been compiled and uploaded by GitHub Actions:

```text
erdos506_preprint.pdf
erdos506_computational_supplement.pdf
arxiv-source.zip
supplement-source.zip
```

Their current SHA-256 values are recorded in `ASSET_SHA256SUMS.txt` and in the release asset `GENERATED_ASSET_SHA256SUMS.txt`.

## One remaining upload

1. Open **Releases** in this repository.
2. Open the existing draft release `v1.0.0`.
3. Edit the draft.
4. Upload only:

```text
Erdos506.zip
```

Expected SHA-256:

```text
528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3
```

5. Confirm that all five publication assets are present.
6. Compare their hashes with `ASSET_SHA256SUMS.txt`.
7. Keep **Set as a pre-release** unchecked.
8. Publish the release.

## After publishing

Run the manual workflow **quick-verification** under the repository's Actions tab. It should end with:

```text
ERDOS506_REPOSITORY_QUICK=PASSED
```

The **full-verification-manual** workflow performs the full computational replay and may take several hours.

Do not make the repository public until the published release page opens correctly and the quick workflow succeeds.
