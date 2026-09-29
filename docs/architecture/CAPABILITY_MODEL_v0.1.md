# AKR Capability Model v0.1

Status: non-canonical design artifact

This document describes what the system must be able to do, independent of implementation technology.

## Capability chain

```text
Capture
  ↓
Normalize
  ↓
Model
  ↓
Resolve
  ↓
Compose
  ↓
Execute
  ↓
Validate
  ↓
Govern
```

The chain is not strictly linear. Validation can feed Governance; Governance can invalidate compiled runtime state; Resolve can request additional Normalize/Model work when a candidate asset is incomplete.

## C1 Capture

### Goal
Prevent useful reasoning from being lost before its final abstraction is known.

### Required behavior
- accept candidate knowledge without forcing permanent classification;
- preserve provenance;
- distinguish raw observation from generalized rule;
- allow later promotion or rejection.

### Failure to avoid
Prompt-shaped ontology.

## C2 Normalize

### Goal
Separate different semantic roles before they are compressed together.

### Candidate roles
- observation
- invariant
- rule
- procedure
- heuristic
- constraint
- precondition
- stop condition
- failure mode
- example
- test
- provenance
- unresolved question

The final ontology is not yet fixed.

## C3 Model

### Goal
Make reasoning assets structurally composable.

### Required relations
- requires
- conflicts_with
- supersedes
- applicable_when
- must_precede
- may_follow
- derived_from
- tested_by
- governed_by

## C4 Resolve

### Goal
Choose the smallest sufficient reasoning set for a task.

### Required behavior
- task-to-asset candidate mapping;
- recursive dependency resolution;
- conflict detection;
- context-budget awareness;
- termination when marginal value is low.

## C5 Compose

### Goal
Create a model-consumable context package without semantic loss.

### Must preserve
- evidence state
- modality
- actor
- condition
- scope
- temporal qualifier
- exceptions
- stop conditions

## C6 Execute

### Goal
Apply selected reasoning assets to the task.

### Required outputs
- task answer or artifact;
- asset IDs actually used;
- unresolved critical unknowns;
- validation-relevant execution metadata.

No requirement is made to persist private chain-of-thought.

## C7 Validate

### Goal
Detect semantic drift and incorrect application.

### Validation types
- schema validation
- dependency validation
- reconstruction tests
- behavioral test vectors
- adversarial cases
- regression tests
- compression fidelity tests

## C8 Govern

### Goal
Prevent silent semantic mutation.

### Lifecycle
- candidate
- draft
- experimental
- validated
- deprecated
- superseded
- rejected

### Governance questions
- Who or what may promote an asset?
- What evidence is required?
- When does a change require a new major version?
- How are conflicts and forks represented?
