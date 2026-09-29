# AKR Canonical Semantic Model v0.1 — Draft

Status: architecture proposal  
Authority: non-canonical draft  
Branch: architecture-synthesis-v0.2

## 1. Design question

What is the smallest reusable semantic unit that AKR should treat as canonical?

The v0.1 taxonomy (`algorithm`, `policy`, `heuristic`) is not assumed to be correct. The semantic model must support those concepts without requiring them to be primitive types.

## 2. Proposed primitive: Reasoning Asset

A **Reasoning Asset** is a versioned semantic object that contributes to reasoning, decision-making, context construction, or validation.

A Reasoning Asset is identified by stable ID and contains one or more semantic roles.

### Required fields

- `id`
- `version`
- `status`
- `title`
- `purpose`
- `semantic_roles`
- `applicability`
- `inputs`
- `outputs`
- `constraints`
- `stop_conditions`
- `provenance`

### Optional fields

- `procedure`
- `invariants`
- `heuristics`
- `failure_modes`
- `examples`
- `tests`
- `notes`

## 3. Semantic roles

A single asset may carry multiple roles.

Candidate roles:

- `procedure` — ordered transformation or decision process
- `invariant` — condition that must remain true
- `heuristic` — defeasible guidance
- `constraint` — prohibited or bounded behavior
- `operator` — reusable reasoning transformation
- `classifier` — assigns states/classes
- `evaluator` — judges conformance or utility
- `router` — maps task/problem state to assets or execution paths
- `stop_rule` — determines when further work should terminate
- `recovery_rule` — specifies behavior after failure or ambiguity
- `test_oracle` — defines expected behavior in representative cases

These are semantic roles, not necessarily top-level folders.

## 4. Why a generic asset is preferred

A generic Reasoning Asset avoids several early lock-ins:

1. A "policy" may contain both an invariant and a procedure.
2. A "heuristic" may later become a validated decision rule.
3. An "algorithm" may include constraints, examples, and stop rules that must compose independently.
4. Runtime selection should depend on applicability and relations, not folder names.

## 5. Applicability model

Applicability should be explicit rather than inferred only from natural-language triggers.

Candidate structure:

```yaml
applicability:
  when:
    all:
      - task.domain in [security, privacy]
      - task.intent == evaluate_information_suitability
    any:
      - data.sensitivity >= S2
      - provider_handles_identity_data == true
  unless:
    - task.only_requires_public_information == true
```

Natural-language trigger text may remain for discovery, but executable applicability should use structured predicates where practical.

## 6. Relation model

Relations are first-class graph edges.

### Dependency / ordering

- `requires`
- `optional_with`
- `must_precede`
- `must_follow`

### Conflict / exclusion

- `conflicts_with`
- `mutually_exclusive_with`
- `overrides`

### Lifecycle / lineage

- `supersedes`
- `derived_from`
- `forked_from`

### Governance / validation

- `governed_by`
- `tested_by`
- `validated_by`

### Applicability / composition

- `complements`
- `specializes`
- `generalizes`
- `applies_to`

Each edge should have:
- source
- target
- relation_type
- optional condition
- optional rationale
- optional priority

## 7. State separation

Epistemic state is not a relation type. It is metadata attached to claims, observations, or outputs.

Candidate states:

- OBSERVED
- VERIFIED
- INFERRED
- HYPOTHESIS
- SCENARIO
- UNKNOWN

Modal state is separate:

- OPTION
- RECOMMENDATION
- REQUEST
- REQUIREMENT
- COMMAND

This separation prevents one dimension from being overloaded by the other.

## 8. Canonical content vs compiled runtime

Canonical source should contain human-auditable semantic definitions.

Compiled runtime may normalize the source into:

- SQLite rows
- FTS index
- dependency graph
- applicability predicates
- cached summaries
- vector representations

Compiled forms are rebuildable and non-authoritative.

## 9. Candidate canonical file structure

The file system layout should be treated as packaging, not ontology.

Example:

```text
assets/
  RA-SEC-001/
    asset.yaml
    body.md
    tests.yaml
```

Where `asset.yaml` carries machine-critical semantics and `body.md` carries rationale and explanatory detail.

This is only a packaging candidate, not yet a migration decision.

## 10. Open questions

1. Should one Reasoning Asset be allowed to contain multiple procedures, or should each procedure be a separate asset?
2. Should claims inside an asset have stable IDs?
3. Which applicability predicates must be executable versus descriptive?
4. Should relation rationale remain canonical?
5. How should conflict resolution be represented without embedding a global priority hierarchy too early?
6. Should tests be first-class assets or attached artifacts?
7. How should model-specific execution hints be stored without contaminating model-independent canonical meaning?
