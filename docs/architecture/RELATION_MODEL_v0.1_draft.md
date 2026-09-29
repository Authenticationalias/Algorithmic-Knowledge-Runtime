# AKR Relation Model v0.1 — Draft

Status: non-canonical design artifact

## Purpose

Represent composition and lifecycle explicitly enough that an AI does not need to infer all relationships from prose.

## Edge schema

```yaml
source: RA-SEC-001
target: RA-RES-001
relation: requires
condition: null
priority: null
rationale: "Blind-spot expansion is required before final suitability judgment when premature closure is material."
```

## Edge classes

### Composition edges

`requires`  
Target must be resolved before source can execute correctly.

`optional_with`  
Target may improve execution but is not mandatory.

`complements`  
Assets cover different aspects and may be combined.

### Ordering edges

`must_precede`  
Source must execute before target.

`must_follow`  
Source must execute after target.

Ordering is distinct from dependency. An asset can depend on another without requiring that its full procedure run first.

### Conflict edges

`conflicts_with`  
Both assets may apply but cannot be executed unchanged together.

`mutually_exclusive_with`  
Only one may be selected for a given execution.

`overrides`  
Source intentionally supersedes target behavior under an explicit condition.

### Lineage edges

`supersedes`  
Source replaces target as the preferred current definition.

`derived_from`  
Source was generalized or transformed from target but does not replace it.

`forked_from`  
Source intentionally diverges while retaining lineage.

### Governance edges

`governed_by`  
Source execution is constrained by target.

`tested_by`  
Target contains a test or oracle for source.

`validated_by`  
Target records validation evidence for source.

### Semantic specialization

`specializes`  
Source narrows target to a domain or condition.

`generalizes`  
Source abstracts multiple narrower assets.

## Conflict resolution

The graph should expose conflict; it should not silently resolve every conflict globally.

Resolution may depend on:
- task context;
- authority;
- version;
- actor;
- risk level;
- explicit override relation;
- governance policy.

The runtime must be allowed to return `UNRESOLVED_CONFLICT`.

## Design warning

Do not encode every natural-language relation as an edge. Edges are justified when they change retrieval, ordering, validation, lifecycle, or conflict behavior.
