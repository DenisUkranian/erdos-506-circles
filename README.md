# Erdős #634 — exact triangle-tiling research

Research directed by **Denis Paliy**, with substantial GPT/Codex assistance.

This is a reproducible research collection, **not a solution of the full Erdős problem**. Reflections and T-junctions are allowed. The primary audited result is:

> A triangle with sides **(125,125,142)** cannot be tiled by congruent triangles with sides **(10,21,25)**. The area ratio is 71.

This does not classify all 71-piece tilings, all parameters of the rational family, or all admissible tile counts.

## Publication location

This collection is isolated on branch `erdos-634-research` of the owner's existing public repository. The `main` branch and releases devoted to Erdős #506 are not modified. The branch name, rather than the repository's legacy name, identifies this project.

## Start here

- [Self-contained N71 proof](docs/N71_proof.md)
- [Shifted-endpoint strip obstruction](docs/shifted_strip.md)
- [Claim ledger and limits](STATUS.md)
- [Literature and review questions](docs/literature.md)
- [AI assistance](AI_DISCLOSURE.md)

The original N71 certificate has 7,618 states. A shifted-endpoint strip obstruction reduces it to 7,614. Both full trees were accepted by exact rational verification. The four-state reduction is modest and is not advertised as a major speedup.

## Reproduction

The checkers reconstruct all 12 placements at each selected strict convex corner, check containment and intersections with rational arithmetic, and reject missing children. No edge-to-edge restriction, arbitrary interior-direction bound, floating-point tolerance or timeout is treated as a proof of impossibility.

The paper argument that every possible tiling has the fixed three-apex root up to reflection is essential. Running a checker alone does not check that argument.

## Historical collection and scope

The publication separates current proofs from inherited notes and intermediate claims. The full manuscript of a separately reported uniform `u=2` proof was not recovered; its existence is not substituted for a proof or claimed as a fresh verification. The separate Shallit #9 work and private correspondence are excluded.

## Novelty and external review

Michael Beeson already stated broader non-prime-tiling results for this angle family, including Theorem 15 of arXiv:1206.2229v3 (2019), and further prime-count results in arXiv:2607.19572 and arXiv:2607.23453 (2026). Therefore N71 must **not** be presented as the first announcement of this non-tiling conclusion. The contribution offered for review is a self-contained exact geometric certificate and strip arguments independent of the older divisibility route.

Two explicit issues in the older printed arithmetic argument are recorded as technical questions, not as counterexamples to the main non-tiling conclusions. Literary priority, correctness of every inherited proof, and journal acceptance have not been established by this publication.

“Independent checker” means implementation independence from the generator. It does not mean independent human peer review, human-only authorship, or Lean formalization. No prize application or full-resolution claim accompanies this collection.
