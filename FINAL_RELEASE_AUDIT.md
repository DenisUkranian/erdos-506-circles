# Final pre-release audit

Performed on 23 August 2026 before creating GitHub Release `v1.0.0`.

## Publication files

- manuscript clean compile: passed, 8 pages;
- supplement clean compile: passed, 5 pages;
- arXiv source ZIP: valid;
- supplement source ZIP: valid;
- all five planned assets match `ASSET_SHA256SUMS.txt`.

## Canonical verification object

```text
528cabbc1e6cbd842ce34ab8c52ab34bd99ad1bf46dc015a45de1126466bd9f3  Erdos506.zip
```

Checks performed from a clean extraction:

```text
TOP_MANIFEST=PASSED
PACKAGE=base ZIP=OK
PACKAGE=n12 ZIP=OK
PACKAGE=B80 ZIP=OK
PACKAGE=B81 ZIP=OK
PACKAGE=B82 ZIP=OK
PACKAGE=B83 ZIP=OK
MANIFEST=base PASSED
MANIFEST=n12 PASSED
MANIFEST=B80 PASSED
MANIFEST=B81 PASSED
MANIFEST=B82 PASSED
MANIFEST=B83 PASSED
RETAINED_FINAL_AUDITS=PASSED
ERDOS506_VALUE_ARITHMETIC=PASSED
ERDOS506_QUICK_AUDIT=PASSED
```

The earlier retained full clean replay ended with `ERDOS506_FULL_REPLAY=PASSED`.

## Remaining action

Only the web-interface creation of GitHub Release `v1.0.0` and upload of the five checked binary assets remains. See `RELEASE_CHECKLIST.md` and issue #1.
