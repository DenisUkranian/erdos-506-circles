# Changelog

## 1.0.2 — reproducibility correction

- fixed the `n=14` all-286 runner invocation;
- vendored and checksummed `cadical-wasm@0.1.2` for offline `n=10` replay;
- vendored and checksummed SymPy 1.14.0 and mpmath 1.3.0;
- made `verify.py --full` run the complete `n=10` and extended `n=14` paths;
- restored executable modes required by nested runners;
- explicitly marked the stale `n=13` WIP snapshot as historical and inactive;
- regenerated affected manifests and added v1.0.2 structural checks.

No mathematical input or claimed value changed.

## 1.0.0 — initial public verification release

- compact self-contained verification archive;
- complete working exact package for `f(12)=51`;
- complete working exact packages for the `n=13` levels `B=80,81,82,83`;
- full replay command and retained clean-audit logs;
- manuscript, citation metadata and publication disclosures.
