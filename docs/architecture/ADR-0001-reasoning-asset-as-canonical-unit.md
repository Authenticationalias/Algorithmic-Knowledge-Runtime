# ADR-0001: Use a generic Reasoning Asset as the canonical semantic unit

Status: Proposed  
Date: 2026-09-29

## Context

AKR v0.1 began with top-level categories:

- algorithm
- policy
- heuristic

These categories emerged directly from the initial conversation and are useful for capture, but they may encode the wording of the originating discussion rather than a durable system ontology.

A future AKR must support:
- procedures;
- invariants;
- heuristics;
- constraints;
- routers;
- stop rules;
- evaluators;
- tests;
- dependencies and conflicts.

## Decision

Introduce **Reasoning Asset** as the proposed canonical semantic unit.

`algorithm`, `policy`, and `heuristic` become possible semantic-role labels or views rather than mandatory primitive types.

## Consequences

### Positive

- Reduces prompt-shaped ontology risk.
- Supports multi-role assets.
- Allows future specialization without ID migration.
- Makes runtime composition depend on semantics and graph relations rather than folders.

### Negative

- Requires stronger schema design.
- May create overly broad assets if granularity rules are weak.
- Existing v0.1 IDs and folders need a later migration map.

## Rejected alternatives

### Keep algorithm/policy/heuristic as primitives
Rejected provisionally because the categories overlap and may not remain stable.

### Make every rule a graph node
Rejected provisionally because it may over-fragment authoring and increase graph-management cost.

### Use only free-form Markdown
Rejected because exact applicability, dependencies, and validation would remain ambiguous.

## Follow-up questions

- Define asset granularity.
- Define executable applicability syntax.
- Define relation edge schema.
- Test whether v0.1 assets map cleanly without semantic loss.
