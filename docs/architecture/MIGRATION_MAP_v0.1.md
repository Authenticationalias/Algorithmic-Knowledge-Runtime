# AKR v0.1 → Architecture Synthesis Migration Map

Status: planning artifact only  
Rule: no canonical migration is authorized by this document.

## Purpose

Preserve useful v0.1 work while preventing its initial folder structure and terminology from becoming accidental architecture.

## Keep as evidence

The following v0.1 assets remain useful regardless of the final ontology:

- Secure Information Handling Suitability content
- Blind-Spot Expansion content
- Actor-Specific Information Value content
- Evidence State Separation
- Modality Preservation
- test vectors
- routing examples
- compression invariants
- SQLite/FTS prototype
- fresh-session reconstruction concept

## Re-evaluate before promoting to architecture

### 1. Asset taxonomy
Current:
- algorithm
- policy
- heuristic

Question:
Could these all be specialized views over a generic Reasoning Asset with semantic-role metadata?

### 2. Registry
Current:
single YAML inventory.

Question:
Should registry remain canonical metadata, or be generated from per-asset canonical metadata into a semantic graph?

### 3. Dependencies
Current:
`requires`.

Question:
Need richer edge types:
- requires
- conflicts_with
- must_precede
- supersedes
- tested_by
- governed_by
- applicable_when

### 4. Context rules
Current:
separate routing/retrieval/compression YAML files.

Question:
Which rules are architecture-level invariants, which are runtime policy, and which are heuristics?

### 5. SQLite
Current:
derived relational runtime + FTS.

Question:
Treat SQLite as one compiled target, not necessarily the runtime architecture itself.

### 6. AGENTS.md
Current:
bootstrap contract for AI consumers.

Question:
Keep a bootstrap entrypoint, but derive as much as possible from canonical governance rules to prevent duplication.

## Proposed migration sequence

1. Freeze v0.1 as baseline.
2. Complete canonical semantic-model design.
3. Map every v0.1 object into the new semantic model.
4. Identify information loss or forced classifications.
5. Build v0.2 compiler/runtime in parallel.
6. Run fresh-session reconstruction against both versions.
7. Migrate only after behavioral equivalence or intentional improvement is demonstrated.

## No-change principle

Do not rename folders, rewrite IDs, or migrate canonical files merely to match this draft. The architecture synthesis branch is intentionally non-destructive.
