# GitHub Release `v1.0.0` — final manual step

The source repository is prepared. GitHub Release assets must be uploaded through the GitHub web interface because the connected automation does not expose release-asset upload.

## Create the release

1. Open this repository on GitHub.
2. Select **Releases** → **Draft a new release**.
3. Choose **Create new tag** and enter `v1.0.0` targeting `main`.
4. Release title: `Erdős Problem 506 — proof and verification archive v1.0.0`.
5. Paste the contents of `RELEASE_NOTES.md` into the description.
6. Upload exactly these five files:

```text
Erdos506.zip
erdos506_preprint.pdf
erdos506_computational_supplement.pdf
arxiv-source.zip
supplement-source.zip
```

7. Compare every uploaded file against `ASSET_SHA256SUMS.txt`.
8. Keep **Set as a pre-release** unchecked.
9. Publish the release.

## After publishing

Run the manual workflow **quick-verification** under the repository's Actions tab. It should end with:

```text
ERDOS506_REPOSITORY_QUICK=PASSED
```

The **full-verification-manual** workflow performs the computational replay and may take several hours.

Do not make the repository public until the release page opens correctly and the quick workflow succeeds.
