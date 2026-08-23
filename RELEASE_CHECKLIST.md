# GitHub Release `v1.0.0` — final publication step

A private draft release has already been created automatically. Four source-derived assets have been compiled, page-checked, made reproducible where applicable, and uploaded by GitHub Actions:

```text
erdos506_preprint.pdf
erdos506_computational_supplement.pdf
arxiv-source.zip
supplement-source.zip
```

Their final SHA-256 values are recorded in `ASSET_SHA256SUMS.txt`.

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

Do not publish the release manually yet.

## Automated verification and publication

After the upload:

1. Open **Actions**.
2. Select **finalize-release-v1**.
3. Select **Run workflow** on branch `main`.

The workflow will:

- download all five release assets;
- verify every SHA-256 against `ASSET_SHA256SUMS.txt`;
- unpack `Erdos506.zip`;
- run the canonical quick proof audit;
- require `ERDOS506_QUICK_AUDIT=PASSED`;
- publish release `v1.0.0` only after all checks pass;
- close issue #1 as completed.

After that workflow succeeds, change repository visibility from **Private** to **Public**.

The separate **full-verification-manual** workflow performs the full computational replay and may take several hours.
