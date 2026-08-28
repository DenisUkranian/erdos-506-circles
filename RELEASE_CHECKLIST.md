# GitHub Release `v1.0.2` — completed checklist

Release [`v1.0.2`](https://github.com/DenisUkranian/erdos-506-circles/releases/tag/v1.0.2) has been published successfully.

Completed:

- [x] deterministic corrected `Erdos506.zip` build;
- [x] executable modes preserved for all shell runners;
- [x] vendored `cadical-wasm@0.1.2`, SymPy 1.14.0, and mpmath 1.3.0 checked offline;
- [x] quick and v1.0.2 structural audits passed;
- [x] complete clean replay passed;
- [x] all 61 AA and 61 AB `n=10` branches passed;
- [x] complete `n=12` package passed;
- [x] active `n=13` packages for `B=80,81,82,83` passed;
- [x] extended `n=14` replay, including all 286 labelled placements, passed;
- [x] fail-closed damaged-archive tests passed;
- [x] nine release assets uploaded;
- [x] release published as public, non-draft, non-pre-release, and Latest;
- [x] tag `v1.0.2` verified at `0fecffaecd3a53999aaef1b8a23a4665088af938`;
- [x] every public GitHub API asset digest matched its frozen expected SHA-256;
- [x] exact frozen upload bytes passed fresh quick and structural audits.

Canonical archive SHA-256:

```text
100316dcf37b1f424cf93df9e36ab539a3e97c3fdb05c87d641fd181bffd6298
```

Verification boundary: direct post-publication browser download was blocked, so no independent consumer-side byte-download replay is claimed. The public API digest comparison and exact-byte local replays are reported separately in `FINAL_RELEASE_AUDIT.md`.

Historical `v1.0.0` remains unchanged. Use `v1.0.2` for current downloading, verification, and citation. Future substantive corrections require a new release version and checksums.
