# Algorithmic Knowledge Runtime (AKR)

AKR is a machine-readable, human-auditable repository for reusable AI reasoning assets.

It externalizes:
- algorithms
- policies
- heuristics
- routing and retrieval rules
- schemas
- test vectors
- derived runtime specifications

## Design principles

1. **Canonical source is plain text.** Markdown + YAML/JSON are the source of truth.
2. **SQLite is derived.** Runtime databases and search indexes are rebuildable artifacts, not authority.
3. **Evidence modality is preserved.** Observed facts, verified claims, inferences, hypotheses, unknowns, options, and requests must not collapse into each other.
4. **Broad internal exploration, narrow external action.** Blind-spot discovery may be expansive; outward queries and recommendations are filtered by decision relevance.
5. **Actor-relative information value.** Information value depends on the actor, decision, authority, incentives, and cost.
6. **Stop conditions are explicit.** More detail is not automatically more useful.
7. **Fresh-session reconstructability matters.** An AI should be able to recover an algorithm's intended meaning from the repository without relying on chat history.

## Repository layout

```text
algorithms/   reusable procedures
policies/     invariant rules and constraints
heuristics/   defeasible exploration rules
registry/     machine-readable inventory
schemas/      validation schemas
context/      routing/retrieval/compression rules
tests/        reconstruction and behavior test vectors
runtime/      derived-runtime specification (SQLite, FTS, indexes)
```

## Authority boundary

AKR is separate from architecture-authority repositories such as AASA. Architecture systems may reference or consume AKR, but AKR does not inherit their canonical authority unless explicitly declared.

## Runtime model

```text
Canonical Markdown/YAML
        ↓ validate/build
Derived SQLite/FTS runtime
        ↓
Algorithm Router
        ↓
Dependency Resolver
        ↓
Context Composer
        ↓
LLM execution
        ↓
Validation
```

## Current status

Foundation v0.1. The initial registry contains:
- Secure Information Handling Suitability
- Blind-Spot Expansion
- Actor-Specific Information Value

License: not yet selected.
