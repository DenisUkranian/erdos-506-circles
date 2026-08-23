# Clean source-build audit

The publication sources were rebuilt in a fresh working directory on 23 August 2026.

## Manuscript

```text
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
Pages: 8
SHA-256: 0305cbb06065ae005e1cd7607f19904ac964f8f76fb19b7ae8f84af3c144a5a4
```

## Computational supplement

```text
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
Pages: 5
SHA-256: 5babe56e4cdfbb9de44b4fae1b57128966318fc081ffc92dae631f88abc96ad2
```

No undefined control sequence, LaTeX error, emergency stop or fatal error appeared in the final logs. The exact release-source and PDF checksums are recorded in `ASSET_SHA256SUMS.txt`.
